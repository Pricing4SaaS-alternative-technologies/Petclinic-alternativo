<template>
  <div class="reservas-container">
    <div class="reservas-header">
      <h1 class="reservas-title">Mis Reservas</h1>
      <button class="back-btn" @click="$router.go(-1)">
        <i class="fas fa-arrow-left"></i> Volver
      </button>
    </div>

    <div v-if="jwtValido">
      <div v-if="loading || cargandoReservas" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Cargando reservas...</p>
      </div>

      <div v-else-if="habitacionesReservadas.length > 0" class="rooms-grid">
        <div v-for="habitacion in habitacionesReservadas" :key="habitacion.id" class="room-card">
          <div class="room-image-container">
            <img v-if="habitacion.url_imagen" :src="habitacion.url_imagen" :alt="habitacion.nombre" class="room-image" />
            <div v-else class="no-image-placeholder">
              <span>No Image</span>
            </div>
            <div class="reserved-badge">RESERVADA</div>
          </div>
          <div class="room-content">
            <h3 class="room-name">{{ habitacion.nombre }}</h3>

            <!-- Sección de fechas de reserva -->
            <div v-if="habitacion.reservas && habitacion.reservas.length > 0" class="reservas-dates">
              <h4 class="reservas-subtitle">Fechas reservadas:</h4>
              <div v-for="(reserva, index) in habitacion.reservas" :key="index" class="reserva-item">
                <div class="reserva-date-range">
                  <i class="fas fa-calendar-alt"></i>
                  {{ formatearFecha(reserva.fecha_inicio) }} - {{ formatearFecha(reserva.fecha_fin) }}
                </div>
                <div class="reserva-status" :class="{
                  'status-active': reserva.estado === 'activa',
                  'status-pending': reserva.estado === 'pendiente',
                  'status-completed': reserva.estado === 'completada'
                }">
                  {{ reserva.estado }}
                </div>
              </div>
            </div>

            <div v-else class="no-reservas-dates">
              <p class="no-dates-text">No hay fechas de reserva disponibles</p>
            </div>

            <div class="room-details">
              <span class="room-detail"><i class="fas fa-paw"></i> Tipo: {{ habitacion.tipo }}</span>
              <span class="room-detail"><i class="fas fa-expand-arrows-alt"></i> Tamaño: {{ habitacion.tamaño }}</span>
            </div>
            <div class="room-actions">
              <!-- Aquí podrías agregar botones de acción si los necesitas -->
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-reservas">
        <div class="empty-state">
          <i class="fas fa-bed empty-icon"></i>
          <h3>No tienes reservas activas</h3>
          <p>¡Explora nuestras habitaciones y reserva para tu mascota!</p>
          <button class="explore-btn" @click="$router.push('/habitaciones-hotel')">
            <i class="fas fa-search"></i> Ver habitaciones disponibles
          </button>
        </div>
      </div>
    </div>

    <div v-else class="no-auth">
      <div class="auth-error">
        <i class="fas fa-exclamation-triangle"></i>
        <p class="error">No estás autorizado para ver esta información. Por favor, inicia sesión.</p>
        <button class="login-btn" @click="$router.push('/login')">
          <i class="fas fa-sign-in-alt"></i> Iniciar sesión
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      {{ error }}
    </div>
  </div>
</template>

<script>
import api from '../api/axios'
import axios from 'axios'

export default {
  name: 'MisReservas',

  data () {
    return {
      info_usuario: null,
      jwtValido: false,
      habitacionesReservadas: [],
      reservas: [],
      todasLasMascotas: [],
      mascotaSeleccionada: 'todas',
      loading: false,
      cargandoReservas: false,
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
        this.$router.push('/login')
        return
      }

      try {
        this.info_usuario = JSON.parse(rawUser)
        this.jwtValido = true
        this.obtenerMiHabsReservadas()
        this.obtenerMascotas()
        this.obtenerMisReservas()
      } catch (e) {
        console.error('Error al parsear el usuario:', e)
        this.jwtValido = false
      }
    },

    async obtenerMiHabsReservadas () {
      if (!this.jwtValido) return

      this.loading = true
      this.error = ''

      try {
        const params = {}
        if (this.mascotaSeleccionada !== 'todas') {
          params.mascota_id = parseInt(this.mascotaSeleccionada)
        }

        console.log('Enviando parámetros:', params)

        const response = await api.get('http://localhost:5000/api/reservas/mis_habs_reservas', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt')}`
          },
          params: params
        })

        console.log('Datos de habitaciones reservadas:', response.data)

        if (response.data && Array.isArray(response.data)) {
          this.habitacionesReservadas = response.data
          // Si ya tenemos las reservas, las organizamos
          if (this.reservas.length > 0) {
            this.organizarReservasPorHabitacion()
          }
        } else {
          this.habitacionesReservadas = []
          console.warn('Formato de respuesta inválido')
        }
      } catch (error) {
        console.error('Error al obtener reservas:', error)
        if (error.response) {
          console.error('Detalles del error:', error.response.status, error.response.data)

          if (error.response.status === 403) {
            this.error = 'No tienes permisos para ver las reservas. Solo propietarios de mascotas pueden acceder.'
          } else if (error.response.status === 400) {
            this.error = 'Error en la solicitud. ' + (error.response.data.message || 'Verifica los datos enviados.')
          } else if (error.response.status === 404) {
            this.error = 'No se encontraron reservas.'
            this.habitacionesReservadas = []
          } else {
            this.error = 'Error al cargar las reservas. Por favor, intenta nuevamente.'
          }
        } else {
          this.error = 'Error de conexión. Verifica tu conexión a internet.'
        }
      } finally {
        this.loading = false
      }
    },

    async obtenerMascotas () {
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user || !user.id) {
        this.todasLasMascotas = []
        return
      }

      try {
        const res = await axios.get('http://localhost:5000/api/mascotas/listar-tus-mascotas', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })
        this.todasLasMascotas = res.data || []
        console.log('Todas las mascotas cargadas:', this.todasLasMascotas)
      } catch (error) {
        console.error('Error al cargar mascotas:', error)
        this.todasLasMascotas = []
      }
    },

    async obtenerMisReservas () {
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user || !user.id) {
        this.reservas = []
        return
      }

      this.cargandoReservas = true

      try {
        const res = await axios.get('http://localhost:5000/api/reservas/mis_reservas', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        this.reservas = res.data || []
        console.log('Datos de reservas:', this.reservas)

        // Organizar reservas por habitación
        this.organizarReservasPorHabitacion()
      } catch (error) {
        console.error('Error al cargar reservas:', error)
        this.reservas = []
      } finally {
        this.cargandoReservas = false
      }
    },

    organizarReservasPorHabitacion () {
      // Crear un mapa para agrupar reservas por habitación
      const reservasPorHabitacion = {}

      this.reservas.forEach(reserva => {
        if (!reservasPorHabitacion[reserva.habitacion_id]) {
          reservasPorHabitacion[reserva.habitacion_id] = []
        }
        reservasPorHabitacion[reserva.habitacion_id].push(reserva)
      })

      // Asignar las reservas a cada habitación
      this.habitacionesReservadas = this.habitacionesReservadas.map(habitacion => {
        return {
          ...habitacion,
          reservas: reservasPorHabitacion[habitacion.id] || []
        }
      })
    },

    formatearFecha (fechaString) {
      const fecha = new Date(fechaString)
      return fecha.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }
  }
}
</script>

<style scoped src="./css/PropHabitacionesHotelReservas.css"></style>
