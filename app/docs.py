from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename 
from flask_jwt_extended import jwt_required,get_jwt_identity
import os
from app import summarizer 
from transformers import pipeline
import logging
logging.basicConfig(level=logging.DEBUG)
from PyPDF2 import PdfReader
from docx import Document

global summarizer
summarizer = pipeline("summarization")
qa_pipeline = pipeline("question-answering")



doc_routes = Blueprint('docs', __name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'md'}
user_files = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@doc_routes.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Permite subir archivos y guardarlos temporalmente"""
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            text = extract_text(filepath, filename)
            user_files[user_id] = text  # Guarda el texto en memoria del usuario
            os.remove(filepath)  
            
            return jsonify({'message': 'File successfully uploaded and processed', 'filename': filename}), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File type not allowed'}), 400

def extract_text(filepath, filename):
    """Extrae el texto según el tipo de archivo"""
    text = ""
    if filename.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    elif filename.endswith('.pdf'):
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() or ""  # Evita errores si no puede extraer
    elif filename.endswith('.docx'):
        document = Document(filepath)
        text = "\n".join([paragraph.text for paragraph in document.paragraphs])
    else:
        raise ValueError("File format not supported")
    
    return text
  
def extract_text(filepath, filename):
  """Extrae el texto según el tipo de archivo"""
  text = ""
  if filename.endswith('.txt'):
      with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
          text = f.read()
  elif filename.endswith('.pdf'):
      reader = PdfReader(filepath)
      for page in reader.pages:
          text += page.extract_text() or ""  # Evita errores si no puede extraer
  elif filename.endswith('.docx'):
      document = Document(filepath)
      text = "\n".join([paragraph.text for paragraph in document.paragraphs])
  else:
      raise ValueError("File format not supported")
  
  return text

@doc_routes.route('/summarize', methods=['POST'])
@jwt_required()
def summarize_text():
    """Genera un resumen del texto del archivo procesado"""
    user_id = get_jwt_identity()
    
    if user_id not in user_files:
        return jsonify({'error': 'No uploaded document found for this user'}), 400

    text = user_files[user_id]  # Recupera el texto del archivo del usuario

    summary = summarizer(text, max_length=200, min_length=50, do_sample=False)
    
    return jsonify({'summary': summary[0]['summary_text']}), 200


@doc_routes.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    """Permite hacer preguntas sobre el archivo previamente subido"""
    user_id = get_jwt_identity()
    
    if user_id not in user_files:
        return jsonify({'error': 'No uploaded document found for this user'}), 400

    if 'question' not in request.json:
        return jsonify({'error': 'No question provided'}), 400
    if user_id not in user_files or not user_files[user_id].strip():
        return jsonify({'error': 'No uploaded document found or document is empty for this user'}), 400

    question = request.json['question']
    context = user_files[user_id]  # Recupera el texto del archivo del usuario
    print(f"Documentos guardados: {user_files}")
    logging.debug(f"El user context es este: {context[:500]}") 
    
    
    answer = qa_pipeline(question=question, context=context)

    return jsonify({'answer': answer['answer']}), 200