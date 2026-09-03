"""
SkillProof - POST /api/analyze
Evidence -> Gemini -> Section 8 JSON contract (Claim <-> Evidence analysis).

Owned by Member 1 (backend) + Member 3 (Gemini prompt/schema).
The API key is read from the GEMINI_API_KEY env var ONLY. Never hardcode it.

Run:
    pip install -r requirements.txt
    export GEMINI_API_KEY=...          # Windows: set GEMINI_API_KEY=...
    python app.py                      # serves on http://localhost:5000
    python app.py --selftest           # runs logic checks, no API key needed
"""

import base64
import json
import os

from database import save_project_analysis, get_project_from_db
from qr_generator import create_qr_code

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # frontend (Stitch) is a different origin; without this the browser blocks calls

# Use whatever Gemini model the hackathon provides; override with GEMINI_MODEL.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# The four support levels from Section 9 - enforced by the schema so Gemini can't drift.
SUPPORT = ["STRONG", "MODERATE", "WEAK", "UNSUPPORTED"]

# Section 8 contract as a Gemini response schema. This is what makes the output reliable:
# the model is forced into this exact shape with these exact enum values.
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "required": ["project", "technologies", "claims", "skills", "viva_questions", "portfolio"],
    "properties": {
        "project": {
            "type": "OBJECT",
            "required": ["title", "problem", "solution", "project_story"],
            "properties": {
                "title": {"type": "STRING"},
                "problem": {"type": "STRING"},
                "solution": {"type": "STRING"},
                "project_story": {"type": "STRING"},
            },
        },
        "technologies": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": ["name", "evidence", "strength"],
                "properties": {
                    "name": {"type": "STRING"},
                    "evidence": {"type": "STRING"},
                    "strength": {"type": "STRING", "enum": SUPPORT},
                },
            },
        },
        "claims": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": ["claim", "support", "supporting_evidence", "missing_evidence", "reason"],
                "properties": {
                    "claim": {"type": "STRING"},
                    "support": {"type": "STRING", "enum": SUPPORT},
                    "supporting_evidence": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "missing_evidence": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "reason": {"type": "STRING"},
                },
            },
        },
        "skills": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": ["skill", "strength", "evidence"],
                "properties": {
                    "skill": {"type": "STRING"},
                    "strength": {"type": "STRING", "enum": SUPPORT},
                    "evidence": {"type": "STRING"},
                },
            },
        },
        "viva_questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": ["question", "topic", "reason"],
                "properties": {
                    "question": {"type": "STRING"},
                    "topic": {"type": "STRING"},
                    "reason": {"type": "STRING"},
                },
            },
        },
        "portfolio": {
            "type": "OBJECT",
            "required": ["summary", "contribution", "technologies", "evidence_highlights"],
            "properties": {
                "summary": {"type": "STRING"},
                "contribution": {"type": "STRING"},
                "technologies": {"type": "ARRAY", "items": {"type": "STRING"}},
                "evidence_highlights": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
        },
    },
}

REQUIRED_FIELDS = ["title", "problem", "solution", "contribution"]


def validate(payload):
    """Return (ok, message). Evidence must exist or the whole product is meaningless."""
    if not isinstance(payload, dict):
        return False, "Body must be a JSON object."
    missing = [f for f in REQUIRED_FIELDS if not str(payload.get(f, "")).strip()]
    if missing:
        return False, f"Missing required field(s): {', '.join(missing)}"
    has_code = bool(str(payload.get("code", "")).strip())
    has_images = bool(payload.get("screenshots"))
    if not has_code and not has_images:
        return False, "Provide evidence: 'code' (text) and/or 'screenshots' (base64 images)."
    return True, ""


def build_prompt(payload):
    """The reasoning contract. Structure is handled by RESPONSE_SCHEMA; this enforces honesty."""
    claims = payload.get("claims") or []
    if claims:
        claims_block = "Claims to verify:\n" + "\n".join(
            f"{i}. {c}" for i, c in enumerate(claims, 1)
        )
    else:
        claims_block = (
            "No explicit claims were given. Extract the student's implicit claims from their "
            "stated contribution and solution, then verify each one against the evidence."
        )
    screenshot_note = (
        "Screenshot(s) are attached as images - use them as visual evidence.\n"
        if payload.get("screenshots")
        else ""
    )
    return f"""You are an expert technical project evaluator for SkillProof. Compare what the student CLAIMS they built against the EVIDENCE they submitted, and judge how strongly the evidence supports each claim, technology, and skill. Be strict and honest.

NON-NEGOTIABLE RULES:
- Base EVERY finding ONLY on the evidence below. Never assume, extrapolate, or invent files, features, or facts.
- If evidence for a claim is absent, you MUST mark it WEAK or UNSUPPORTED and fill missing_evidence. Do not be generous: a confident claim with no code behind it is UNSUPPORTED.
- List a technology or skill only if a file, import, config, endpoint, or code line shows it.
- Every viva question MUST reference something concrete in THIS student's evidence (a specific file, function, table, endpoint, or decision). No generic textbook questions.
- Support/strength = STRONG (evidence directly supports), MODERATE (supported but incomplete), WEAK (some related evidence, insufficient), UNSUPPORTED (no meaningful evidence).

STUDENT SUBMISSION
Project title: {payload.get('title')}
Problem statement: {payload.get('problem')}
Solution summary: {payload.get('solution')}
Stated personal contribution: {payload.get('contribution')}
{claims_block}

CODE / README / TECHNICAL EVIDENCE:
{payload.get('code', '(none provided)')}

{screenshot_note}Analyze now and return the structured JSON."""


