from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from fastapi_jwt_auth import AuthJWT
from app.config import settings
import os
import shutil
from pypdf import PdfReader
from docx import Document
from app.llama_model import generate_summary, answer_question  # Importa nuestro modelo Llama
import logging

router = APIRouter(prefix="/docs", tags=["documents"])

# Crear la carpeta de uploads si no existe
if not os.path.exists(settings.upload_folder):
    os.makedirs(settings.upload_folder)

# Almacenamiento en memoria para el texto de documentos subidos (para pruebas, en producción usar almacenamiento persistente)
user_files = {}

ALLOWED_EXTENSIONS = {"txt", "pdf", "docx", "md"}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(filepath: str, filename: str) -> str:
    text = ""
    extension = filename.rsplit('.', 1)[1].lower()
    if extension in {"txt", "md"}:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    elif extension == "pdf":
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif extension == "docx":
        document = Document(filepath)
        text = "\n".join([paragraph.text for paragraph in document.paragraphs])
    else:
        raise ValueError("Formato de archivo no soportado")
    return text

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    filename = file.filename
    if not allowed_file(filename):
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    file_location = os.path.join(settings.upload_folder, filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        text = extract_text(file_location, filename)
        user_files[user_id] = text
        os.remove(file_location)
        return {"message": "Archivo cargado y procesado correctamente", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_text(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    if user_id not in user_files:
        raise HTTPException(status_code=400, detail="No se encontró documento cargado para este usuario")
    
    text = user_files[user_id]
    summary = generate_summary(text, max_tokens=200)
    return {"summary": summary}

@router.post("/ask")
async def ask_question(request: Request, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    data = await request.json()
    if "question" not in data:
        raise HTTPException(status_code=400, detail="No se proporcionó la pregunta")
    if user_id not in user_files or not user_files[user_id].strip():
        raise HTTPException(status_code=400, detail="No se encontró documento cargado para este usuario")
    
    question = data["question"]
    context = user_files[user_id]
    answer = answer_question(question, context, max_tokens=100)
    return {"answer": answer}
