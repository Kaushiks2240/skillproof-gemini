# SkillProof — Backend + Gemini (project rules for Claude Code)

**Read `SkillProof-Master-Document.md` for the full frozen spec. This file is the short version + hard rules.**

## What SkillProof is
Gemini judges whether a student's project **claims** are supported by their submitted **evidence** (code, screenshots, contribution notes), and returns STRONG / MODERATE / WEAK / UNSUPPORTED per claim. Core innovation = **Claim ↔ Evidence**. Framed as "evidence-backed" — NEVER authenticity / lie-detection / plagiarism.

## Our track
**BACKEND + GEMINI only.** Frontend (Google Stitch) and Firebase/DB belong to other members. Do NOT touch them.

## The spec is FROZEN
Do not rename, broaden, replace, or add features. Allowed changes only: bug fix, reliability, security, or Gemini/API compatibility. A new feature is not automatically good — ask "does this make Claim ↔ Evidence more useful?" If no, postpone.

## Locked contract (do not change)
- Endpoint: `POST /api/analyze` in `app.py`.
- Output JSON shape is enforced by `RESPONSE_SCHEMA` in `app.py` with top-level keys: `project, technologies, claims, skills, viva_questions, portfolio`.
- Support levels are an enum of EXACTLY: `STRONG`, `MODERATE`, `WEAK`, `UNSUPPORTED`.
- Gemini key comes from the `GEMINI_API_KEY` env var ONLY. Never hardcode, log, or commit it.
- Gemini model comes from the `GEMINI_MODEL` env var. Do not invent a model name.

## How to work here
Lazy and surgical: smallest change that works, reuse existing code, only the already-chosen deps (flask, flask-cors, google-genai). No speculative abstractions, no extra endpoints, no scaffolding "for later." Reuse `app.py`/`requirements.txt` if present — don't rewrite working code.

## Stop and ask before
Adding any dependency · changing the JSON contract or the enum · adding any endpoint beyond `/api/analyze` · touching Firebase/database/frontend code.

## The demo must prove
A deliberately-mixed project where an ML claim has NO supporting code comes back `WEAK`/`UNSUPPORTED` with non-empty `missing_evidence`. That is the money moment — protect it.

## Verify
- `python app.py --selftest` must print `selftest OK`.
- A real `POST /api/analyze` returns 200 with valid contract JSON and the unsupported ML claim marked WEAK/UNSUPPORTED.
