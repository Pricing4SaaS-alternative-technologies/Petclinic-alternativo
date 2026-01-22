<template>
  <div class="pet-hotel-container">
    <div class="hotel-header">
      <h1 class="hotel-title">Pet Hotel Rooms</h1>
      <p class="hotel-description">
        Deja a tu mascota bajo el mejor cuidado de nuestro personal dedicado en el hotel para mascotas.
      </p>
    </div>

    <div v-if="jwtValido">
      <h2 class="rooms-title">Todas las habitaciones</h2>

      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading rooms...</p>
      </div>

      <div v-else-if="habitaciones.length > 0" class="rooms-grid">
        <div v-for="habitacion in habitaciones" :key="habitacion.id" class="room-card">
          <div class="room-image-container">
            <img v-if="habitacion.url_imagen" :src="habitacion.url_imagen" :alt="habitacion.nombre" class="room-image" />
            <div v-else class="no-image-placeholder">
              <span>No Image</span>
            </div>
          </div>
          <div class="room-content">
            <h3 class="room-name">{{ habitacion.nombre }}</h3>
            <p class="room-perfect-for">Perfect for: {{ getPetType(habitacion.tipo.toUpperCase()) }}</p>
            <button class="see-details-btn" @click="$router.push(`/detalles-habitacion/${habitacion.id}`)">Ver detalles</button>
          </div>
        </div>
      </div>

      <div v-else class="no-rooms">
        <p>No hay habitaciones disponibles en este momento.</p>
      </div>
    </div>

    <div v-else class="no-auth">
      <p class="error">You are not authorized to view this information. Please log in.</p>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import api from '../api/axios'

export default {
  name: 'HotelRooms',

  data () {
    return {
      info_usuario: null,
      jwtValido: false,
      habitaciones: [],
      loading: false,
      error: ''
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
      const rawUser = localStorage.getItem('user')

      if (!token || !rawUser) {
        this.jwtValido = false
        return
      }

      try {
        this.info_usuario = JSON.parse(rawUser)
        this.jwtValido = true
        this.obtenerHabitaciones()
      } catch (e) {
        console.error('Error al parsear el usuario:', e)
        this.jwtValido = false
      }
    },

    async obtenerHabitaciones () {
      if (!this.jwtValido) return

      this.loading = true
      this.error = ''

      try {
        console.log('Usuario clinica ID:', this.info_usuario.clinica_id)
        const response = await api.get(`http://localhost:5000/api/habitaciones_hotel/listar/${this.info_usuario.clinica_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        console.log('Datos de habitaciones:', response.data)

        if (response.data) {
          this.habitaciones = response.data
        } else {
          this.error = 'No se recibieron datos de habitaciones'
        }
      } catch (error) {
        console.error('Error al obtener habitaciones:', error)
        this.error = 'Error al cargar las habitaciones. Por favor, intenta nuevamente.'
      } finally {
        this.loading = false
      }
    },

    getPetType (roomType) {
      const petTypeMap = {
        'gato': 'Gatos',
        'perro': 'Perros',
        'reptil': 'Reptiles',
        'pájaro': 'Pájaros',
        'HAMSTER': 'Hamsters',
        'tortuga': 'Tortugas'
      }
      return petTypeMap[roomType] || 'Cualquier tipo de mascota'
    }
  }
}
</script>

<style scoped src="./css/HotelRooms.css"></style>
