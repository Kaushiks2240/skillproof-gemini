import os
import qrcode


def create_qr_code(project_id):
    """
    Create a QR code for the public SkillProof portfolio.
    """

    base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:5000")
    base_url = base_url.rstrip("/")

    public_url = f"{base_url}/p/{project_id}"

    os.makedirs("static/qr", exist_ok=True)

    file_path = f"static/qr/{project_id}.png"

    qr = qrcode.make(public_url)
    qr.save(file_path)

    return file_path, public_url
