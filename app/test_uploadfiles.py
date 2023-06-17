from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

files = [("files", open("main.py", "rb")), ("files", open("test_uploadfiles.py", "rb"))]
response = client.post(url="docker/upload-source-files/", files=files)
assert len(response.json()) != 0
print()
print(response.json())


# def test_send_multiple_files():
