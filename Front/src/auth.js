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
  fetch('https://backend-622667124527.us-central1.run.app/login', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          nombre_usuario: nombreUsuario,
          contrasena: contrasena
      })
  })
  .then(response => response.json())
  .then(data => {
      if (data.access_token) {
          localStorage.setItem('token', data.access_token);
          window.location.href = '/resumen.html';
      } else {
          alert('Error al iniciar sesión');
      }
  })
  .catch(error => console.error('Error:', error));
}

function registrarUsuario(nombreUsuario, contrasena, imagenPerfil) {
  fetch('https://backend-622667124527.us-central1.run.app/registro', {
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
  .then(response => response.json())
  .then(data => {
      if (data.mensaje === 'Usuario registrado') {
          window.location.href = '/resumen.html';
      } else {
          alert('Error al registrar usuario');
      }
  })
  .catch(error => console.error('Error:', error));
}



//  python3 -m http.server 3000