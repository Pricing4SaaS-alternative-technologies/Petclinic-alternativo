<template>
    <div class="auth-container">
      <div class="auth-toggle">
        <button @click="mode = 'login'" :class="{ active: mode === 'login' }">Login</button>
        <button @click="mode = 'register'" :class="{ active: mode === 'register' }">Register</button>
      </div>

      <!-- Formulario de Login -->
      <div v-if="mode === 'login'" class="login-form">
        <h2>Login</h2>
        <form @submit.prevent="login">
          <div>
            <label for="username_or_email">Username or Email</label>
            <input type="text" id="username_or_email" v-model="loginForm.username_or_email" required />
          </div>
          <div>
            <label for="login-password">Password</label>
            <input type="password" id="login-password" v-model="loginForm.password" required />
          </div>
          <button type="submit">Login</button>
        </form>
        <p v-if="loginError" class="error">{{ loginError }}</p>
      </div>

      <!-- Formulario de Registro -->
      <div v-if="mode === 'register'" class="register-form">
        <h2>Register</h2>
        <form @submit.prevent="register">
          <div>
            <label for="username">Username</label>
            <input type="text" id="username" v-model="registerForm.username" required />
          </div>
          <div>
            <label for="email">Email</label>
            <input type="email" id="email" v-model="registerForm.email" required />
          </div>
          <div>
            <label for="register-password">Password</label>
            <input type="password" id="register-password" v-model="registerForm.password" required />
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
      mode: 'login', // modo inicial de la pagina, en este caso login
      loginForm: {
        username_or_email: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: ''
      },
      loginError: '',
      registerError: ''
    }
  },
  methods: {
    async login () {
      this.loginError = ''
      try {
        const response = await axios.post('http://localhost:5000/api/auth/login', this.loginForm)
        console.log('Login success:', response.data)
        // Guarda el token JWT en localStorage (o sessionStorage, según prefieras)
        localStorage.setItem('jwt', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        window.dispatchEvent(new Event('login'))
        this.$router.push('/')
        // Aquí podrías redirigir o actualizar el estado de la aplicación
      } catch (error) {
        console.error('Login error:', error.response.data)
        this.loginError = error.response.data.message || 'Login failed'
      }
    },
    async register () {
      this.registerError = ''
      try {
        const response = await axios.post('http://localhost:5000/api/auth/register', this.registerForm)
        console.log('Registration success:', response.data)
        // Opcional: Cambia a modo login después de registrarte
        this.mode = 'login'
      } catch (error) {
        console.error('Registration error:', error.response.data)
        this.registerError = error.response.data.message || 'Registration-failed'
      }
    }
  }
}
</script>

  <style scoped>
  .auth-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
  }

  .auth-toggle {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;
  }

  .auth-toggle button {
    flex: 1;
    padding: 10px;
    margin: 0 5px;
    cursor: pointer;
  }

  .auth-toggle button.active {
    font-weight: bold;
    background-color: #007bff;
    color: white;
  }

  form div {
    margin-bottom: 10px;
  }

  label {
    display: block;
    margin-bottom: 5px;
  }

  input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
  }

  .error {
    color: red;
  }
  </style>
