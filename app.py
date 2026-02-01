import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
from pdf2docx import Converter
from backend.formatter import clean_and_format_docx

app = FastAPI(title="PDF to Word & Formatter API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "online", "service": "PDF to Word Converter"}

@app.post("/convert")
async def convert_pdf_to_word(file: UploadFile = File(...)):
    """
    Converts uploaded PDF to Word (docx).
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    input_path = UPLOAD_DIR / file.filename
    output_filename = file.filename.replace('.pdf', '.docx')
    output_path = OUTPUT_DIR / output_filename

    try:
        # Save uploaded file
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Convert
        cv = Converter(str(input_path))
        cv.convert(str(output_path), start=0, end=None)
        cv.close()

        return FileResponse(
            path=output_path, 
            filename=output_filename, 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    finally:
        # Cleanup input (optional, depending on load)
        if input_path.exists():
            input_path.unlink()

@app.post("/format")
async def format_word_doc(file: UploadFile = File(...)):
    """
    Applies formatting rules to an uploaded Word document.
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX")
        
    input_path = UPLOAD_DIR / f"raw_{file.filename}"
    output_filename = f"formatted_{file.filename}"
    output_path = OUTPUT_DIR / output_filename
    
    try:
         # Save uploaded file
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Apply formatting using existing logic
        clean_and_format_docx(str(input_path), str(output_path))
        
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Formatting failed: {str(e)}")
    finally:
        if input_path.exists():
            input_path.unlink()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
