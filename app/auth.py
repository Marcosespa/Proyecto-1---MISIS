from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT

router = APIRouter(prefix="/auth", tags=["auth"])

class RegistroModel(BaseModel):
    nombre_usuario: str
    contrasena: str
    imagen_perfil: str = None

class LoginModel(BaseModel):
    nombre_usuario: str
    contrasena: str

@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registro(usuario: RegistroModel, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_usuario = db.query(models.Usuario).filter(models.Usuario.nombre_usuario == usuario.nombre_usuario).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Usuario ya registrado")
    nuevo_usuario = models.Usuario(
        nombre_usuario=usuario.nombre_usuario,
        imagen_perfil=usuario.imagen_perfil
    )
    nuevo_usuario.set_password(usuario.contrasena)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario registrado"}

@router.post("/login")
def login(user: LoginModel, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.nombre_usuario == user.nombre_usuario).first()
    if not db_usuario or not db_usuario.check_password(user.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    access_token = Authorize.create_access_token(subject=db_usuario.id)
    return {"access_token": access_token}

@router.post("/logout")
def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"mensaje": "Sesión cerrada"}

@router.get("/usuarios/me")
def obtener_usuario_actual(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    db_usuario = db.get(models.Usuario, user_id)

    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id": db_usuario.id,
        "nombre_usuario": db_usuario.nombre_usuario,
        "imagen_perfil": db_usuario.imagen_perfil
    }
