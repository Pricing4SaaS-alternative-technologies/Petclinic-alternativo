<template>
  <div class="navbar">
    <!-- Barra superior oscura -->
    <nav class="navbar-top">
      <div class="navbar-logo">
        <router-link to="/" class="nav-logo-link">
          <img src="@/assets/logo.png" alt="Logo" class="nav-logo" />
        </router-link>
      </div>
      <div v-if="!loggedIn" class="nav-links-right">
        <router-link to="/auth" class="nav-link">Login</router-link>
      </div>
      <!-- Muestra el nombre de usuario y el botón de logout si está logueado -->
      <div v-if="loggedIn" class="user-info">
        <span class="usuario">Hola, {{ usuarioActual.usuario }}</span>
        <span v-if="userTipo === 'prop_clinica' && has_plan" class="usuario">
          Plan: {{ contract_info.subscriptionPlans["PetClinic"] || contract_info.subscriptionPlans["petclinic"]}}
        </span>
        <span v-else-if="userTipo === 'prop_clinica' && !has_plan" class="usuario">
          Sin plan activo
        </span>
        <button class="logout" @click="logout">Cerrar sesión</button>
      </div>
    </nav>

    <!-- Columna lateral gris -->
    <div v-if="loggedIn" class="sidebar">
      <!-- Mostrar "Visitas" solo para veterinarios -->
      <router-link
        v-if="userTipo === 'veterinario'"
        to="/visitas"
        class="sidebar-link"
      >
        Visitas
      </router-link>
      <router-link
        v-if="userTipo === 'prop_mascota'"
        to="/mis-visitas"
        class="sidebar-link"
      >
        Vet visits
      </router-link>
      <router-link
        v-if="userTipo === 'prop_mascota'"
        to="/adopciones"
        class="sidebar-link"
      >
        Adoptions
      </router-link>
    </div>
  </div>
</template>

<script>

export default {
  name: 'Navbar',
  data () {
    return {
      loggedIn: !!localStorage.getItem('jwt'), // Estado inicial basado en el token
      usuarioActual: {},
      userTipo: '',
      contract_info: null,
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
        this.updateBodyClass(false)
        return
      }
      this.usuarioActual = JSON.parse(rawUser)
      this.userTipo = this.getUserTipo()
      if (parsedContrato !== null && parsedContrato !== '') {
        this.contract_info = parsedContrato
        this.has_plan = true
      }
      this.loggedIn = true
      this.updateBodyClass(true)
    },
    getUserTipo () {
      const rawUser = localStorage.getItem('user')
      if (!rawUser) return ''
      const u = JSON.parse(rawUser)
      const tipo = u.tipo
      return tipo ? tipo.toLowerCase() : ''
    },
    logout () {
      // eliminamos tokens(el token de precios deberá ser eliminado tambien si esta)
      localStorage.removeItem('jwt')
      localStorage.removeItem('user')
      localStorage.removeItem('contrato')
      window.dispatchEvent(new Event('logout'))

      // nos cargamos el error de la consola de duplicateNav
      if (this.$route.path !== '/') {
        this.$router.push('/')
      }
    },
    handleLogout () {
      this.loggedIn = false
      this.usuarioActual = {}
      this.userTipo = ''
      this.has_plan = false
      this.contract_info = null
      this.updateBodyClass(false)
    },
    updateBodyClass (showSidebar) {
      if (showSidebar) {
        document.body.classList.add('with-sidebar')
      } else {
        document.body.classList.remove('with-sidebar')
      }
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
