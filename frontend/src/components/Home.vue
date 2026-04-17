import { useRouter } from 'vue-router'

<template>
  <div>
    <div v-if="!jwtValido">
      <p class="error"> No estás logueado. Por favor, inicia sesión.</p>
    </div>
    <div v-else>
      <div class="welcome-banner">
        <div class="welcome-icon">👋</div>
        <h2 class="welcome-text">
          ¡Bienvenido, <span class="username">{{ info_usuario.usuario }}</span>!
        </h2>
      </div>
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
  color: #dc2626;
  font-weight: bold;
  padding: 1em;
  background-color: #fee2e2;
  border-radius: 8px;
  border-left: 4px solid #dc2626;
  margin: 2rem auto;
  max-width: 600px;
}

.welcome-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem 1rem 1.5rem;
  margin: 0 auto;
  max-width: 800px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.12);
  margin-bottom: 1.5rem;
  animation: slideDown 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.welcome-icon {
  font-size: 2.5rem;
  animation: wave 1.5s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(20deg); }
  75% { transform: rotate(-20deg); }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-text {
  color: #1f2937;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
}

.username {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
}

@media (max-width: 768px) {
  .welcome-banner {
    flex-direction: column;
    gap: 0.5rem;
    padding: 1.5rem 1rem;
  }

  .welcome-text {
    font-size: 1.5rem;
    text-align: center;
  }

  .welcome-icon {
    font-size: 2rem;
  }
}
</style>
