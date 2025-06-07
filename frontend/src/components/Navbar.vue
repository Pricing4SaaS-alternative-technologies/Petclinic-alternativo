<template>
  <nav class="navbar">
    <div class="nav-links">
      <router-link to="/" class="nav-logo-link">
        <img src="@/assets/logo.png" alt="Logo" class="nav-logo" style="height: 3rem; margin: 0 0.5rem;" />
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
      usuarioActual: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).usuario : ''
    }
  },
  methods: {
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
      const user = localStorage.getItem('user')
      this.usuarioActual = user ? JSON.parse(user).usuario : ''
    },
    handleLogout () {
      this.loggedIn = false
      this.usuarioActual = ''
    }
  },
  created () {
    window.addEventListener('login', this.handleLogin)
    window.addEventListener('logout', this.handleLogout)
    console.log('Usuario en localStorage:', localStorage.getItem('user'))
    const user = localStorage.getItem('user')
    this.usuarioActual = user ? JSON.parse(user).usuario : ''
  },
  beforeUnmount () {
    window.removeEventListener('login', this.handleLogin)
    window.removeEventListener('logout', this.handleLogout)
  }
}
</script>

<style scoped>
.navbar {
  background-color: #333;
  height: 5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  margin: 0;
  width: 100%;
  box-sizing: border-box;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  margin-left: 1rem;
}

.nav-link:hover {
  text-decoration: underline;
}

.user-info {
  display: flex;
  align-items: center;
}

.usuario {
  color: white;
  margin-right: 1rem;
  font-size: 1rem;
}

.logout {
  color: rgb(255, 0, 0);
  background-color: transparent;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  margin-right: 1rem;
}

.logout:hover {
  text-decoration: underline;
}
</style>
