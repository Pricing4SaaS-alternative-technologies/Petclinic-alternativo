<template>
  <nav class="navbar">
    <div class="nav-links">
      <router-link to="/" class="nav-logo-link">
        <img src="@/assets/logo.png" alt="Logo" class="nav-logo" style="height: 3rem; margin: 0 0.5rem;" />
      </router-link>
      <!-- Mostrar “Visitas” solo para veterinarios -->
      <router-link
        v-if="loggedIn && userTipo === 'veterinario'"
        to="/visitas"
        class="nav-link"
      >
        Visitas
      </router-link>
      <router-link
        v-if="loggedIn && userTipo === 'prop_mascota'"
        to="/mis-visitas"
        class="nav-link"
      >
        Mis visitas
      </router-link>
      <router-link
        v-if="loggedIn && userTipo==='prop_mascota'"
        to="/adopciones"
        class="nav-link"
      >
        Adopciones
      </router-link>
    </div>
    <div v-if="!loggedIn" class="nav-links-right" style="margin-right: 1rem;">
      <router-link to="/auth" class="nav-link">Login</router-link>
    </div>

    <!-- Muestra el nombre de usuario y el botón de logout si está logueado -->
    <div v-if="loggedIn" class="user-info">
      <span class="usuario">Hola, {{ usuarioActual.usuario }}</span>
      <span v-if="userTipo === 'prop_clinica' && has_plan" class="user-info">
        Plan: {{ plan }}
      </span>
      <span v-else-if="userTipo === 'prop_clinica' && !has_plan" class="user-info">
        Sin plan activo
      </span>
      <button class="logout" @click="logout">Cerrar sesión</button>
    </div>
  </nav>
</template>

<script>
import api from '../api/axios'

export default {
  name: 'Navbar',
  data () {
    // no llamar a getPlan aquí porque es async
    return {
      loggedIn: !!localStorage.getItem('jwt'), // Estado inicial basado en el token
      usuarioActual: this.getUsuarioActual(),
      userTipo: this.getUserTipo(),
      plan: '',
      has_plan: false
    }
  },
  methods: {
    getUsuarioActual () { // Sacamos el usuario completo, podemos explotarlo con todos sus atributos
      const user = localStorage.getItem('user')
      return user ? JSON.parse(user) : ''
    },
    getUserTipo () {
      const raw = localStorage.getItem('user')
      if (!raw) return ''
      const u = JSON.parse(raw)
      const tipo = u.tipo
      return tipo ? tipo.toLowerCase() : ''
    },
    async getPlan () {
      try {
        let plan = this.plan
        if (this.userTipo === 'prop_clinica') {
          plan = await api.get(`http://localhost:5000/api/contratos/getContract/${this.usuarioActual.id}`)
          console.log('Navbar - plan obtenido:', plan.data)
        } else {
          const clinica = ''// no implementado aun en backend
          plan = await api.get(`http://localhost:5000/api/contratos/getContract/${clinica.data.propietario_id}`) // obtenemos el plan de la clinica a la que pertenece el veterinario
        }
        if (plan.data !== '') {
          this.plan = plan.data.nombre_plan
          this.has_plan = true
        }
      } catch (err) {
        console.error('Error al obtener el plan:', err)
      }
    },
    logout () {
      // eliminamos tokens(el token de precios deberá ser eliminado tambien si esta)
      localStorage.removeItem('jwt')
      localStorage.removeItem('user')
      this.loggedIn = false
      this.usuarioActual = ''
      window.dispatchEvent(new Event('logout'))

      // nos cargamos el error de la consola de duplicateNav
      if (this.$route.path !== '/') {
        this.$router.push('/')
      }
    },
    // manejamos el inicio de sesión y cierre de sesión
    handleLogin () {
      this.loggedIn = true
      this.usuarioActual = this.getUsuarioActual()
      console.log('Usuario en localStorage:', localStorage.getItem('user'))
      this.userTipo = this.getUserTipo()
      this.getPlan() // generamos la información del plan
      console.log(this.userTipo)
    },
    handleLogout () {
      this.loggedIn = false
      this.usuarioActual = ''
      this.userTipo = ''
      this.has_plan = false
      this.plan = ''
    }
  },
  created () {
    window.addEventListener('login', this.handleLogin)
    window.addEventListener('logout', this.handleLogout)
    const user = localStorage.getItem('user')
    this.usuarioActual = user ? JSON.parse(user) : ''
    this.userTipo = this.getUserTipo()
    this.getPlan()// generamos la información del plan
  },
  beforeUnmount () {
    window.removeEventListener('login', this.handleLogin)
    window.removeEventListener('logout', this.handleLogout)
  }
}
</script>

<style scoped>
@import './css/Navbar.css';
</style>
