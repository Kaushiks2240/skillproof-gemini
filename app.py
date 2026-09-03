from flask import Flask, render_template, jsonify, request
from database import save_project_analysis, get_project_from_db
from qr_generator import create_qr_code

app = Flask(__name__)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    return "SkillProof is working!"


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
        # Save complete Gemini analysis to Firestore
        project_id = save_project_analysis(analysis)

        # Generate QR code and public URL
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

# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
