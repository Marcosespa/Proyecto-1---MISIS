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
    #CORS(app, origins="http://localhost:8000")
    CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Authorization", "Content-Type"]}})
    
    app.config.from_object('app.config.Config')
    app.config['JWT_SECRET_KEY'] = 'super-secret-key' 
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.init_app(app)
    jwt.init_app(app)
        
    # Importar y registrar Blueprints con url_prefix
    from app.auth import auth_bp 
    from app.docs import docs_bp, upload_file 

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(docs_bp, url_prefix="/docs")
    
    @app.route('/upload', methods=['POST'])
    @jwt_required()
    def wrapped_upload_file():
        return upload_file(app)
    
    return app