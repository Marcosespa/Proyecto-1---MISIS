import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

# Fixture para crear y limpiar la base de datos de test
@pytest.fixture(scope="module")
def test_db():
    # Crear las tablas de la base de datos
    Base.metadata.create_all(bind=engine)
    yield
    # Eliminar las tablas tras la ejecución de los tests
    Base.metadata.drop_all(bind=engine)

# Fixture que registra y loguea un usuario de prueba, devolviendo el header de autenticación
@pytest.fixture
def auth_header(test_db):
    reg_data = {
        "nombre_usuario": "testuser",
        "contrasena": "testpassword",
        "imagen_perfil": None
    }
    # Registrar usuario (ignorar error si ya existe)
    client.post("/auth/registro", json=reg_data)
    # Loguear usuario
    response = client.post("/auth/login", json={
        "nombre_usuario": "testuser",
        "contrasena": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_register_and_login(test_db):
    # Registro de un nuevo usuario
    reg_data = {
        "nombre_usuario": "newuser",
        "contrasena": "newpassword",
        "imagen_perfil": "image.png"
    }
    response = client.post("/auth/registro", json=reg_data)
    assert response.status_code == 201
    assert response.json()["mensaje"] == "Usuario registrado"
    
    # Login del usuario registrado
    response = client.post("/auth/login", json={
        "nombre_usuario": "newuser",
        "contrasena": "newpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_current_user(auth_header):
    response = client.get("/auth/usuarios/me", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    # El nombre del usuario debe ser uno de los registrados en los tests
    assert data["nombre_usuario"] in ["testuser", "newuser"]

def test_logout(auth_header):
    response = client.post("/auth/logout", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Sesión cerrada"

@pytest.mark.dependency(depends=["test_register_and_login"])
def test_upload_bitcoin_pdf(auth_header):
    # Verificar que el archivo "bitcoin.pdf" exista en la raíz del proyecto.
    pdf_path = os.path.join(os.getcwd(), "bitcoin.pdf")
    if not os.path.isfile(pdf_path):
        pytest.skip("El archivo 'bitcoin.pdf' no se encontró en la raíz del proyecto")
    
    with open(pdf_path, "rb") as file:
        response = client.post(
            "/docs/upload",
            headers=auth_header,
            files={"file": ("bitcoin.pdf", file, "application/pdf")}
        )
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["message"] == "Archivo cargado y procesado correctamente"
    assert json_resp["filename"] == "bitcoin.pdf"

@pytest.mark.dependency(depends=["test_upload_bitcoin_pdf"])
def test_summarize_bitcoin(auth_header):
    # Llama al endpoint para resumir el documento previamente cargado ("bitcoin.pdf")
    response = client.post("/docs/summarize", headers=auth_header)
    assert response.status_code == 200
    summary = response.json().get("summary", "")
    # Verificamos que el resumen no esté vacío (el contenido puede variar según el modelo)
    assert summary != ""
    print("Resumen obtenido:", summary)

@pytest.mark.dependency(depends=["test_upload_bitcoin_pdf"])
def test_ask_bitcoin(auth_header):
    # Enviar una pregunta basada en el documento "bitcoin.pdf"
    payload = {"question": "¿De qué trata el documento?"}
    response = client.post("/docs/ask", headers=auth_header, json=payload)
    assert response.status_code == 200
    answer = response.json().get("answer", "")
    # Verificamos que se obtenga una respuesta no vacía
    assert answer != ""
    print("Respuesta obtenida:", answer)

def test_upload_invalid_file(auth_header):
    # Crear un archivo temporal con formato no permitido (.exe)
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile("w+", delete=False, suffix=".exe") as tmp:
        tmp.write("Contenido no permitido")
        tmp_filename = tmp.name

    with open(tmp_filename, "rb") as file:
        response = client.post(
            "/docs/upload",
            headers=auth_header,
            files={"file": (os.path.basename(tmp_filename), file, "application/octet-stream")}
        )
    os.unlink(tmp_filename)
    assert response.status_code == 400
    assert response.json()["detail"] == "Tipo de archivo no permitido"

def test_summarize_without_upload(auth_header, monkeypatch):
    # Simula que el usuario no tiene documento cargado borrando todo el diccionario
    from app.docs import user_files
    user_files.clear()
    response = client.post("/docs/summarize", headers=auth_header)
    assert response.status_code == 400
    assert response.json()["detail"] == "No se encontró documento cargado para este usuario"

def test_ask_without_question(auth_header):
    response = client.post("/docs/ask", headers=auth_header, json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No se proporcionó la pregunta"