def build_contents(payload):
    """Text prompt plus any screenshots as image parts."""
    from google.genai import types

    parts = [build_prompt(payload)]
    for shot in payload.get("screenshots", []) or []:
        # Accept {"mime_type": "image/png", "data": "<base64>"} or a raw base64 string.
        if isinstance(shot, dict):
            data, mime = shot.get("data", ""), shot.get("mime_type", "image/png")
        else:
            data, mime = shot, "image/png"
        try:
            parts.append(types.Part.from_bytes(data=base64.b64decode(data), mime_type=mime))
        except Exception:
            continue  # skip a bad image rather than failing the whole analysis
    return parts


def get_client():
    """Lazy so the module imports (and --selftest runs) without a key set."""
    from google import genai

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=key)



# --------------------------------------------------
# SAVE PROJECT + GENERATE QR
# --------------------------------------------------

@app.route("/api/save-project", methods=["POST"])
def save_project():
    analysis = request.get_json(silent=True)

    if not analysis:
        return jsonify({
            "success": False,
            "error": "No analysis data provided"
        }), 400

    try:
        project_id = save_project_analysis(analysis)
        qr_path, public_url = create_qr_code(project_id)

        return jsonify({
            "success": True,
            "project_id": project_id,
            "public_url": public_url,
            "qr_url": f"/{qr_path}"
        })

    except Exception as e:
        print("ERROR:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# --------------------------------------------------
# PUBLIC SKILLPROOF PORTFOLIO
# --------------------------------------------------

@app.route("/p/<project_id>")
def public_portfolio(project_id):
    project = get_project_from_db(project_id)

    if not project:
        return """
        <h1>Project Not Found</h1>
        <p>The requested SkillProof project does not exist.</p>
        """, 404

    analysis = project.get("analysis", {})

    return render_template(
        "public_portfolio.html",
        project=project,
        analysis=analysis,
        project_id=project_id
    )

@app.route("/", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "skillproof", "model": MODEL})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(silent=True)
    ok, msg = validate(payload)
    if not ok:
        return jsonify({"error": msg}), 400

    from google.genai import types

    try:
        client = get_client()
        response = client.models.generate_content(
            model=MODEL,
            contents=build_contents(payload),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                temperature=0.2,  # low = less likely to invent supporting evidence
            ),
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Gemini request failed: {e}"}), 502

    try:
        raw_text = getattr(response, "text", "") or ""
        return jsonify(json.loads(raw_text)), 200
    except Exception:
        return jsonify({"error": "Model did not return valid JSON.", "raw": str(getattr(response, "text", ""))}), 502


def _selftest():
    """Smallest checks that fail if the core logic breaks. No API key, no network."""
    # Enum + schema shape
    assert SUPPORT == ["STRONG", "MODERATE", "WEAK", "UNSUPPORTED"]
    for key in ["project", "technologies", "claims", "skills", "viva_questions", "portfolio"]:
        assert key in RESPONSE_SCHEMA["properties"], key
    assert RESPONSE_SCHEMA["properties"]["claims"]["items"]["properties"]["support"]["enum"] == SUPPORT

    # Validation: missing required field -> rejected
    ok, _ = validate({"problem": "p", "solution": "s", "contribution": "c", "code": "x"})
    assert ok is False, "missing title should fail"
    # Validation: no evidence at all -> rejected
    ok, _ = validate({"title": "t", "problem": "p", "solution": "s", "contribution": "c"})
    assert ok is False, "no code/screenshots should fail"
    # Validation: complete -> accepted
    ok, _ = validate({"title": "t", "problem": "p", "solution": "s", "contribution": "c", "code": "print()"})
    assert ok is True, "complete payload should pass"

    # Prompt actually embeds the evidence and the strictness rule
    prompt = build_prompt({"title": "Attendance", "problem": "p", "solution": "s",
                           "contribution": "I built the ML model", "code": "app.py: Flask routes"})
    assert "Attendance" in prompt and "UNSUPPORTED" in prompt and "app.py" in prompt

    print("selftest OK")


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        _selftest()
    else:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))