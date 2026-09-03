import os
import random
import string

import firebase_admin
from firebase_admin import credentials, firestore


# Initialize Firebase only once
if not firebase_admin._apps:
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    if not service_account_path:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT is not set"
        )

    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)


# Firestore connection
db = firestore.client()


def generate_project_id():
    """Generate a unique SkillProof project ID."""

    while True:
        suffix = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        project_id = f"SP-{suffix}"

    doc = (
        db.collection("skillproof_projects")
        .document(project_id)
        .get()
    )

    if not doc.exists:
        return project_id


def save_project_analysis(analysis):
    """Save structured analysis to Firestore."""

    project_id = generate_project_id()

    data = {
        "project_id": project_id,
        "analysis": analysis
    }

    (
        db.collection("projects")
        .document(project_id)
        .set(data)
    )

    return project_id


def get_project_from_db(project_id):
    """Retrieve a project from Firestore."""

    doc = (
        db.collection("projects")
        .document(project_id)
        .get()
    )

    if not doc.exists:
        return None
import os
import random
import string

import firebase_admin
from firebase_admin import credentials, firestore


# Initialize Firebase only once
if not firebase_admin._apps:
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    if not service_account_path:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT is not set"
        )

    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)


# Firestore connection
db = firestore.client()


def generate_project_id():
    """Generate a unique SkillProof project ID."""

    while True:
        suffix = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        project_id = f"SP-{suffix}"

        doc = (
            db.collection("projects")
            .document(project_id)
            .get()
        )

        if not doc.exists:
            return project_id


def save_project_analysis(analysis):
    """Save structured analysis to Firestore."""

    project_id = generate_project_id()

    data = {
        "project_id": project_id,
        "analysis": analysis
    }

    (
        db.collection("projects")
        .document(project_id)
        .set(data)
    )

    return project_id


def get_project_from_db(project_id):
    """Retrieve a project from Firestore."""

    doc = (
        db.collection("projects")
        .document(project_id)
        .get()
    )

    if not doc.exists:
        return None

    return doc.to_dict()
