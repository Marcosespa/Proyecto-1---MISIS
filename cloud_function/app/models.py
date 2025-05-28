from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(64), unique=True, nullable=False, index=True)
    contrasena = Column(String(512), nullable=False)
    imagen_perfil = Column(String(256), nullable=True)
    documentos = relationship("Documento", backref="usuario", lazy=True)

    def set_password(self, password: str):
        self.contrasena = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.contrasena, password)

class Documento(Base):
    __tablename__ = 'documentos'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    filename = Column(String(256), nullable=False)
    text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
