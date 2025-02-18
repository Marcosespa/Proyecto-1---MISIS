import os

class Config:
    # Configuración de la base de datos (SQLite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de JWT
    JWT_SECRET_KEY = 'super-secret-key'  