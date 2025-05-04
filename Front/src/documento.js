// front/app/documento.js
// const API_URL = 'http://localhost:5050';
const API_URL = 'http://35.238.74.4:5000';

document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = './index.html';
        return;
    }

    let usuarioId = null;

    function obtenerUsuarioLoggeado() {
        fetch(`${API_URL}/auth/usuarios/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('No autorizado');
            return response.json();
        })
        .then(usuario => {
            const nombreUsuario = document.getElementById('nombre_usuario');
            const fotoPerfil = document.getElementById('fotoPerfil');
            nombreUsuario.textContent = usuario.nombre_usuario;
            usuarioId = usuario.id;

            if (!usuario.imagen_perfil || usuario.imagen_perfil.trim() === "") {
                fotoPerfil.src = "https://cdn.pixabay.com/photo/2017/01/25/17/35/picture-2008484_1280.png";
            } else {
                fotoPerfil.src = usuario.imagen_perfil;
            }
            fotoPerfil.style.display = "block";
            console.log("Usuario autenticado con ID:", usuarioId);
        })
        .catch(error => {
            console.error('Error al obtener usuario:', error);
            logout();
        });
    }

    function cargarListaDeDocumentos() {
        fetch(`${API_URL}/docs/list`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            const selector = document.getElementById('document-selector');
            if (!selector) return;
            selector.innerHTML = '<option value="">-- Selecciona un documento --</option>'; // 🧼 Limpiar antes
            data.documents.forEach(doc => {
                const option = document.createElement('option');
                option.value = doc.id;
                option.textContent = `${doc.filename}`;
                selector.appendChild(option);
            });

            const savedId = localStorage.getItem('documento_id');
            if (savedId) selector.value = savedId;
        })
        .catch(error => {
            console.error("Error al cargar documentos:", error);
            document.getElementById('selector-message').textContent = "No se pudieron cargar los documentos.";
        });
    }

    window.cambiarDocumento = function () {
        const selector = document.getElementById('document-selector');
        const documentoId = selector.value;
        if (documentoId) {
            localStorage.setItem('documento_id', documentoId);
            document.getElementById('selector-message').textContent = "Documento seleccionado correctamente.";
        } else {
            localStorage.removeItem('documento_id');
            document.getElementById('selector-message').textContent = "No hay documento seleccionado.";
        }
    };

    window.uploadFile = function () {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        if (!file) {
            alert('Selecciona un archivo');
            return;
        }
        const formData = new FormData();
        formData.append('file', file);

        fetch(`${API_URL}/docs/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
            const uploadMessage = document.getElementById('upload-message');
            if (status === 200) {
                uploadMessage.textContent = `${body.message} (${body.filename})`;
                uploadMessage.className = 'success';

                if (body.documento_id) {
                    localStorage.setItem('documento_id', body.documento_id);
                    console.log("ID del documento guardado:", body.documento_id);
                }

                cargarListaDeDocumentos();

                const selector = document.getElementById('document-selector');
                if (selector && body.documento_id) {
                    selector.value = body.documento_id;
                }
            } else {
                throw new Error(body.error || 'Error al subir archivo');
            }
        })
        .catch(error => {
            document.getElementById('upload-message').textContent = error.message;
            document.getElementById('upload-message').className = 'error';
        });
    };

    window.summarize = function () {
        const documentoId = localStorage.getItem('documento_id');
        console.log("ID del documento a resumir:", documentoId);
        if (!documentoId) {
            alert('Debes seleccionar o subir un documento primero.');
            return;
        }
        fetch(`${API_URL}/docs/summarize`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ documento_id: parseInt(documentoId) })
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
            const summaryMessage = document.getElementById('summary-message');
            if (status === 200) {
                document.getElementById('summary-result').value = body.summary;
                summaryMessage.textContent = 'Resumen generado';
                summaryMessage.className = 'success';
            } else {
                throw new Error(body.error || 'Error al generar resumen');
            }
        })
        .catch(error => {
            document.getElementById('summary-message').textContent = error.message;
            document.getElementById('summary-message').className = 'error';
        });
    };

    window.askQuestion = function () {
        const documentoId = localStorage.getItem('documento_id');
        const question = document.getElementById('question').value;
        if (!documentoId) {
            alert('Debes subir o seleccionar un documento primero.');
            return;
        }
        if (!question) {
            alert('Escribe una pregunta');
            return;
        }
        fetch(`${API_URL}/docs/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ question, documento_id: parseInt(documentoId) })
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
            const askMessage = document.getElementById('ask-message');
            if (status === 200) {
                document.getElementById('answer-result').value = body.answer;
                askMessage.textContent = 'Pregunta respondida';
                askMessage.className = 'success';
            } else {
                throw new Error(body.error || 'Error al responder pregunta');
            }
        })
        .catch(error => {
            document.getElementById('ask-message').textContent = error.message;
            document.getElementById('ask-message').className = 'error';
        });
    };

    window.logout = function () {
        localStorage.removeItem('token');
        window.location.href = './index.html';
    };

    obtenerUsuarioLoggeado();
    cargarListaDeDocumentos();
});
