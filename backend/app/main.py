from fastapi import FastAPI, UploadFile, File
import os

from app.agents.code_understanding_agent import analyze_fortran_code

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

    # READ FILE CONTENT FOR AI
    fortran_text = content.decode("utf-8", errors="ignore")

    analysis = analyze_fortran_code(fortran_text)

    return {
        "filename": file.filename,
        "analysis": analysis
    }