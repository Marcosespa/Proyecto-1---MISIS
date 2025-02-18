from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from transformers import pipeline

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

    db.init_app(app)
    jwt.init_app(app)
    global summarizer
    summarizer = pipeline("summarization")
    
    from app.auth import auth_routes 
    from app.docs import doc_routes

    app.register_blueprint(auth_routes)

    return app