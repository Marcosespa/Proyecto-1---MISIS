from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import Config
from app.database import db
import os
from flask_jwt_extended import jwt_required
from dotenv import load_dotenv
load_dotenv()

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Authorization", "Content-Type"]}})
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Crear carpeta de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)

    @app.route('/')
    def index():
        return "API corriendo"

    # Registrar Blueprints
    from app.auth import auth_bp 
    from app.docs import docs_bp, upload_file
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(docs_bp, url_prefix="/docs")

    # @app.route('/upload', methods=['POST'])
    # @jwt_required()
    # def wrapped_upload_file():
    #     return upload_file()

    return app
