<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-toggle">
      <button @click="mode = 'login'" :class="{ active: mode === 'login' }">Iniciar Sesión</button>
      <button @click="mode = 'register'" :class="{ active: mode === 'register' }">Registrarse</button>
    </div>

    <!-- Login -->
    <div v-if="mode === 'login'" class="login-form">
      <h2><i class="fa-solid fa-sign-in-alt"></i> Iniciar Sesión</h2>
      <form @submit.prevent="login">
        <div>
          <label for="usuario_o_email">Usuario o Email</label>
          <input type="text" id="usuario_o_email" v-model="loginForm.usuario_o_email" placeholder="ejemplo@email.com" required />
        </div>
        <div class="password-wrapper">
          <label for="contraseña-login">Contraseña</label>
          <div class="input-icon-wrapper">
            <input :type="showPassword ? 'text' : 'password'" id="contraseña-login" v-model="loginForm.contraseña" placeholder="Ingresa tu contraseña" required />
            <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'" @click="showPassword = !showPassword" class="password-toggle-icon"></i>
          </div>
        </div>
        <button type="submit"><i class="fa-solid fa-sign-in-alt"></i> Ingresar</button>
      </form>
      <p v-if="loginError" class="error"><i class="fa-solid fa-circle-exclamation"></i> {{ loginError }}</p>
    </div>

    <!-- Registro -->
    <div v-if="mode === 'register'" class="register-form">
      <h2><i class="fa-solid fa-user-plus"></i> Crear Cuenta</h2>
      <form @submit.prevent="register">
        <div>
          <label for="tipo_usuario"><i class="fa-solid fa-list"></i> Tipo de Usuario</label>
          <select v-model="registerForm.tipo_usuario" required>
            <option disabled value="">Selecciona un tipo</option>
            <option value="PROP_MASCOTA">🐾 Dueño de Mascota</option>
            <option value="VETERINARIO">🩺 Veterinario</option>
            <option value="PROP_CLINICA">🏥 Dueño de Clínica</option>
          </select>
        </div>
        <div>
          <label for="nombre"><i class="fa-solid fa-user"></i> Nombre</label>
          <input type="text" id="nombre" v-model="registerForm.nombre" placeholder="Tu nombre" required />
        </div>
        <div>
          <label for="apellidos"><i class="fa-solid fa-user"></i> Apellido</label>
          <input type="text" id="apellidos" v-model="registerForm.apellidos" placeholder="Tu apellido" required />
        </div>
        <div>
          <label for="usuario"><i class="fa-solid fa-at"></i> Username</label>
          <input type="text" id="usuario" v-model="registerForm.usuario" placeholder="nombre_de_usuario" required />
        </div>
        <div>
          <label for="email"><i class="fa-solid fa-envelope"></i> Email</label>
          <input type="email" id="email" v-model="registerForm.email" placeholder="ejemplo@email.com" required />
        </div>
        <div class="password-wrapper">
          <label for="contraseña-registro"><i class="fa-solid fa-lock"></i> Contraseña</label>
          <div class="input-icon-wrapper">
            <input :type="showPassword ? 'text' : 'password'" id="contraseña-registro" v-model="registerForm.contraseña" placeholder="Mínimo 8 caracteres" required />
            <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'" @click="showPassword = !showPassword" class="password-toggle-icon"></i>
          </div>
        </div>

        <!-- PROP_MASCOTA -->
        <div v-if="registerForm.tipo_usuario === 'PROP_MASCOTA'">
          <div>
            <label for="direccion"><i class="fa-solid fa-map-marker-alt"></i> Dirección</label>
            <input type="text" id="direccion" v-model="registerForm.direccion" placeholder="Tu dirección" required />
          </div>
          <div>
            <label for="telefono"><i class="fa-solid fa-phone"></i> Teléfono</label>
            <input type="text" id="telefono" v-model="registerForm.telefono" placeholder="Tu número de teléfono" required />
          </div>
          <div>
            <label for="clinica_id"><i class="fa-solid fa-hospital-user"></i> Clínica</label>
            <select v-model="registerForm.clinica_id" required>
              <option disabled value="">Selecciona una clínica</option>
              <option v-for="clinica in clinicasDisponibles" :key="clinica.id" :value="clinica.id">
                {{ clinica.nombre }}
              </option>
            </select>
          </div>
        </div>

        <!-- PROP_CLINICA -->
        <div v-if="registerForm.tipo_usuario === 'PROP_CLINICA'">
          <div>
            <label for="telefono"><i class="fa-solid fa-phone"></i> Teléfono</label>
            <input type="text" id="telefono" v-model="registerForm.telefono" placeholder="Teléfono de la clínica" required />
          </div>
        </div>

        <!-- VETERINARIO -->
        <div v-if="registerForm.tipo_usuario === 'VETERINARIO'">
          <div>
            <label for="ciudad"><i class="fa-solid fa-city"></i> Ciudad</label>
            <input type="text" id="ciudad" v-model="registerForm.ciudad" placeholder="Tu ciudad" required />
          </div>
          <div>
            <label for="especialidades"><i class="fa-solid fa-stethoscope"></i> Especialidades</label>
            <select id="especialidades" v-model="registerForm.especialidades" multiple required>
              <option v-for="esp in especialidadesDisponibles" :key="esp" :value="esp">
                {{ esp }}
              </option>
            </select>
          </div>
          <div>
            <label for="clinica_id"><i class="fa-solid fa-hospital-user"></i> Clínica</label>
            <select v-model="registerForm.clinica_id" required>
              <option disabled value="">Selecciona una clínica</option>
              <option v-for="clinica in clinicasDisponibles" :key="clinica.id" :value="clinica.id">
                {{ clinica.nombre }}
              </option>
            </select>
          </div>
        </div>

        <button type="submit"><i class="fa-solid fa-user-plus"></i> Registrarse</button>
      </form>
      <p v-if="registerError" class="error"><i class="fa-solid fa-circle-exclamation"></i> {{ registerError }}</p>
    </div>
    </div>
  </div>
</template>

<script>
import api from '../api/axios'

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
        const res = await api.get('http://localhost:5000/api/auth/especialidades')
        this.especialidadesDisponibles = res.data
      } catch (err) {
        console.error('Error al cargar especialidades', err)
      }
    },
    async fetchClinicas () {
      try {
        const res = await api.get('http://localhost:5000/api/clinicas/listar-todas')
        // TODO: Añadir filtro para detectar clinicas que no peuden tener usuarios nuevos
        this.clinicasDisponibles = res.data
      } catch (err) {
        console.error('Error al cargar clínicas', err)
      }
    },
    async login () {
      this.loginError = ''
      try {
        const response = await api.post('http://localhost:5000/api/auth/login', this.loginForm)
        console.log('Login successful', response.data.contrato)
        localStorage.setItem('jwt', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.usuario))
        localStorage.setItem('contrato', JSON.stringify(response.data.contrato))
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
        const response = await api.post('http://localhost:5000/api/auth/register', payload)
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
@import './css/AuthPage.css';
</style>
