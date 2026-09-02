import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.testclient import TestClient

app = FastAPI()

# Create a dummy MP3 file in public_assets/audio
test_dir = Path("public_assets/audio")
test_dir.mkdir(parents=True, exist_ok=True)
test_file = test_dir / "test_range.mp3"
test_file.write_bytes(b"\xff\xfb\x90\x00" * 100) # 400 bytes dummy mp3

@app.get("/test-audio")
def get_test_audio():
    abs_path = os.path.abspath(str(test_file))
    return FileResponse(abs_path, media_type="audio/mpeg")

client = TestClient(app)

# 1. Normal GET
res1 = client.get("/test-audio")
print("1. Normal GET status:", res1.status_code)
print("   Content-Length:", res1.headers.get("content-length"))
print("   Accept-Ranges:", res1.headers.get("accept-ranges"))

# 2. Range request from Safari / iOS
res2 = client.get("/test-audio", headers={"Range": "bytes=0-100"})
print("2. Range request status:", res2.status_code)
print("   Content-Range:", res2.headers.get("content-range"))
print("   Content-Length:", res2.headers.get("content-length"))
