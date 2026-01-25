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
            <img v-if="habitacion.url_imagen" :src="habitacion.url_imagen" :alt="habitacion.nombre"
              class="room-image" />
            <div v-else class="no-image-placeholder">
              <span>No Image</span>
            </div>
          </div>

          <!-- Información de la habitación -->
          <div class="room-info">
            <h1 class="room-title">{{ habitacion.nombre || 'Habitación sin nombre' }}</h1>
            <p class="room-perfect-for">Perfecto para: {{ habitacion.tipo }}</p>

            <div class="room-meta">
              <div class="room-meta-item">
                <i class="fas fa-expand-arrows-alt"></i>
                <span>Tamaño: {{ habitacion.tamaño || 'No especificado' }}</span>
              </div>
            </div>

            <div class="room-features">
              <div v-if="habitacion.reservable" class="feature-tag available">
                Reservable
              </div>
              <div v-else class="feature-tag not-available">
                No Reservable
              </div>
            </div>

            <!-- Descripción -->
            <h3 class="section-title" style="margin-top: 6vh;">Descripción de la habitación</h3>
            <p class="room-description">
              {{ habitacion.descripcion || 'No hay descripción disponible para esta habitación.' }}
            </p>

            <!-- Botones de acción -->
            <div class="action-buttons">
              <button class="see-reservas-btn" @click="abrirModalDisponibilidad">
                <i class="far fa-calendar-alt"></i> Consultar Disponibilidad
              </button>
              <button class="see-reservas-btn" @click="verMisReservas">
                <i class="fas fa-paw"></i> Mis reservas
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Disponibilidad -->
    <div v-if="modalVisible" class="modal-overlay" @click="cerrarModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Disponibilidad de la habitación</h2>
          <button class="close-modal" @click="cerrarModal">&times;</button>
        </div>

        <div class="modal-body">
          <!-- Selector de fechas -->
          <div class="availability-dates">
            <div class="date-range">
              <label class="date-label">
                <i class="far fa-calendar-alt"></i> Fecha de entrada
              </label>
              <div class="date-input-container">
                <input
                  type="date"
                  v-model="fechaInicio"
                  class="date-input"
                  :min="fechaMinima"
                  @input="validarFechas"
                >
                <i class="fas fa-calendar-alt date-icon"></i>
              </div>
              <div v-if="errorFechaInicio" class="date-error">
                <i class="fas fa-exclamation-circle"></i> {{ errorFechaInicio }}
              </div>
            </div>

            <div class="date-range">
              <label class="date-label">
                <i class="far fa-calendar-alt"></i> Fecha de salida
              </label>
              <div class="date-input-container">
                <input
                  type="date"
                  v-model="fechaFin"
                  class="date-input"
                  :min="fechaInicio || fechaMinima"
                  @input="validarFechas"
                >
                <i class="fas fa-calendar-alt date-icon"></i>
              </div>
              <div v-if="errorFechaFin" class="date-error">
                <i class="fas fa-exclamation-circle"></i> {{ errorFechaFin }}
              </div>
            </div>
          </div>

          <!-- Selector de mascotas -->
          <div class="pet-selection">
            <label class="pet-label">
              <i class="fas fa-paw"></i> Selecciona una mascota
            </label>

            <!-- Estado de carga para mascotas -->
            <div v-if="cargandoMascotas" class="loading-mascotas">
              <i class="fas fa-spinner fa-spin"></i> Cargando tus mascotas...
            </div>

            <!-- Select solo se muestra si hay mascotas -->
            <select
              v-else-if="mascotasFiltradas.length > 0"
              id="pet-select"
              class="pet-select"
              v-model="mascotaSeleccionada"
            >
              <option value="" disabled>Selecciona una mascota...</option>
              <option
                v-for="mascota in mascotasFiltradas"
                :key="mascota.id"
                :value="mascota.id"
              >
                {{ mascota.nombre }} ({{ mascota.tipo }})
              </option>
            </select>

            <!-- Mensaje si no hay mascotas disponibles -->
            <div v-else class="no-pets-message">
              <p><i class="fas fa-info-circle"></i>
                {{ todasLasMascotas.length === 0 ?
                  'No tienes mascotas registradas.' :
                  'No tienes mascotas compatibles con esta habitación.'
                }}
              </p>
            </div>
          </div>

          <!-- Botones del modal -->
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="cerrarModal">
              Cancelar
            </button>
            <button
              class="btn btn-primary"
              @click="confirmarReserva"
              :disabled="!formularioValido || creandoReserva"
            >
              <i v-if="creandoReserva" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-calendar-check"></i>
              {{ creandoReserva ? 'Creando reserva...' : 'Confirmar Reserva' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/axios'
import axios from 'axios'

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

      habitacionId: null,

      // Datos para el modal
      modalVisible: false,
      cargandoMascotas: false,
      todasLasMascotas: [],
      mascotaSeleccionada: '',

      // Fechas - SIN valores por defecto, vacías para que el usuario las elija
      fechaInicio: '',
      fechaFin: '',
      errorFechaInicio: '',
      errorFechaFin: '',

      // Estado para la creación de reserva
      creandoReserva: false
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
    },
    mascotaSeleccionadaValida () {
      return this.mascotaSeleccionada !== ''
    },
    // Filtrar mascotas por tipo de habitación
    mascotasFiltradas () {
      if (!this.habitacion.tipo || this.todasLasMascotas.length === 0) {
        return []
      }
      const tipoHabitacion = this.habitacion.tipo.toLowerCase()
      return this.todasLasMascotas.filter(mascota => {
        const tipoMascota = mascota.tipo ? mascota.tipo.toLowerCase() : ''
        return tipoMascota === tipoHabitacion
      })
    },
    // Fecha mínima (mañana) - para que solo se pueda seleccionar fechas posteriores a hoy
    fechaMinima () {
      const manana = new Date()
      manana.setDate(manana.getDate() + 1)
      return manana.toISOString().split('T')[0]
    },
    // Calcular número de noches - solo si hay ambas fechas
    noches () {
      if (!this.fechaInicio || !this.fechaFin) return 0

      const inicio = new Date(this.fechaInicio)
      const fin = new Date(this.fechaFin)

      // Asegurarse de que fin sea posterior a inicio
      if (fin <= inicio) return 0

      const diferencia = fin.getTime() - inicio.getTime()
      return Math.ceil(diferencia / (1000 * 3600 * 24))
    },
    // Verificar si las fechas son válidas (sin errores y con noches positivas)
    fechasValidas () {
      if (!this.fechaInicio || !this.fechaFin) return false

      const inicio = new Date(this.fechaInicio)
      const fin = new Date(this.fechaFin)
      const hoy = new Date()
      hoy.setHours(0, 0, 0, 0)

      // Validaciones
      if (inicio <= hoy) return false
      if (fin <= inicio) return false
      if (this.noches > 30) return false

      return true
    },
    // Validar formulario completo
    formularioValido () {
      return (
        this.mascotaSeleccionadaValida &&
        this.fechasValidas &&
        !this.errorFechaInicio &&
        !this.errorFechaFin
      )
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

  watch: {
    modalVisible (newVal) {
      if (newVal) {
        this.cargarMascotas()
      } else {
        // Resetear todo al cerrar el modal
        this.mascotaSeleccionada = ''
        this.fechaInicio = ''
        this.fechaFin = ''
        this.errorFechaInicio = ''
        this.errorFechaFin = ''
        this.creandoReserva = false
      }
    }
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

    async cargarMascotas () {
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user || !user.id) {
        this.todasLasMascotas = []
        return
      }

      this.cargandoMascotas = true

      try {
        const res = await axios.get('http://localhost:5000/api/mascotas/listar-tus-mascotas', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })
        this.todasLasMascotas = res.data || []
        console.log('Todas las mascotas cargadas:', this.todasLasMascotas)
        console.log('Tipo de habitación:', this.habitacion.tipo)
      } catch (error) {
        console.error('Error al cargar mascotas:', error)
        this.todasLasMascotas = []
      } finally {
        this.cargandoMascotas = false
      }
    },

    // Métodos para el modal
    async abrirModalDisponibilidad () {
      if (!this.habitacion.reservable) {
        alert('Esta habitación no es reservable en este momento.')
        return
      }

      // Verificar que el usuario tenga permisos para reservar
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user) {
        alert('Debes iniciar sesión para hacer una reserva.')
        this.$router.push('/login')
        return
      }

      this.modalVisible = true
    },

    cerrarModal () {
      this.modalVisible = false
    },

    // Validar fechas
    validarFechas () {
      this.errorFechaInicio = ''
      this.errorFechaFin = ''

      if (!this.fechaInicio) {
        this.errorFechaInicio = 'Por favor, selecciona una fecha de entrada'
        return
      }

      if (!this.fechaFin) {
        this.errorFechaFin = 'Por favor, selecciona una fecha de salida'
        return
      }

      const inicio = new Date(this.fechaInicio)
      const fin = new Date(this.fechaFin)
      const hoy = new Date()
      hoy.setHours(0, 0, 0, 0)

      // Solo permite fechas posteriores a hoy
      if (inicio <= hoy) {
        this.errorFechaInicio = 'La fecha de entrada debe ser posterior a hoy'
      }

      if (fin <= inicio) {
        this.errorFechaFin = 'La fecha de salida debe ser posterior a la de entrada'
      }

      if (this.noches > 30) {
        this.errorFechaFin = 'La estancia máxima es de 30 noches'
      }
    },

    async confirmarReserva () {
      if (!this.formularioValido) {
        alert('Por favor, completa todos los campos correctamente.')
        return
      }

      this.creandoReserva = true

      try {
        const mascota = this.mascotasFiltradas.find(m => m.id === this.mascotaSeleccionada)

        console.log('Creando reserva:', {
          habitacionId: this.habitacionId,
          mascotaId: this.mascotaSeleccionada,
          mascotaNombre: mascota.nombre,
          fechaInicio: this.fechaInicio,
          fechaFin: this.fechaFin,
          noches: this.noches
        })

        // Datos para enviar al backend
        const reservaData = {
          mascota_id: this.mascotaSeleccionada,
          habitacion_hotel_id: parseInt(this.habitacionId),
          fecha_inicio: this.fechaInicio,
          fecha_fin: this.fechaFin
        }

        console.log('Enviando datos al backend:', reservaData)

        // Llamada al endpoint del backend
        const response = await api.post('http://localhost:5000/api/reservas/crear', reservaData, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        if (response.status === 201) {
          // Éxito: mostrar mensaje y cerrar modal
          alert(`¡Reserva creada exitosamente!
            Mascota: ${mascota.nombre}
            Desde: ${this.formatearFecha(this.fechaInicio)}
            Hasta: ${this.formatearFecha(this.fechaFin)}
            Noches: ${this.noches}`)

          this.cerrarModal()
          // this.$router.push('/mis-reservas')
        }
      } catch (error) {
        console.error('Error al crear la reserva:', error)

        // Manejo de errores específicos del backend
        if (error.response) {
          const { status, data } = error.response

          switch (status) {
            case 400:
              alert(`Error de validación: ${data.message}`)
              break
            case 403:
              alert(`No tienes permiso: ${data.message}`)
              break
            case 404:
              alert(`No encontrado: ${data.message}`)
              break
            case 409:
              alert(`Conflicto: ${data.message}`)
              break
            default:
              alert(`Error ${status}: ${data.message || 'Error al procesar la reserva'}`)
          }
        } else if (error.request) {
          alert('No se pudo conectar con el servidor. Verifica tu conexión.')
        } else {
          alert('Error al realizar la solicitud. Por favor, intenta nuevamente.')
        }
      } finally {
        this.creandoReserva = false
      }
    },

    // Formatear fecha para mostrar (DD/MM/YYYY)
    formatearFecha (fechaISO) {
      if (!fechaISO) return ''
      const fecha = new Date(fechaISO)

      // Asegurarse de que la fecha sea válida
      if (isNaN(fecha.getTime())) return ''

      const dia = fecha.getDate().toString().padStart(2, '0')
      const mes = (fecha.getMonth() + 1).toString().padStart(2, '0')
      const año = fecha.getFullYear()
      return `${dia}/${mes}/${año}`
    },

    async verMisReservas () {
      try {
        // Redirigir a la vista de reservas
        this.$router.push('/mis-reservas')
      } catch (error) {
        console.error('Error al navegar a reservas:', error)
        alert('Error al cargar las reservas')
      }
    }
  }
}
</script>

<style scoped src="./css/PropHabitacionesHotelDetalles.css"></style>
