from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename 
from flask_jwt_extended import get_jwt, jwt_required,get_jwt_identity
import os

doc_routes = Blueprint('docs', __name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Endpoint para subir archivos
@doc_routes.route('/upload', methods=['POST'])
@jwt_required()
def upload_file(app):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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