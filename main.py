main.pyfrom fastapi import FastAPI, UploadFile, File
from pdf2docx import Converter
import os
import shutil
import uuid

app = FastAPI()

@app.post("/convert")
async def convert_pdf_to_docx(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    temp_pdf = f"temp_{job_id}.pdf"
    temp_docx = f"temp_{job_id}.docx"

    with open(temp_pdf, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    cv = Converter(temp_pdf)
    cv.convert(temp_docx, start=0, end=None)
    cv.close()

    # In a real app, you would return the file. 
    # For now, we'll just confirm conversion.
    # To return file: from fastapi.responses import FileResponse
    # return FileResponse(temp_docx, filename=file.filename.replace(".pdf", ".docx"))

    os.remove(temp_pdf)
    # Note: temp_docx should be returned or cleaned up later.

    return {"message": "Conversion successful", "job_id": job_id}

@app.get("/")
def read_root():
    return {"status": "PDF to Word service is running"}
