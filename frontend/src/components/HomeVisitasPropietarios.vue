<template>
  <div v-if="jwtValido" class="visitas-container">
    <h2>📋 Mis Visitas</h2>
    <ul v-if="visitas.length" class="visita-lista">
      <li v-for="v in visitas" :key="v.id" class="visita-card">
        <span>{{ formatearFecha(v.date_time) }}</span>
        <span>{{ v.mascota }}</span>
        <span>{{ v.description }}</span>
      </li>
    </ul>
    <p v-else class="no-visitas">No tienes visitas registradas.</p>
  </div>
  <p v-else class="error">No estás autorizado. Inicia sesión como propietario de mascota.</p>
</template>

<script>
import api from '@/api/axios'

export default {
  data () {
    return {
      jwtValido: false,
      info_usuario: null,
      visitas: []
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
      const raw = localStorage.getItem('user')
      if (!token || !raw) {
        this.jwtValido = false
        return
      }

      this.info_usuario = JSON.parse(raw)
      if (this.info_usuario.tipo !== 'prop_mascota') {
        this.jwtValido = false
        return
      }

      this.jwtValido = true
      this.fetchVisitas()
    },
    async fetchVisitas () {
      try {
        const { data } = await api.get(
          `/clinicas/${this.info_usuario.clinica_id}` +
          `/props_mascotas/mine/visitas`
        )
        this.visitas = data
      } catch (e) {
        console.error('No se pudieron cargar visitas:', e)
      }
    },
    formatearFecha (iso) {
      const [y, m, d] = iso.split('T')[0].split('-')
      return `${d}/${m}/${y}`
    }
  }
}
</script>

<style scoped>
@import './css/HomeVisitas.css';
</style>
