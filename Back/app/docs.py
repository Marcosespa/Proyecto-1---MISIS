from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .config import config
from werkzeug.utils import secure_filename
import os
from pypdf import PdfReader
from docx import Document
from .llama_model import generate_summary, answer_question
from .database import SessionLocal
from .models import Documento

docs_bp = Blueprint('docs', __name__)

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
    
    print("request.method:", request.method)
    print("request.headers:", request.headers)
    print("request.files:", request.files)
    print("request.form:", request.form)  # Para ver si hay otros campos
    
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400

    filename = secure_filename(file.filename)
    file_location = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(file_location)
    try:
        text = extract_text(file_location, filename)
        os.remove(file_location)
        db = SessionLocal()
        # Si el usuario ya tiene un documento, se actualiza; de lo contrario, se crea uno nuevo
        documento = db.query(Documento).filter(Documento.user_id == user_id).first()
        if documento:
            documento.filename = filename
            documento.text = text
            documento.summary = None  # Reinicia el resumen al actualizar el documento
        else:
            documento = Documento(
                user_id=user_id,
                filename=filename,
                text=text
            )
            db.add(documento)
        db.commit()
        db.refresh(documento)
        db.close()
        return jsonify({'message': 'Archivo cargado y procesado correctamente', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@docs_bp.route('/summarize', methods=['POST'])
@jwt_required()
def summarize_text():
    user_id = get_jwt_identity()
    db = SessionLocal()
    documento = db.query(Documento).filter(Documento.user_id == user_id).first()
    if not documento:
        db.close()
        return jsonify({'error': 'No se encontró documento cargado para este usuario'}), 400
    summary = generate_summary(documento.text, max_tokens=200)
    # Se almacena el resumen en el registro del documento
    documento.summary = summary
    db.commit()
    db.refresh(documento)
    db.close()
    return jsonify({'summary': summary}), 200

@docs_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({'error': 'No se proporcionó la pregunta'}), 400
    db = SessionLocal()
    documento = db.query(Documento).filter(Documento.user_id == user_id).first()
    if not documento or not documento.text.strip():
        db.close()
        return jsonify({'error': 'No se encontró documento cargado para este usuario'}), 400
    question = data["question"]
    answer = answer_question(question, documento.text, max_tokens=100)
    db.close()
    return jsonify({'answer': answer}), 200
