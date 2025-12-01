from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2
import io

app = FastAPI()

# السماح للواجهة (localhost:5500) تتصل بالباك إند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeResponse(BaseModel):
    contract_text: str
    page_count: int
    filename: str

@app.post("/api/analyze-contract", response_model=AnalyzeResponse)
async def analyze_contract(file: UploadFile = File(...)):
    # نتأكد أنه PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # نقرأ محتوى الملف في الذاكرة
    content = await file.read()
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read PDF file.")

    texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        texts.append(page_text)

    full_text = "\n\n".join(texts).strip()
    if not full_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    return AnalyzeResponse(
        contract_text=full_text,
        page_count=len(reader.pages),
        filename=file.filename,
    )
