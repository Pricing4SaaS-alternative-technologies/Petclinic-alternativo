<template>
  <div class="vet-area">
    <div class="vet-card">
      <p class="message">Puedes gestionar las visitas desde aquí</p>
      <button class="btn-crear" @click="goToVisitas">Ir a Visitas</button>
    </div>
  </div>
</template>

<script>
import api from '@/api/axios'

export default {
  name: 'HomeVeterinario',
  data () {
    return {
      consultasHoy: 0,
      pacientes: 0,
      mensajesNuevos: 0,
      loading: false,
      error: ''
    }
  },
  created () {
    this.loadKpis()
    window.addEventListener('logout', this.loadKpis)
  },
  beforeUnmount () {
    window.removeEventListener('logout', this.loadKpis)
  },
  methods: {
    goToVisitas () {
      this.$router.push({ name: 'visitas' })
    },
    async loadKpis () {
      this.loading = true
      this.error = ''
      try {
        const rawUser = localStorage.getItem('user')
        if (!rawUser) {
          this.error = 'No autenticado'
          this.loading = false
          return
        }
        const user = JSON.parse(rawUser)
        const userId = user.id

        const { data } = await api.get(`visitas/veterinario/${userId}`)

        // consultas hoy
        const today = new Date().toDateString()
        const consultasHoy = data.filter(v => new Date(v.fecha).toDateString() === today).length

        // pacientes únicos en las visitas retornadas
        const uniqueMascotas = new Set(data.map(v => v.mascota_id || v.mascota_id === 0 ? v.mascota_id : v.mascota_nombre))
        const pacientes = uniqueMascotas.size

        // mensajes nuevos no disponible en API actual -> mostrar 0
        const mensajesNuevos = 0

        this.consultasHoy = consultasHoy
        this.pacientes = pacientes
        this.mensajesNuevos = mensajesNuevos
      } catch (e) {
        console.error('Error cargando KPIs', e)
        this.error = 'Error al cargar datos'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.vet-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}
.vet-card {
  background: #fff;
  box-shadow: 0 4px 16px rgba(44,62,80,0.08);
  border-radius: 18px;
  padding: 36px 32px;
  min-width: 340px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.message {
  font-size: 1.15rem;
  color: #2c3e50;
  margin-bottom: 24px;
}
.loading { color:#95a5a6 }
.error { color:#e74c3c }
.btn-crear {
  display: block;
  margin: 0.5rem auto 0;
  padding: 0.75rem 1.8rem;
  background: linear-gradient(135deg, #1e90ff 0%, #1c7ed6 100%);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(30, 144, 255, 0.3);
}
.btn-crear:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(30, 144, 255, 0.4);
  background: linear-gradient(135deg, #1c7ed6 0%, #155bc0 100%);
}
.btn-crear:active { transform: translateY(0); }
</style>
