from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .database import Base
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre_usuario = db.Column(db.String(64), unique=True, nullable=False, index=True)
    contrasena = db.Column(db.String(128), nullable=False)
    imagen_perfil = db.Column(db.String(256), nullable=True)

    def set_password(self, password: str):
        self.contrasena = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.contrasena, password)
    
class Documento(Base):
    __tablename__ = 'documentos'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    filename = Column(String(256), nullable=False)
    text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
