from fastapi import FastAPI, UploadFile, File
import os

from app.pipeline.analyzer import analyze_fortran_code
from app.pipeline.translator import generate_python_code

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

    fortran_text = content.decode("utf-8", errors="ignore")

    analysis = analyze_fortran_code(fortran_text)
    python_code = generate_python_code(analysis)

    return {
        "filename": file.filename,
        "analysis": analysis,
        "python_code": python_code
    }
