// front/app/documento.js
const API_URL = 'http://localhost:5050';

document.addEventListener('DOMContentLoaded', function () {
  const token = localStorage.getItem('token');
  if (!token) {
      window.location.href = '/index.html'; // Redirigir a login si no hay token
      return;
  }

  let usuarioId = null; // Almacenar el ID del usuario

  // Obtener datos del usuario autenticado
  function obtenerUsuarioLoggeado() {
      fetch(`${API_URL}/me`, {
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

          // Manejar la imagen de perfil
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
          logout(); // Cerrar sesión si hay error (e.g., token inválido)
      });
  }

  // Subir archivo
  window.uploadFile = function () {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert('Selecciona un archivo');
        return;
    }
    const formData = new FormData();
    formData.append('file', file); // Coincide con 'file' en el backend

    fetch(`${API_URL}/upload`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data }))) // ✅ Captura la respuesta correctamente
    .then(({ status, body }) => {
        const uploadMessage = document.getElementById('upload-message');
        if (status === 200) {  // ✅ Ahora validamos el código de respuesta HTTP
            uploadMessage.textContent = `${body.message} (${body.filename})`;
            uploadMessage.className = 'success';
        } else {
            throw new Error(body.error || 'Error al subir archivo');
        }
    })
    .catch(error => {
        document.getElementById('upload-message').textContent = error.message;
        document.getElementById('upload-message').className = 'error';
    });
};


  // Generar resumen
  window.summarize = function () {
    fetch(`${API_URL}/summarize`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
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

  // Hacer pregunta
  window.askQuestion = function () {
    const question = document.getElementById('question').value;
    if (!question) {
        alert('Escribe una pregunta');
        return;
    }
    fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ question })
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


  // Cerrar sesión
  window.logout = function () {
      localStorage.removeItem('token');
      window.location.href = '/index.html';
  };

  // Iniciar cargando los datos del usuario
  obtenerUsuarioLoggeado();
});