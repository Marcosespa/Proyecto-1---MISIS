from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename 
from flask_jwt_extended import jwt_required
import os
from app import summarizer 

doc_routes = Blueprint('docs', __name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Endpoint para subir archivos
@doc_routes.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File successfully uploaded', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

# Endpoint para generar resúmenes
@doc_routes.route('/summarize', methods=['POST'])
@jwt_required()
def summarize_text():
    if 'text' not in request.json:
        return jsonify({'error': 'No text provided for summarization'}), 400
    
    text = request.json['text']
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return jsonify({'summary': summary[0]['summary_text']}), 200

# Endpoint para procesar y resumir archivos
@doc_routes.route('/process_and_summarize', methods=['POST'])
@jwt_required()
def process_and_summarize():
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
            text = ""
            if filename.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            elif filename.endswith('.pdf'):
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                for page in reader.pages:
                    text += page.extract_text()
            elif filename.endswith('.docx'):
                from docx import Document
                document = Document(filepath)
                text = "\n".join([paragraph.text for paragraph in document.paragraphs])
            else:
                return jsonify({'error': 'File format not supported'}), 400

            # Llama al endpoint de resumen usando directamente el sumarizador
            summary = summarizer(text, max_length=500, min_length=30, do_sample=False)
            if summary and 'summary_text' in summary[0]:
                result = jsonify({'summary': summary[0]['summary_text']}), 200
            else:
                result = jsonify({'error': 'Failed to generate summary'}), 500

        except UnicodeDecodeError:
            result = jsonify({'error': 'Failed to decode file. Please ensure it is in a readable format.'}), 500
        except Exception as e:
            result = jsonify({'error': str(e)}), 500
        finally:
            # Limpieza: Eliminar el archivo temporal si no es necesario mantenerlo
            os.remove(filepath)
        
        return result
    else:
        return jsonify({'error': 'File type not allowed'}), 400