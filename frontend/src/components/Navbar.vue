<template>
  <div class="navbar">
    <nav class="navbar-top">
      <div class="navbar-logo">
        <router-link to="/" class="nav-logo-link">
          <img :src="logo" alt="Logo" class="nav-logo" />
        </router-link>
      </div>
      <div v-if="!loggedIn" class="nav-links-right">
        <router-link to="/auth" class="nav-link">Login</router-link>
      </div>
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

    <div v-if="loggedIn" class="sidebar">
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
        Visitas
      </router-link>

      <Feature id="petclinic-visitCalendar" v-if="userTipo === 'prop_mascota'">
        <template #on>
          <router-link
            v-if="loggedIn && userTipo === 'prop_mascota'"
            to="/calendario-visitas"
            class="sidebar-link"
          >
            Calendario de visitas
          </router-link>
        </template>
      </Feature>

      <router-link
        v-if="loggedIn && userTipo==='prop_mascota'"
        to="/adopciones"
        class="sidebar-link"
      >
        Adopciones
      </router-link>
    <Feature id="petclinic-petHotelManagement">
      <template #on>
        <router-link
          v-if="loggedIn && userTipo==='prop_mascota' || userTipo === 'prop_clinica'"
          to="/habitaciones-hotel"
          class="sidebar-link"
        >
          Habitaciones hotel
        </router-link>
      </template>
    </Feature>
    </div>
  </div>
</template>

<script>
import logoImg from '@/assets/logo.png'
import { syncSpaceToken } from '@/utils/spaceSync'
import { Feature } from '@npm_team/space-vue-client'

export default {
  name: 'Navbar',
  components: {
    Feature
  },
  data () {
    return {
      loggedIn: !!localStorage.getItem('jwt'),
      usuarioActual: {},
      userTipo: '',
      contract_info: null,
      has_plan: false,
      logo: logoImg
    }
  },
  methods: {
    async checkAuth () {
      const token = localStorage.getItem('jwt')
      const rawUser = localStorage.getItem('user')
      const rawContrato = localStorage.getItem('contrato')
      const parsedContrato = rawContrato ? JSON.parse(rawContrato) : null

      // 1. Añadimos la lectura del token de precios
      const pricingToken = localStorage.getItem('pricing_token')

      if (!token || !rawUser) {
        this.loggedIn = false
        this.updateBodyClass(false)
        return
      }
      this.usuarioActual = JSON.parse(rawUser)
      this.userTipo = this.getUserTipo()

      if (parsedContrato !== null && parsedContrato !== '' && this.userTipo !== 'veterinario') {
        this.contract_info = parsedContrato
        this.has_plan = true
      }

      this.loggedIn = true
      this.updateBodyClass(true)
      if (this.userTipo !== 'veterinario') {
        await syncSpaceToken(this.$router)
      }

      // 2. Le inyectamos el token a tu librería usando el método update()
      if (pricingToken && this.$tokenService) {
        this.$tokenService.update(pricingToken)
      }
    },

    getUserTipo () {
      const rawUser = localStorage.getItem('user')
      if (!rawUser) return ''
      const u = JSON.parse(rawUser)
      const tipo = u.tipo
      return tipo ? tipo.toLowerCase() : ''
    },

    logout () {
      localStorage.removeItem('jwt')
      localStorage.removeItem('user')
      localStorage.removeItem('contrato')
      localStorage.removeItem('pricing_token')

      // 3. Limpiamos el token de la librería al cerrar sesión
      if (this.$tokenService && typeof this.$tokenService.clear === 'function') {
        this.$tokenService.clear()
      }

      window.dispatchEvent(new Event('logout'))

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
  async created () {
    await this.checkAuth()
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
