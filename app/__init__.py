from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app, origins="http://localhost:8000")

    app.config.from_object('app.config.Config')
    app.config['JWT_SECRET_KEY'] = 'super-secret-key' 


    db.init_app(app)
    jwt.init_app(app)

    # from app.routes import main_routes
    from app.auth import auth_routes 
    # app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)


    return app