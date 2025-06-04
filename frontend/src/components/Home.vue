import { useRouter } from 'vue-router'

<template>
  <div>
    <div v-if="!jwtValido">
      <p class="error"> No estás logueado. Por favor, inicia sesión.</p>
    </div>
    <div v-else>
      <h2>Bienvenido {{ info_usuario.usuario }}</h2>
      <component :is="componenteRol" />
    </div>
  </div>
</template>

<script>
import HomeMascota from './HomeMascota.vue'
import HomeClinica from './HomeClinica.vue'
import HomeVeterinario from './HomeVeterinario.vue'
import HomeAdmin from './HomeAdmin.vue'

export default {
  components: {
    HomeMascota,
    HomeClinica,
    HomeVeterinario,
    HomeAdmin
  },
  data () {
    return {
      info_usuario: null,
      jwtValido: false,
      componenteRol: null
    }
  },
  created () {
    this.checkAuth()
    window.addEventListener('logout', this.checkAuth)
  },
  beforeUnmount () {
    window.removeEventListener('logout', this.checkAuth)
  },
  methods: {
    checkAuth () {
      const token = localStorage.getItem('jwt')
      // user tiene tipo, usuario, email e id como campos que se guardan
      const rawUser = localStorage.getItem('user')

      // Verificamos si hay token y usuario
      if (!token || !rawUser) {
        this.jwtValido = false
        return
      }

      try {
        this.info_usuario = JSON.parse(rawUser)
        this.jwtValido = true
        this.asignarComponentePorRol(this.info_usuario.tipo)
      } catch (e) {
        console.error('Error al parsear el usuario:', e)
        this.jwtValido = false
      }
    },
    asignarComponentePorRol (tipo) {
      switch (tipo) {
        case 'prop_mascota':
          this.componenteRol = HomeMascota
          break
        case 'prop_clinica':
          this.componenteRol = HomeClinica
          break
        case 'veterinario':
          this.componenteRol = HomeVeterinario
          break
        case 'admin':
          this.componenteRol = HomeAdmin // Asignar un componente por defecto para ADMIN
          break
        default:
          this.componenteRol = null
      }
    }
  }
}
</script>

<style scoped>
.error {
  color: red;
  font-weight: bold;
  padding: 1em;
}
</style>
