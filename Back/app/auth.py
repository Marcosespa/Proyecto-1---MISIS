from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Usuario
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    session = db.session
    try:
        usuario = session.query(Usuario).filter(Usuario.nombre_usuario == data['nombre_usuario']).first()
        if usuario:
            return jsonify({"mensaje": "Usuario ya registrado"}), 400
        nuevo_usuario = Usuario(
            nombre_usuario=data['nombre_usuario'],
            imagen_perfil=data.get('imagen_perfil')
        )
        nuevo_usuario.set_password(data['contrasena'])
        session.add(nuevo_usuario)
        session.commit()
        session.refresh(nuevo_usuario)
        return jsonify({"mensaje": "Usuario registrado"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"mensaje": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    session = db.session
    try:
        usuario = session.query(Usuario).filter(Usuario.nombre_usuario == data['nombre_usuario']).first()
        if not usuario or not usuario.check_password(data['contrasena']):
            return jsonify({"mensaje": "Credenciales inválidas"}), 401
        access_token = create_access_token(identity=str(usuario.id))
        if isinstance(access_token, bytes):
            access_token = access_token.decode('utf-8')
        return jsonify({"access_token": access_token}), 200
    except Exception as e:
        return jsonify({"mensaje": str(e)}), 500


@auth_bp.route('/usuarios/me', methods=['GET'])
@jwt_required()
def obtener_usuario_actual():
    user_id = get_jwt_identity()
    session = db.session
    usuario = session.get(Usuario, user_id)
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    return jsonify({
        "id": usuario.id,
        "nombre_usuario": usuario.nombre_usuario,
        "imagen_perfil": usuario.imagen_perfil
    }), 200
