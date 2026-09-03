from qr_generator import create_qr_code

project_id = "SP-HN6626"

file_path, public_url = create_qr_code(project_id)

print("QR created successfully!")
print("QR file:", file_path)
print("Public URL:", public_url)
