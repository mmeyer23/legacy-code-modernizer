from fastapi import FastAPI, UploadFile, File
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def health_check():
    return {"status": "Legacy Modernizer API running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": file.filename,
        "size_bytes": len(content),
        "message": "File uploaded successfully"
    }