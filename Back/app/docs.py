from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .config import config
from werkzeug.utils import secure_filename
import os
from pypdf import PdfReader
from docx import Document
from app import db
from .models import Documento
import requests
import time
from dotenv import load_dotenv

docs_bp = Blueprint('docs', __name__)

# Configuración de la API de Gemini (ajusta según tu endpoint y clave)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"  # Endpoint de Gemini

if not os.path.exists(config.UPLOAD_FOLDER):
    os.makedirs(config.UPLOAD_FOLDER)

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

@docs_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400

    filename = secure_filename(file.filename)
    file_location = os.path.join("mnt/nfs/files", filename)
    file.save(os.path.join("/mnt/nfs/files", filename))
    try:
        text = extract_text(file_location, filename)
        os.remove(file_location)
        session = db.session
        documento = session.query(Documento).filter(Documento.user_id == user_id).first()
        if documento:
            documento.filename = filename
            documento.text = text
            documento.summary = None
        else:
            documento = Documento(
                user_id=user_id,
                filename=filename,
                text=text
            )
            session.add(documento)
        session.commit()
        session.refresh(documento)
        return jsonify({'message': 'Archivo cargado y procesado correctamente', 'filename': filename}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500

@docs_bp.route('/summarize', methods=['POST'])
@jwt_required()
def summarize_text():
    user_id = get_jwt_identity()
    session = db.session
    documento = session.query(Documento).filter(Documento.user_id == user_id).first()
    if not documento:
        return jsonify({'error': 'No se encontró documento cargado para este usuario'}), 400
    summary = generate_summary(documento.text, max_tokens=200)
    documento.summary = summary
    session.commit()
    session.refresh(documento)
    return jsonify({'summary': summary}), 200

@docs_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({'error': 'No se proporcionó la pregunta'}), 400
    session = db.session
    documento = session.query(Documento).filter(Documento.user_id == user_id).first()
    if not documento or not documento.text.strip():
        return jsonify({'error': 'No se encontró documento cargado para este usuario'}), 400
    question = data["question"]
    answer = answer_question(question, documento.text, max_tokens=100)
    return jsonify({'answer': answer}), 200

# Nuevas funciones para usar la API de Gemini
def truncate_text(text: str, max_chars: int = 2000) -> str:
    """
    Trunca el texto a un máximo de caracteres para evitar exceder el límite de la API.
    """
    if len(text) > max_chars:
        return text[:max_chars]
    return text

def generate_summary(text: str, max_tokens: int = 150) -> str:
    """
    Genera un resumen del texto usando la API de Gemini.
    """
    truncated_text = truncate_text(text, max_chars=2000)
    prompt = f"Resume el siguiente texto de forma clara y concisa:\n\n{truncated_text}\n\nResumen:"
    
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.7,
        }
    }
    
    start_time = time.time()
    response = requests.post(
        f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
        headers=headers,
        json=payload
    )
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        summary = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"Tiempo de respuesta del resumen: {elapsed_time:.2f} segundos")
        return summary
    else:
        raise Exception(f"Error en la API de Gemini: {response.text}")

def answer_question(question: str, context: str, max_tokens: int = 100) -> str:
    """
    Responde una pregunta basada en el contexto usando la API de Gemini.
    """
    truncated_context = truncate_text(context, max_chars=2000)
    prompt = f"Contexto:\n{truncated_context}\n\nPregunta: {question}\n\nRespuesta:"
    
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.7,
        }
    }
    
    start_time = time.time()
    response = requests.post(
        f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
        headers=headers,
        json=payload
    )
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        answer = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"Tiempo de respuesta para la pregunta: {elapsed_time:.2f} segundos")
        return answer
    else:
        raise Exception(f"Error en la API de Gemini: {response.text}")
