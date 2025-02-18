from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from app import db
from app.models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt, jwt_required,get_jwt_identity

auth_routes = Blueprint('auth', __name__)

# Endpoint para registrar un nuevo usuario
@auth_routes.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    hashed_password = generate_password_hash(data['contrasena'], method='pbkdf2:sha256')
    nuevo_usuario = Usuario(
        nombre_usuario=data['nombre_usuario'],
        contrasena=hashed_password,
        imagen_perfil=data.get('imagen_perfil')
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario registrado"}), 201

# Endpoint para iniciar sesión
@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = Usuario.query.filter_by(nombre_usuario=data['nombre_usuario']).first()
    if usuario and check_password_hash(usuario.contrasena, data['contrasena']):
        access_token = create_access_token(identity=str(usuario.id))  
        return jsonify(access_token=access_token), 200
    return jsonify({"mensaje": "Credenciales inválidas"}), 401
  
# Endpoint para cerrar sesión
@auth_routes.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']  
    return jsonify({"mensaje": "Sesión cerrada"}), 200

@auth_routes.route('/usuarios/me', methods=['GET'])
@jwt_required()
def obtener_usuario_actual():
    usuario_id = get_jwt_identity() 
    usuario = Usuario.query.get(usuario_id)  
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    return jsonify({
        "id": usuario.id,
        "nombre_usuario": usuario.nombre_usuario,
        "imagen_perfil": usuario.imagen_perfil
    }), 200