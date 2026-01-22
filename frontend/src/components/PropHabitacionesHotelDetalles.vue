<template>
  <div class="detalles-habitacion-container">
    <!-- Estados de carga y error -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando detalles de la habitación...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <h3><i class="fas fa-exclamation-triangle"></i> Error</h3>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="errorPermisos" class="no-auth">
      <h3><i class="fas fa-lock"></i> Sin permisos</h3>
      <p>{{ mensajeError }}</p>
    </div>

    <!-- Vista de detalles de la habitación -->
    <div v-else class="room-details-view">
      <div class="container">
        <div class="room-details-container">
          <!-- Imagen de la habitación -->
          <div class="room-image-container">
            <img
              v-if="habitacion.url_imagen"
              :src="habitacion.url_imagen"
              :alt="habitacion.nombre"
              class="room-image"
            />
            <div v-else class="no-image-placeholder">
              <span>No Image</span>
            </div>
          </div>

          <!-- Información de la habitación -->
          <div class="room-info">
            <h1 class="room-title">{{ habitacion.nombre || 'Habitación sin nombre' }}</h1>
            <p class="room-perfect-for">Perfecto para: {{ getPetType(habitacion.tipo) }}</p>

            <div class="room-meta">
              <div class="room-meta-item">
                <i class="fas fa-expand-arrows-alt"></i>
                <span>Tamaño: {{ habitacion.tamaño || 'No especificado' }}</span>
              </div>
              <div class="room-meta-item">
                <i class="fas fa-home"></i>
                <span>Tipo: {{ habitacion.tipo || 'No especificado' }}</span>
              </div>
            </div>

            <!-- Etiquetas de características -->
            <div class="room-features">
              <div v-if="habitacion.reservable" class="feature-tag reservable">
                Reservable
              </div>
              <div v-else class="feature-tag not-reservable">
                No Reservable
              </div>
              <div class="feature-tag available">
                Disponible
              </div>
            </div>

            <!-- Descripción -->
            <h3 class="section-title">Descripción de la habitación</h3>
            <p class="room-description">
              {{ habitacion.descripcion || 'No hay descripción disponible para esta habitación.' }}
            </p>

            <!-- Botones de acción -->
            <div class="action-buttons">
              <button class="btn btn-primary" @click="consultarDisponibilidad">
                <i class="far fa-calendar-alt"></i> Consultar Disponibilidad
              </button>
              <button
                class="btn btn-secondary"
                @click="reservarHabitacion"
                :disabled="!habitacion.reservable"
                :class="{ 'disabled': !habitacion.reservable }"
              >
                <i class="fas fa-paw"></i> Reservar Ahora
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/axios'

export default {
  name: 'DetallesHabitacion',

  data () {
    return {
      info_usuario: null,
      jwtValido: false,

      habitacion: {
        id: null,
        nombre: '',
        descripcion: '',
        reservable: false,
        url_imagen: '',
        tamaño: '',
        tipo: '',
        clinica_id: null,
        propietario_clinica_id: null
      },

      loading: true,
      error: '',
      errorPermisos: false,
      mensajeError: '',

      habitacionId: null
    }
  },

  computed: {
    usuarioIniciales () {
      if (!this.info_usuario || !this.info_usuario.tipo_usuario) return 'U'
      return this.info_usuario.tipo_usuario.charAt(0)
    },
    usuarioNombre () {
      if (!this.info_usuario || !this.info_usuario.id) return 'Usuario'
      return `Usuario #${this.info_usuario.id}`
    },
    usuarioRolFormateado () {
      if (!this.info_usuario || !this.info_usuario.tipo_usuario) return 'Rol'
      const roleMap = {
        'PROP_CLINICA': 'Propietario de Clínica',
        'PROP_MASCOTA': 'Propietario de Mascota',
        'ADMIN': 'Administrador'
      }
      return roleMap[this.info_usuario.tipo_usuario] || this.info_usuario.tipo_usuario
    }
  },

  created () {
    this.habitacionId = this.$route.params.id
    this.checkAuth()
    window.addEventListener('logout', this.checkAuth)
  },

  beforeUnmount () {
    window.removeEventListener('logout', this.checkAuth)
  },

  methods: {
    async checkAuth () {
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
        await this.obtenerDetallesHabitacion()
      } catch (e) {
        this.jwtValido = false
        this.error = 'Error de autenticación. Por favor, inicie sesión nuevamente.'
        this.loading = false
      }
    },

    async obtenerDetallesHabitacion () {
      if (!this.jwtValido || !this.habitacionId) {
        this.error = 'Faltan credenciales o ID de habitación'
        this.loading = false
        return
      }

      this.loading = true
      this.error = ''
      this.errorPermisos = false

      try {
        const url = `http://localhost:5000/api/habitaciones_hotel/detalles/${this.habitacionId}`
        const response = await api.get(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        console.log('Datos de la habitación:', response.data)

        if (response.data) {
          this.habitacion = response.data
        } else {
          this.error = 'No se recibieron datos de la habitación'
        }
      } catch (error) {
        console.error('Error al obtener detalles de la habitación:', error)

        if (error.response) {
          console.error('Respuesta de error:', error.response)
          console.error('Status:', error.response.status)
          console.error('Data:', error.response.data)

          if (error.response.status === 403) {
            this.errorPermisos = true
            this.mensajeError = error.response.data.message || 'No tienes permiso para ver los detalles de esta habitación'
          } else if (error.response.status === 404) {
            this.error = 'Habitación no encontrada'
          } else {
            this.error = `Error ${error.response.status}: ${error.response.data.message || 'Error al cargar los detalles'}`
          }
        } else if (error.request) {
          console.error('No se recibió respuesta:', error.request)
          this.error = 'No se pudo conectar con el servidor. Verifica tu conexión.'
        } else {
          this.error = 'Error al realizar la solicitud. Por favor, intenta nuevamente.'
        }
      } finally {
        this.loading = false
      }
    },

    // Obtener tipo de mascota para mostrar
    getPetType (roomType) {
      if (!roomType) return 'Pets'

      const petTypeMap = {
        'gato': 'Gatos',
        'perro': 'Perros',
        'reptil': 'Reptiles',
        'pájaro': 'Pájaros',
        'HAMSTER': 'Hamsters',
        'tortuga': 'Tortugas',
        'GATO': 'Cats',
        'PERRO': 'Dogs',
        'EXOTICO': 'Exotic Pets',
        'MIXTO': 'All Pets'
      }

      return petTypeMap[roomType.toUpperCase()] || 'Cualquier tipo de mascota'
    }
  }
}
</script>

<style scoped src="./css/DetallesHabitacion.css"></style>
