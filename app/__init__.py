from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from transformers import pipeline
from flask_jwt_extended import get_jwt, jwt_required,get_jwt_identity
import os

db = SQLAlchemy()
jwt = JWTManager()
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    CORS(app, origins="http://localhost:8000")

    app.config.from_object('app.config.Config')
    app.config['JWT_SECRET_KEY'] = 'super-secret-key' 
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.init_app(app)
    jwt.init_app(app)
    
    # SI ES QUE NO DEJAMOS EL ARCHIVO GGUF 
    # global summarizer
    # summarizer = pipeline("summarization")
    
    from llama_cpp import Llama
    MODEL_PATH="/Users/marcosrodrigo/Desktop/Universidad/Quinto semestre/Desarrollo de Soluciones Cloud/mistral-7b-instruct.Q4_K_M.gguf"

    def load_summarizer():
        return Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,  # Reduce el uso de memoria
            n_threads=4,  # Limita el uso de CPU
            n_batch=8,  # Controla el procesamiento por lotes
            verbose=False  # Desactiva logs innecesarios
        )
    global summarizer
    summarizer = load_summarizer()
        
    # Importar y registrar Blueprints
    from app.auth import auth_bp 
    from app.docs import docs_bp, upload_file 
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(docs_bp)
    
    @app.route('/upload', methods=['POST'])
    @jwt_required()
    def wrapped_upload_file():
        return upload_file(app)
    
    return app