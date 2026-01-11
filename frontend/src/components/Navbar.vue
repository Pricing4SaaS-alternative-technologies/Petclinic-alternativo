<template>
  <div class="navbar-container">
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
        <span class="usuario">Hola, {{ usuarioActual }}</span>
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
        v-if="userTipo==='prop_mascota'"
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
