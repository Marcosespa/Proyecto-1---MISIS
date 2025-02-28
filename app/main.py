from fastapi import FastAPI
from app.auth import router as auth_router
from app.docs import router as docs_router
from app.config import settings
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from app.database import engine
from app.models import Usuario
from app.database import Base

# Crear las tablas de la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Document Management and AI Analysis SaaS")

app.include_router(auth_router)
app.include_router(docs_router)

class SettingsModel(BaseModel):
    authjwt_secret_key: str = settings.jwt_secret_key

@AuthJWT.load_config
def get_config():
    return SettingsModel()