<template>
  <div class="auth-container">
    <div class="auth-toggle">
      <button @click="mode = 'login'" :class="{ active: mode === 'login' }">Login</button>
      <button @click="mode = 'register'" :class="{ active: mode === 'register' }">Register</button>
    </div>

    <!-- Login -->
    <div v-if="mode === 'login'" class="login-form">
      <h2>Login</h2>
      <form @submit.prevent="login">
        <div>
          <label for="usuario_o_email">Usuario o Email</label>
          <input type="text" id="usuario_o_email" v-model="loginForm.usuario_o_email" required />
        </div>
        <div class="password-wrapper">
          <label for="contraseña-login">Contraseña</label>
          <div class="input-icon-wrapper">
            <input :type="showPassword ? 'text' : 'password'" id="contraseña-login" v-model="loginForm.contraseña" required />
            <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'" @click="showPassword = !showPassword" class="password-toggle-icon"></i>
          </div>
        </div>
        <button type="submit">Login</button>
      </form>
      <p v-if="loginError" class="error">{{ loginError }}</p>
    </div>

    <!-- Registro -->
    <div v-if="mode === 'register'" class="register-form">
      <h2>Register</h2>
      <form @submit.prevent="register">
        <div>
          <label for="tipo_usuario">Tipo de Usuario</label>
          <select v-model="registerForm.tipo_usuario" required>
            <option disabled value="">Selecciona un tipo</option>
            <option value="PROP_MASCOTA">Dueño de Mascota</option>
            <option value="VETERINARIO">Veterinario</option>
            <option value="PROP_CLINICA">Dueño de Clínica</option>
          </select>
        </div>
        <div>
          <label for="nombre">Nombre</label>
          <input type="text" id="nombre" v-model="registerForm.nombre" required />
        </div>
        <div>
          <label for="apellidos">Apellido</label>
          <input type="text" id="apellidos" v-model="registerForm.apellidos" required />
        </div>
        <div>
          <label for="usuario">Username</label>
          <input type="text" id="usuario" v-model="registerForm.usuario" required />
        </div>
        <div>
          <label for="email">Email</label>
          <input type="email" id="email" v-model="registerForm.email" required />
        </div>
        <div class="password-wrapper">
          <label for="contraseña-registro">Contraseña</label>
          <div class="input-icon-wrapper">
            <input :type="showPassword ? 'text' : 'password'" id="contraseña-registro" v-model="registerForm.contraseña" required />
            <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'" @click="showPassword = !showPassword" class="password-toggle-icon"></i>
          </div>
        </div>

        <!-- PROP_MASCOTA -->
        <div v-if="registerForm.tipo_usuario === 'PROP_MASCOTA'">
          <div>
            <label for="direccion">Dirección</label>
            <input type="text" id="direccion" v-model="registerForm.direccion" required />
          </div>
          <div>
            <label for="telefono">Teléfono</label>
            <input type="text" id="telefono" v-model="registerForm.telefono" required />
          </div>
          <div>
            <label for="clinica_id">Clínica</label>
            <select v-model="registerForm.clinica_id" required>
              <option disabled value="">Selecciona una clínica</option>
              <option v-for="clinica in clinicasDisponibles" :key="clinica.id" :value="clinica.id">
                {{ clinica.nombre }}
              </option>
            </select>
          </div>
        </div>

        <!-- VETERINARIO -->
        <div v-if="registerForm.tipo_usuario === 'VETERINARIO'">
          <div>
            <label for="ciudad">Ciudad</label>
            <input type="text" id="ciudad" v-model="registerForm.ciudad" required />
          </div>
          <div>
            <label for="especialidades">Especialidades</label>
            <select id="especialidades" v-model="registerForm.especialidades" multiple required>
              <option v-for="esp in especialidadesDisponibles" :key="esp" :value="esp">
                {{ esp }}
              </option>
            </select>
          </div>
          <div>
            <label for="clinica_id">Clínica</label>
            <select v-model="registerForm.clinica_id" required>
              <option disabled value="">Selecciona una clínica</option>
              <option v-for="clinica in clinicasDisponibles" :key="clinica.id" :value="clinica.id">
                {{ clinica.nombre }}
              </option>
            </select>
          </div>
        </div>

        <button type="submit">Register</button>
      </form>
      <p v-if="registerError" class="error">{{ registerError }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AuthPage',
  data () {
    return {
      mode: 'login',
      showPassword: false,
      loginForm: {
        usuario_o_email: '',
        contraseña: ''
      },
      registerForm: {
        tipo_usuario: '',
        nombre: '',
        apellidos: '',
        usuario: '',
        email: '',
        contraseña: '',
        direccion: '',
        telefono: '',
        ciudad: '',
        clinica_id: '',
        especialidades: []
      },
      especialidadesDisponibles: [],
      clinicasDisponibles: [],
      loginError: '',
      registerError: ''
    }
  },
  created () {
    this.fetchEspecialidades()
    this.fetchClinicas()
  },
  methods: {
    async fetchEspecialidades () {
      try {
        const res = await axios.get('http://localhost:5000/api/auth/especialidades')
        this.especialidadesDisponibles = res.data
      } catch (err) {
        console.error('Error al cargar especialidades', err)
      }
    },
    async fetchClinicas () {
      try {
        const res = await axios.get('http://localhost:5000/api/clinicas/listar-todas')
        this.clinicasDisponibles = res.data
      } catch (err) {
        console.error('Error al cargar clínicas', err)
      }
    },
    async login () {
      this.loginError = ''
      try {
        const response = await axios.post('http://localhost:5000/api/auth/login', this.loginForm)
        localStorage.setItem('jwt', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.usuario))
        window.dispatchEvent(new Event('login'))
        this.$router.push('/')
      } catch (error) {
        this.loginError = (error.response && error.response.data && error.response.data.message) || 'Login failed'
      }
    },
    async register () {
      this.registerError = ''
      try {
        const payload = { ...this.registerForm }
        const response = await axios.post('http://localhost:5000/api/auth/register', payload)
        console.log('Registro correcto', response.data)
        this.mode = 'login'
      } catch (error) {
        this.registerError = (error.response && error.response.data && error.response.data.message) || 'Registro fallido'
      }
    }
  }
}
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.auth-toggle {
  display: flex;
  justify-content: space-between;
  margin-bottom: 25px;
}

.auth-toggle button {
  flex: 1;
  padding: 12px;
  margin: 0 4px;
  border-radius: 8px;
  border: none;
  background-color: #f0f0f0;
  font-weight: 500;
  cursor: pointer;
}

.auth-toggle button.active {
  background-color: #007bff;
  color: #fff;
  font-weight: bold;
  box-shadow: 0 4px 10px rgba(0, 123, 255, 0.3);
}

form div {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #333;
}

input, select {
  width: 90%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  transition: border-color 0.3s;
}

input:focus, select:focus {
  border-color: #007bff;
  outline: none;
}

button[type="submit"] {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

button[type="submit"]:hover {
  background-color: #0056b3;
}

.error {
  color: red;
  font-size: 0.9em;
  margin-top: 10px;
  text-align: center;
}

.input-icon-wrapper {
  position: relative;
  width: 100%;
}

.password-toggle-icon {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  cursor: pointer;
  color: #666;
  font-size: 1rem;
}
</style>
