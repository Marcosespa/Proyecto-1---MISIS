from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(64), unique=True, nullable=False)
    contrasena = db.Column(db.String(128), nullable=False)
    imagen_perfil = db.Column(db.String(256))  # URL o ruta del archivo de imagen

    def set_password(self, password):
        self.contrasena = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena, password)

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'
      
      