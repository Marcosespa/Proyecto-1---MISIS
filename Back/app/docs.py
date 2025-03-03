from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .config import config
import os
import shutil
from pypdf import PdfReader
from docx import Document
from .llama_model import generate_summary, answer_question

docs_bp = Blueprint('docs', __name__)

if not os.path.exists(config.UPLOAD_FOLDER):
    os.makedirs(config.UPLOAD_FOLDER)

# Almacenamiento en memoria para el texto de documentos subidos (solo para pruebas)
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
    filename = file.filename  # Para producción, usar secure_filename
    file_location = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(file_location)
    try:
        text = extract_text(file_location, filename)
        user_files[user_id] = text
        os.remove(file_location)
        return jsonify({'message': 'Archivo cargado y procesado correctamente', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@docs_bp.route('/summarize', methods=['POST'])
@jwt_required()
def summarize_text():
    user_id = get_jwt_identity()
    if user_id not in user_files:
        return jsonify({'error': 'No se encontró documento cargado para este usuario'}), 400
    text = user_files[user_id]
    summary = generate_summary(text, max_tokens=200)
    return jsonify({'summary': summary}), 200

@docs_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({'error': 'No se proporcionó la pregunta'}), 400
    if user_id not in user_files or not user_files[user_id].strip():
        return jsonify({'error': 'No se encontró documento cargado para este usuario'}), 400
    question = data["question"]
    context = user_files[user_id]
    answer = answer_question(question, context, max_tokens=100)
    return jsonify({'answer': answer}), 200