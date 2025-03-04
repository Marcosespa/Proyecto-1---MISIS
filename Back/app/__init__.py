# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import os

db = SQLAlchemy()
jwt = JWTManager()
UPLOAD_FOLDER = 'uploads'

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Authorization", "Content-Type"]}})
    
    # Cargar configuración
    app.config.from_object('app.config.Config')
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Crear carpeta de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    
    # Importar Blueprints (asegúrate de que en estos archivos se importen los modelos si es necesario)
    from app.auth import auth_bp 
    from app.docs import docs_bp, upload_file
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(docs_bp, url_prefix="/docs")
    
    @app.route('/upload', methods=['POST'])
    @jwt_required()
    def wrapped_upload_file():
        return upload_file(app)
    
    from app.models import Usuario, Documento
    with app.app_context():
        db.create_all()
    
    return app
