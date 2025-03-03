from sqlalchemy import Column, Integer, String
from .database import Base
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(64), unique=True, nullable=False, index=True)
    contrasena = Column(String(128), nullable=False)
    imagen_perfil = Column(String(256), nullable=True)

    def set_password(self, password: str):
        self.contrasena = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.contrasena, password)
