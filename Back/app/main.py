from flask import Flask
from .auth import auth_bp
from .docs import docs_bp
from .config import config
from flask_jwt_extended import JWTManager
from .database import engine, Base

# def create_app():
#     app = Flask(__name__)
    
#     # Configuración
#     app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
#     app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
#     app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    
#     # Inicializar JWT
#     jwt = JWTManager(app)
    
#     # Registrar Blueprints
#     app.register_blueprint(auth_bp, url_prefix='/auth')
#     app.register_blueprint(docs_bp, url_prefix='/docs')
    
#     # Crear tablas de la base de datos
#     Base.metadata.create_all(bind=engine)
    
#     return app

# app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)
