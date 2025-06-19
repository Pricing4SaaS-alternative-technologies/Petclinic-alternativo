<template>
  <nav class="navbar">
    <div class="nav-links">
      <router-link to="/" class="nav-logo-link">
        <img src="@/assets/logo.png" alt="Logo" class="nav-logo" style="height: 3rem; margin: 0 0.5rem;" />
      </router-link>
      <!-- Mostrar “Visitas” solo para veterinarios -->
      <router-link
        v-if="loggedIn && userTipo === 'prop_clinica'"
        to="/visitas"
        class="nav-link"
      >
        Visitas
      </router-link>
    </div>
    <div v-if="!loggedIn" class="nav-links-right" style="margin-right: 1rem;">
      <router-link to="/auth" class="nav-link">Login</router-link>
    </div>

    <!-- Muestra el nombre de usuario y el botón de logout si está logueado -->
    <div v-if="loggedIn" class="user-info">
      <span class="usuario">Hola, {{ usuarioActual }}</span>
      <button class="logout" @click="logout">Cerrar sesión</button>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navbar',
  data () {
    return {
      loggedIn: !!localStorage.getItem('jwt'), // Estado inicial basado en el token
      usuarioActual: this.getUsuarioActual(),
      userTipo: this.getUserTipo()
    }
  },
  methods: {
    getUsuarioActual () { // Con esto sacas el username. Si pones en vez de .usuario y pones otro atributo, te lo devuelve
      const user = localStorage.getItem('user')
      return user ? JSON.parse(user).usuario : ''
    },
    getUserTipo () {
      const raw = localStorage.getItem('user')
      if (!raw) return ''
      const u = JSON.parse(raw)
      const tipo = u.tipo
      return tipo ? tipo.toLowerCase() : ''
    },
    logout () {
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
      const user = localStorage.getItem('user')
      this.usuarioActual = user ? JSON.parse(user).usuario : ''
      this.userTipo = this.getUserTipo()
      const tipo = user ? JSON.parse(user).tipo : ''
      console.log(tipo)
    },
    handleLogout () {
      this.loggedIn = false
      this.usuarioActual = ''
      this.userTipo = ''
    }
  },
  created () {
    window.addEventListener('login', this.handleLogin)
    window.addEventListener('logout', this.handleLogout)
    const user = localStorage.getItem('user')
    this.usuarioActual = user ? JSON.parse(user).usuario : ''
    this.userTipo = this.getUserTipo()
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
