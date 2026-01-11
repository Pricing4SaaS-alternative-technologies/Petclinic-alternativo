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

export default {
  name: 'Navbar',
  data () {
    // no llamar a getPlan aquí porque es async
    return {
      loggedIn: !!localStorage.getItem('jwt'), // Estado inicial basado en el token
      usuarioActual: '',
      userTipo: '',
      plan: null,
      has_plan: false
    }
  },
  methods: {

    checkAuth () {
      const token = localStorage.getItem('jwt')
      const rawUser = localStorage.getItem('user')
      const rawContrato = localStorage.getItem('contrato')
      const parsedContrato = rawContrato ? JSON.parse(rawContrato) : null
      if (!token || !rawUser) {
        this.loggedIn = false
        return
      }
      this.usuarioActual = JSON.parse(rawUser)
      this.userTipo = this.getUserTipo()
      if (parsedContrato !== null && parsedContrato !== '') {
        this.plan = parsedContrato
        this.has_plan = true
      }
      this.loggedIn = true
    },
    getUserTipo () {
      const raw = localStorage.getItem('user')
      if (!raw) return ''
      const u = JSON.parse(raw)
      const tipo = u.tipo
      return tipo ? tipo.toLowerCase() : ''
    },
    logout () {
      // eliminamos tokens(el token de precios deberá ser eliminado tambien si esta)
      localStorage.removeItem('jwt')
      localStorage.removeItem('user')
      localStorage.removeItem('contrato')
      // this.loggedIn = false
      // this.usuarioActual = ''
      window.dispatchEvent(new Event('logout'))

      // nos cargamos el error de la consola de duplicateNav
      if (this.$route.path !== '/') {
        this.$router.push('/')
      }
    },
    // manejamos el inicio de sesión y cierre de sesión
    handleLogout () {
      this.loggedIn = false
      this.usuarioActual = ''
      this.userTipo = ''
      this.has_plan = false
      this.plan = null
    }
  },
  created () {
    this.checkAuth()
    window.addEventListener('login', this.checkAuth)
    window.addEventListener('logout', this.handleLogout)
  },
  beforeUnmount () {
    window.removeEventListener('login', this.checkAuth)
    window.removeEventListener('logout', this.handleLogout)
  }
}
</script>

<style scoped>
@import './css/Navbar.css';
</style>
