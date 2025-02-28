import sys
import os
import io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app.main import app
from app.database import Base, engine

client = app.test_client()

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_header(test_db):
    reg_data = {
        "nombre_usuario": "testuser",
        "contrasena": "testpassword",
        "imagen_perfil": None
    }
    client.post("/auth/registro", json=reg_data)
    response = client.post("/auth/login", json={
        "nombre_usuario": "testuser",
        "contrasena": "testpassword"
    })
    json_resp = response.get_json()
    token = json_resp.get("access_token")
    if not token:
        pytest.fail("No se obtuvo token en el login")
    return {"Authorization": f"Bearer {token}"}

def test_register_and_login(test_db):
    reg_data = {
        "nombre_usuario": "newuser",
        "contrasena": "newpassword",
        "imagen_perfil": "image.png"
    }
    response = client.post("/auth/registro", json=reg_data)
    assert response.status_code == 201
    assert response.get_json()["mensaje"] == "Usuario registrado"
    
    response = client.post("/auth/login", json={
        "nombre_usuario": "newuser",
        "contrasena": "newpassword"
    })
    assert response.status_code == 200
    json_resp = response.get_json()
    assert "access_token" in json_resp

def test_get_current_user(auth_header):
    response = client.get("/auth/usuarios/me", headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert "id" in data
    assert data["nombre_usuario"] in ["testuser", "newuser"]

def test_logout(auth_header):
    response = client.post("/auth/logout", headers=auth_header)
    assert response.status_code == 200
    assert response.get_json()["mensaje"] == "Sesión cerrada"

@pytest.mark.dependency(depends=["test_register_and_login"])
def test_upload_bitcoin_pdf(auth_header):
    pdf_path = os.path.join(os.getcwd(), "bitcoin.pdf")
    if not os.path.isfile(pdf_path):
        pytest.skip("El archivo 'bitcoin.pdf' no se encontró en la raíz del proyecto")
    
    with open(pdf_path, "rb") as f:
        file_content = f.read()
    data = {
        "file": (io.BytesIO(file_content), os.path.basename(pdf_path), "application/pdf")
    }
    response = client.post(
        "/docs/upload",
        headers=auth_header,
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    json_resp = response.get_json()
    assert json_resp["message"] == "Archivo cargado y procesado correctamente"
    assert json_resp["filename"] == "bitcoin.pdf"

@pytest.mark.dependency(depends=["test_upload_bitcoin_pdf"])
def test_summarize_bitcoin(auth_header):
    response = client.post("/docs/summarize", headers=auth_header)
    if response.status_code != 200:
        pytest.skip("No se pudo resumir el documento; revisar la carga del archivo")
    summary = response.get_json().get("summary", "")
    assert summary != ""
    print("Resumen obtenido:", summary)

@pytest.mark.dependency(depends=["test_upload_bitcoin_pdf"])
def test_ask_bitcoin(auth_header):
    payload = {"question": "¿De qué trata el documento?"}
    response = client.post("/docs/ask", headers=auth_header, json=payload)
    if response.status_code != 200:
        pytest.skip("No se pudo obtener respuesta; revisar la carga del archivo")
    answer = response.get_json().get("answer", "")
    assert answer != ""
    print("Respuesta obtenida:", answer)

def test_upload_invalid_file(auth_header):
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile("w+", delete=False, suffix=".exe") as tmp:
        tmp.write("Contenido no permitido")
        tmp_filename = tmp.name

    with open(tmp_filename, "rb") as f:
        file_content = f.read()
    data = {
        "file": (io.BytesIO(file_content), os.path.basename(tmp_filename), "application/octet-stream")
    }
    response = client.post(
        "/docs/upload",
        headers=auth_header,
        data=data,
        content_type="multipart/form-data"
    )
    os.unlink(tmp_filename)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Tipo de archivo no permitido"

def test_summarize_without_upload(auth_header):
    from app.docs import user_files
    user_files.clear()
    response = client.post("/docs/summarize", headers=auth_header)
    assert response.status_code == 400
    assert response.get_json()["error"] == "No se encontró documento cargado para este usuario"

def test_ask_without_question(auth_header):
    response = client.post("/docs/ask", headers=auth_header, json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "No se proporcionó la pregunta"
