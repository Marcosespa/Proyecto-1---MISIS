// front/app/documento.js
const API_URL = 'https://misis-app-1073903910796.us-central1.run.app';

document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = './index.html';
        return;
    }

    // Inicializar la información del usuario
    fetch(`${API_URL}/auth/usuarios/me`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Token inválido o expirado');
        return response.json();
    })
    .then(data => {
        document.getElementById('nombre_usuario').textContent = data.nombre_usuario;
        if (data.imagen_perfil) {
            const foto = document.getElementById('fotoPerfil');
            foto.src = data.imagen_perfil;
            foto.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Sesión expirada. Vuelve a iniciar sesión.');
        localStorage.removeItem('token');
        window.location.href = './index.html';
    });

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
            
            // Guardar el valor actual
            const currentValue = selector.value;
            
            // Limpiar el selector
            selector.innerHTML = '<option value="">-- Selecciona un documento --</option>';
            
            // Agregar los documentos
            data.documents.forEach(doc => {
                const option = document.createElement('option');
                option.value = doc.id;
                option.textContent = `${doc.filename} (${doc.status})`;
                selector.appendChild(option);
            });

            // Restaurar el valor seleccionado o usar el guardado en localStorage
            const savedId = localStorage.getItem('documento_id');
            if (savedId) {
                selector.value = savedId;
            } else if (currentValue) {
                selector.value = currentValue;
            }
            
            // Actualizar el mensaje
            const selectorMessage = document.getElementById('selector-message');
            if (selector.value) {
                const selectedDoc = data.documents.find(doc => doc.id === parseInt(selector.value));
                if (selectedDoc) {
                    selectorMessage.textContent = `Documento seleccionado: ${selectedDoc.filename} (${selectedDoc.status})`;
                    selectorMessage.className = selectedDoc.status === 'processed' ? 'success' : 'warning';
                }
            } else {
                selectorMessage.textContent = "No hay documento seleccionado.";
                selectorMessage.className = '';
            }
        })
        .catch(error => {
            console.error("Error al cargar documentos:", error);
            document.getElementById('selector-message').textContent = "No se pudieron cargar los documentos.";
            document.getElementById('selector-message').className = 'error';
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
        const token = localStorage.getItem('token');
        
        if (!token) {
            alert('No hay sesión activa. Por favor, inicia sesión nuevamente.');
            window.location.href = './index.html';
            return;
        }

        // Decodificar el token para ver el user_id
        try {
            const tokenParts = token.split('.');
            const payload = JSON.parse(atob(tokenParts[1]));
            console.log("Token payload:", payload);
            console.log("User ID del token:", payload.sub);
        } catch (e) {
            console.error("Error al decodificar token:", e);
        }

        console.log("Token usado:", token);
        console.log("ID del documento a resumir:", documentoId);
        if (!documentoId) {
            alert('Debes seleccionar o subir un documento primero.');
            return;
        }

        const summaryMessage = document.getElementById('summary-message');
        summaryMessage.textContent = 'Verificando documento...';
        summaryMessage.className = '';

        // Primero verificar el estado del documento
        fetch(`${API_URL}/docs/list`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            console.log("Respuesta de /docs/list:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Datos recibidos:", data);
            const documento = data.documents.find(doc => doc.id === parseInt(documentoId));
            if (!documento) {
                throw new Error('Documento no encontrado');
            }
            
            // Verificar el estado del documento
            if (documento.status === 'pending') {
                summaryMessage.textContent = 'El documento aún está siendo procesado. Por favor, espera unos minutos e intenta nuevamente.';
                summaryMessage.className = 'warning';
                return null; // No continuar con el resumen
            }
            
            if (!documento.text || documento.text.trim() === '') {
                summaryMessage.textContent = 'El documento no tiene texto para resumir. Por favor, intenta subir el documento nuevamente.';
                summaryMessage.className = 'error';
                return null; // No continuar con el resumen
            }
            
            // Si todo está bien, proceder con el resumen
            summaryMessage.textContent = 'Generando resumen...';
            return fetch(`${API_URL}/docs/summarize`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ documento_id: parseInt(documentoId) })
            });
        })
        .then(response => {
            if (!response) return; // Si response es null, significa que hubo un error en la verificación
            console.log("Respuesta de /docs/summarize:", response.status);
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
                }
                return response.text().then(text => {
                    console.log("Error response:", text);
                    try {
                        const data = JSON.parse(text);
                        throw new Error(data.error || 'Error al generar resumen');
                    } catch (e) {
                        throw new Error(`Error al generar resumen: ${text}`);
                    }
                });
            }
            return response.json();
        })
        .then(data => {
            if (!data) return; // Si data es null, significa que hubo un error en la verificación
            document.getElementById('summary-result').value = data.summary;
            summaryMessage.textContent = 'Resumen generado';
            summaryMessage.className = 'success';
        })
        .catch(error => {
            console.error('Error:', error);
            summaryMessage.textContent = error.message;
            summaryMessage.className = 'error';
            if (error.message.includes('Sesión expirada')) {
                setTimeout(() => {
                    window.location.href = './index.html';
                }, 2000);
            }
        });
    };

    // Función para reintentar el procesamiento del documento
    window.retryProcessing = function() {
        const documentoId = localStorage.getItem('documento_id');
        const token = localStorage.getItem('token');
        
        if (!token || !documentoId) {
            alert('No hay sesión activa o documento seleccionado');
            return;
        }

        // Crear un input de tipo file oculto
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf,.doc,.docx,.txt';
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);

        // Manejar la selección del archivo
        fileInput.onchange = function(event) {
            const file = event.target.files[0];
            if (!file) {
                alert('Por favor, selecciona un archivo.');
                return;
            }

            const summaryMessage = document.getElementById('summary-message');
            summaryMessage.textContent = 'Reintentando procesamiento...';
            summaryMessage.className = '';

            // Crear FormData y agregar el archivo
            const formData = new FormData();
            formData.append('file', file);

            fetch(`${API_URL}/docs/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                summaryMessage.textContent = 'Procesamiento reiniciado. Por favor, espera unos minutos e intenta generar el resumen nuevamente.';
                summaryMessage.className = 'success';
            })
            .catch(error => {
                console.error('Error:', error);
                summaryMessage.textContent = `Error al reintentar procesamiento: ${error.message}`;
                summaryMessage.className = 'error';
            })
            .finally(() => {
                // Limpiar el input de archivo
                document.body.removeChild(fileInput);
            });
        };

        // Simular clic en el input de archivo
        fileInput.click();
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
