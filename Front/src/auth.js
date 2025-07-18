// const API_URL = 'http://localhost:5050';
// const API_URL = 'http://35.238.74.4:5000';
const API_URL = 'https://misis-app-1073903910796.us-central1.run.app';

document.addEventListener('DOMContentLoaded', function () {
  const formLogin = document.getElementById('form-login');
  const formRegistro = document.getElementById('form-registro');

  if (formLogin) {
      formLogin.addEventListener('submit', function (event) {
          event.preventDefault();
          const nombreUsuario = document.getElementById('nombre-usuario').value;
          const contrasena = document.getElementById('contrasena').value;
          iniciarSesion(nombreUsuario, contrasena);
      });
  }

  if (formRegistro) {
      formRegistro.addEventListener('submit', function (event) {
          event.preventDefault();
          const nombreUsuario = document.getElementById('nombre-usuario').value;
          const contrasena = document.getElementById('contrasena').value;
          const imagenPerfil = document.getElementById('imagen-perfil').value;
          registrarUsuario(nombreUsuario, contrasena, imagenPerfil);
      });
  }
});

function iniciarSesion(nombreUsuario, contrasena) {
  fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          nombre_usuario: nombreUsuario,
          contrasena: contrasena
      })
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Error en la respuesta del servidor');
      }
      return response.json();
  })
  .then(data => {
      if (data.access_token) {
          localStorage.setItem('token', data.access_token);
          // Esperar un momento antes de redirigir
          setTimeout(() => {
              window.location.href = './resumen.html';
          }, 100);
      } else {
          alert('Error al iniciar sesión: No se recibió el token');
      }
  })
  .catch(error => {
      console.error('Error:', error);
      alert('Error al iniciar sesión: ' + error.message);
  });
}

function registrarUsuario(nombreUsuario, contrasena, imagenPerfil) {
  fetch(`${API_URL}/auth/registro`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          nombre_usuario: nombreUsuario,
          contrasena: contrasena,
          imagen_perfil: imagenPerfil
      })
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Error en la respuesta del servidor');
      }
      return response.json();
  })
  .then(data => {
      if (data.mensaje === 'Usuario registrado') {
          // Después de registrar, intentar iniciar sesión automáticamente
          iniciarSesion(nombreUsuario, contrasena);
      } else {
          alert('Error al registrar usuario: ' + (data.mensaje || 'Error desconocido'));
      }
  })
  .catch(error => {
      console.error('Error:', error);
      alert('Error al registrar usuario: ' + error.message);
  });
}

//  python3 -m http.server 3000