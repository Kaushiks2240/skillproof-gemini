from database import save_project_analysis, get_project_from_db

sample_analysis = {
    "project": {
        "title": "SkillProof Demo",
        "problem": "Students struggle to prove their actual skills.",
        "solution": "Evidence-backed student skill profiles."
    },
    "technologies": [
        {
            "name": "Python",
            "evidence": "Flask backend",
            "strength": "strong"
        }
    ],
    "claims": [
        {
            "claim": "Built Flask backend",
            "support": "strong",
            "supporting_evidence": ["app.py"],
            "missing_evidence": [],
            "reason": "Backend code was submitted."
        }
    ],
    "skills": [
        {
            "skill": "Python",
            "strength": "strong",
            "evidence": "Flask backend code"
        }
    ],
    "viva_questions": [
        {
            "question": "Why did you choose Flask?",
            "topic": "Backend",
            "reason": "Based on submitted Flask evidence."
        }
    ],
    "portfolio": {
        "summary": "Evidence-backed SkillProof demo.",
        "contribution": "Built the Flask backend.",
        "technologies": ["Python", "Flask"],
        "evidence_highlights": ["app.py"]
    }
}

project_id = save_project_analysis(sample_analysis)

print("Saved project:", project_id)

project = get_project_from_db(project_id)

if project:
    print("Retrieved successfully!")
    print("Project ID:", project["project_id"])
    print("Title:", project["analysis"]["project"]["title"])
else:
    print("ERROR: Project could not be retrieved.")
