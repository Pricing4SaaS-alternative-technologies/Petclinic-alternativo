<template>
  <div class="pet-hotel-container">
    <div class="hotel-header">
      <h1 class="hotel-title">Habitaciones de Hotel</h1>
      <p class="hotel-description">
        Deja a tu mascota bajo el mejor cuidado de nuestro personal dedicado en el hotel para mascotas.
      </p>
    </div>

    <div v-if="jwtValido">
      <div class="rooms-header">
        <h2 class="rooms-title">Todas las habitaciones</h2>

        <div class="header-actions">
          <div v-if="info_usuario.tipo === 'prop_mascota'">
            <button class="see-reservas-btn" @click="verMisReservas">
              <i class="fas fa-paw"></i> Mis reservas
            </button>
          </div>

          <!-- Botón para crear habitación (solo para prop_clinica y admin) -->
          <div v-if="info_usuario.tipo === 'prop_clinica' || info_usuario.tipo_usuario === 'admin'">
            <button class="create-room-btn" @click="abrirModalCrear">
              <i class="fas fa-plus"></i> Crear Habitación
            </button>
          </div>
        </div>
      </div>

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
            <p class="room-perfect-for">Perfecto para: {{ habitacion.tipo }}</p>
            <p v-if="info_usuario.tipo === 'prop_clinica'" class="room-perfect-for">Clínica: {{ habitacion.nombre_clinica }}</p>
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

    <!-- Modal para crear nueva habitación -->
    <div v-if="modalCrearVisible" class="modal-overlay" @click="cerrarModalCrear">
      <div class="modal-content crear-modal" @click.stop>
        <div class="modal-header">
          <h2><i class="fas fa-plus"></i> Crear Nueva Habitación</h2>
          <button class="close-modal" @click="cerrarModalCrear">&times;</button>
        </div>

        <div class="modal-body">
          <div v-if="errorCrear" class="error-message-modal">
            <i class="fas fa-exclamation-circle"></i> {{ errorCrear }}
          </div>

          <div v-if="successCrear" class="success-message-modal">
            <i class="fas fa-check-circle"></i> {{ successCrear }}
          </div>

          <form @submit.prevent="guardarCreacion">
            <div class="form-group">
              <label for="crear-nombre">
                <i class="fas fa-signature"></i> Nombre de la habitación *
              </label>
              <input
                type="text"
                id="crear-nombre"
                v-model="formCrear.nombre"
                required
                maxlength="100"
                :disabled="cargandoCrear"
                placeholder="Ej: Suite para perros grandes"
              />
              <small class="text-muted">Máximo 100 caracteres</small>
            </div>

            <div class="form-group">
              <label for="crear-descripcion">
                <i class="fas fa-align-left"></i> Descripción *
              </label>
              <textarea
                id="crear-descripcion"
                v-model="formCrear.descripcion"
                required
                maxlength="255"
                rows="3"
                :disabled="cargandoCrear"
                placeholder="Describe las características de la habitación..."
              ></textarea>
              <small class="text-muted">Máximo 255 caracteres</small>
            </div>

            <div class="form-group">
              <label><i class="fas fa-ruler-combined"></i> Tamaño *</label>
              <div class="radio-group">
                <label
                  v-for="tamaño in tamaños"
                  :key="tamaño.value"
                  :class="{ selected: formCrear.tamaño === tamaño.value }"
                >
                  <input
                    type="radio"
                    v-model="formCrear.tamaño"
                    :value="tamaño.value"
                    required
                    :disabled="cargandoCrear"
                  />
                  {{ tamaño.label }}
                </label>
              </div>
            </div>

            <div class="form-group">
              <label><i class="fas fa-paw"></i> Tipo de mascota *</label>
              <div class="radio-group">
                <label
                  v-for="tipo in tipos"
                  :key="tipo.value"
                  :class="{ selected: formCrear.tipo === tipo.value }"
                >
                  <input
                    type="radio"
                    v-model="formCrear.tipo"
                    :value="tipo.value"
                    required
                    :disabled="cargandoCrear"
                  />
                  {{ tipo.label }}
                </label>
              </div>
            </div>

            <div class="form-group">
              <label for="crear-url_imagen">
                <i class="fas fa-image"></i> URL de la imagen (opcional)
              </label>
              <input
                type="url"
                id="crear-url_imagen"
                v-model="formCrear.url_imagen"
                maxlength="255"
                :disabled="cargandoCrear"
                placeholder="https://ejemplo.com/imagen.jpg"
              />
              <small class="text-muted">Enlace a una imagen representativa</small>
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="formCrear.reservable"
                  :disabled="cargandoCrear"
                  checked
                />
                <span class="checkmark"></span>
                Habitación reservable
              </label>
              <small class="text-muted">Si está desactivado, la habitación no podrá ser reservada</small>
            </div>

            <!-- Selector de clínica para todos los usuarios con permisos -->
            <div class="form-group">
              <label for="crear-clinica_id">
                <i class="fas fa-hospital"></i> Clínica *
              </label>
              <select
                id="crear-clinica_id"
                v-model="formCrear.clinica_id"
                required
                :disabled="cargandoCrear || cargandoClinicas"
                class="clinica-select"
              >
                <option value="" disabled>Selecciona una clínica...</option>
                <option
                  v-for="clinica in clinicas"
                  :key="clinica.id"
                  :value="clinica.id"
                >
                  {{ clinica.nombre }}
                </option>
              </select>
              <small v-if="cargandoClinicas" class="text-muted">
                <i class="fas fa-spinner fa-spin"></i> Cargando clínicas...
              </small>
            </div>

            <!-- Vista previa de la imagen -->
            <div v-if="formCrear.url_imagen" class="image-preview">
              <label><i class="fas fa-eye"></i> Vista previa:</label>
              <div class="preview-container">
                <img
                  :src="formCrear.url_imagen"
                  alt="Vista previa"
                  @error="handleImageErrorCrear"
                />
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="cerrarModalCrear" :disabled="cargandoCrear">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary" :disabled="cargandoCrear">
                <i v-if="cargandoCrear" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-save"></i>
                {{ cargandoCrear ? 'Creando...' : 'Crear Habitación' }}
              </button>
            </div>
          </form>
        </div>
      </div>
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
      error: '',

      // Datos para el modal de creación
      modalCrearVisible: false,
      cargandoCrear: false,
      errorCrear: '',
      successCrear: '',
      clinicas: [],
      cargandoClinicas: false,
      formCrear: {
        nombre: '',
        descripcion: '',
        tamaño: 'mediano',
        reservable: true,
        url_imagen: '',
        tipo: 'perro',
        clinica_id: null
      },
      tamaños: [
        { value: 'acogedor', label: 'Acogedor' },
        { value: 'mediano', label: 'Mediano' },
        { value: 'king_size', label: 'King Size' }
      ],
      tipos: [
        { value: 'gato', label: 'Gato' },
        { value: 'perro', label: 'Perro' },
        { value: 'reptil', label: 'Reptil' },
        { value: 'pajaro', label: 'Pájaro' },
        { value: 'hamster', label: 'Hamster' },
        { value: 'tortuga', label: 'Tortuga' }
      ]
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

        // Según el tipo de usuario, cargar las habitaciones correspondientes
        if (this.info_usuario.tipo === 'prop_mascota') {
          this.obtenerHabitaciones()
        } else if (this.info_usuario.tipo === 'prop_clinica') {
          this.obtenerHabitacionesDueñoClinica()
        } else if (this.info_usuario.tipo_usuario === 'admin') {
          // Para admin, mostrar todas las habitaciones de todas las clínicas
          this.obtenerHabitacionesAdmin()
        }
      } catch (e) {
        console.error('Error al parsear el usuario:', e)
        this.jwtValido = false
      }
    },

    async verMisReservas () {
      try {
        // Redirigir a la vista de reservas
        this.$router.push('/mis-reservas')
      } catch (error) {
        console.error('Error al navegar a reservas:', error)
        alert('Error al cargar las reservas')
      }
    },

    async obtenerHabitaciones () {
      if (!this.jwtValido) return

      this.loading = true
      this.error = ''

      try {
        console.log('Usuario clínica ID:', this.info_usuario.clinica_id)
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

    async obtenerHabitacionesDueñoClinica () {
      if (!this.jwtValido) return

      this.loading = true
      this.error = ''

      try {
        console.log('Dueño clínica ID:', this.info_usuario.id)
        const response = await api.get(`http://localhost:5000/api/habitaciones_hotel/listar/prop-clinica/${this.info_usuario.id}`, {
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

    async obtenerHabitacionesAdmin () {
      if (!this.jwtValido) return

      this.loading = true
      this.error = ''

      try {
        // Endpoint para obtener todas las habitaciones (para admin)
        const response = await api.get('http://localhost:5000/api/habitaciones_hotel/listar', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        console.log('Datos de habitaciones (admin):', response.data)

        if (response.data) {
          this.habitaciones = response.data
        } else {
          this.error = 'No se recibieron datos de habitaciones'
        }
      } catch (error) {
        console.error('Error al obtener habitaciones (admin):', error)
        this.error = 'Error al cargar las habitaciones. Por favor, intenta nuevamente.'
      } finally {
        this.loading = false
      }
    },

    // Métodos para el modal de creación
    async abrirModalCrear () {
      // Verificar que el usuario tenga permisos para crear
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user) {
        alert('Debes iniciar sesión para crear una habitación.')
        this.$router.push('/login')
        return
      }

      // Solo propietarios de clínica y administradores pueden crear
      if (user.tipo !== 'prop_clinica' && user.tipo_usuario !== 'admin') {
        alert('No tienes permisos para crear habitaciones.')
        return
      }

      // Resetear el formulario
      this.resetFormCrear()

      this.modalCrearVisible = true
      this.errorCrear = ''
      this.successCrear = ''

      // Cargar las clínicas disponibles según el tipo de usuario
      await this.cargarClinicasDisponibles()
    },

    async cargarClinicasDisponibles () {
      this.cargandoClinicas = true
      try {
        let url = ''

        if (this.info_usuario.tipo === 'prop_clinica') {
          // Para prop_clinica: cargar las clínicas que le pertenecen
          url = `http://localhost:5000/api/clinicas/listar/${this.info_usuario.id}`
        } else if (this.info_usuario.tipo_usuario === 'admin') {
          // Para admin: cargar todas las clínicas
          url = 'http://localhost:5000/api/clinicas/listar-todas'
        }

        const response = await api.get(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        this.clinicas = response.data || []

        if (this.clinicas.length === 0) {
          this.errorCrear = 'No hay clínicas disponibles para crear habitaciones.'
        } else if (this.clinicas.length === 1) {
          // Si solo hay una clínica, seleccionarla automáticamente
          this.formCrear.clinica_id = this.clinicas[0].id
        }
      } catch (error) {
        console.error('Error al cargar clínicas:', error)
        this.clinicas = []

        if (error.response && error.response.status === 404) {
          // Si no existe el endpoint específico, intentar cargar todas las clínicas
          try {
            const response = await api.get('http://localhost:5000/api/clinicas/listar', {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('jwt')}`
              }
            })
            this.clinicas = response.data || []
          } catch (secondError) {
            console.error('Error al cargar todas las clínicas:', secondError)
            this.errorCrear = 'No se pudieron cargar las clínicas. Verifica tu conexión.'
          }
        } else {
          this.errorCrear = 'No se pudieron cargar las clínicas. Verifica tu conexión.'
        }
      } finally {
        this.cargandoClinicas = false
      }
    },

    cerrarModalCrear () {
      this.modalCrearVisible = false
      this.errorCrear = ''
      this.successCrear = ''
      this.cargandoCrear = false
      this.clinicas = []
      this.cargandoClinicas = false
      // Resetear el formulario
      this.resetFormCrear()
    },

    resetFormCrear () {
      this.formCrear = {
        nombre: '',
        descripcion: '',
        tamaño: 'mediano',
        reservable: true,
        url_imagen: '',
        tipo: 'perro',
        clinica_id: null
      }
    },

    handleImageErrorCrear (event) {
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZWVlZWVlIi8+Cjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5OTk5Ij5JbWFnZW4gbm8gZGlzcG9uaWJsZTwvdGV4dD4KPC9zdmc+'
    },

    validarFormularioCreacion () {
      if (!this.formCrear.nombre || !this.formCrear.descripcion || !this.formCrear.tamaño || !this.formCrear.tipo) {
        this.errorCrear = 'Por favor, completa todos los campos obligatorios'
        return false
      }

      if (this.formCrear.nombre.length > 100) {
        this.errorCrear = 'El nombre no puede tener más de 100 caracteres'
        return false
      }

      if (this.formCrear.descripcion.length > 255) {
        this.errorCrear = 'La descripción no puede tener más de 255 caracteres'
        return false
      }

      if (this.formCrear.url_imagen && this.formCrear.url_imagen.length > 255) {
        this.errorCrear = 'La URL de la imagen no puede tener más de 255 caracteres'
        return false
      }

      // Validar que se haya seleccionado una clínica
      if (!this.formCrear.clinica_id) {
        this.errorCrear = 'Por favor, selecciona una clínica'
        return false
      }

      return true
    },

    async guardarCreacion () {
      this.errorCrear = ''
      this.successCrear = ''

      if (!this.validarFormularioCreacion()) {
        return
      }

      this.cargandoCrear = true

      try {
        console.log('Enviando datos para crear habitación:', this.formCrear)

        const response = await api.post(
          'http://localhost:5000/api/habitaciones_hotel/crear-habitacion',
          this.formCrear,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('jwt')}`
            }
          }
        )

        console.log('Respuesta de creación:', response.data)
        this.successCrear = response.data.msg || 'Habitación creada con éxito'

        // Actualizar la lista de habitaciones después de crear
        await this.actualizarListaHabitaciones()

        // Cerrar el modal después de 2 segundos
        setTimeout(() => {
          this.cerrarModalCrear()
        }, 1000)
      } catch (error) {
        console.error('Error al crear la habitación:', error)

        if (error.response) {
          const { status, data } = error.response

          switch (status) {
            case 400:
              this.errorCrear = data.msg || 'Datos inválidos'
              break
            case 403:
              this.errorCrear = data.msg || 'No tienes permiso para crear habitaciones'
              break
            case 404:
              this.errorCrear = data.msg || 'Clínica no encontrada'
              break
            case 409:
              this.errorCrear = data.msg || 'Ya existe una habitación con ese nombre'
              break
            case 500:
              this.errorCrear = data.msg || 'Error en el servidor al crear la habitación'
              break
            default:
              this.errorCrear = data.msg || 'Error al crear la habitación'
          }
        } else if (error.request) {
          this.errorCrear = 'No se pudo conectar con el servidor. Verifica tu conexión.'
        } else {
          this.errorCrear = 'Error al realizar la solicitud. Por favor, intenta nuevamente.'
        }
      } finally {
        this.cargandoCrear = false
      }
    },

    async actualizarListaHabitaciones () {
      try {
        // Actualizar la lista de habitaciones según el tipo de usuario
        if (this.info_usuario.tipo === 'prop_mascota') {
          await this.obtenerHabitaciones()
        } else if (this.info_usuario.tipo === 'prop_clinica') {
          await this.obtenerHabitacionesDueñoClinica()
        } else if (this.info_usuario.tipo_usuario === 'admin') {
          await this.obtenerHabitacionesAdmin()
        }
      } catch (error) {
        console.error('Error al actualizar lista de habitaciones:', error)
      }
    }
  }
}
</script>

<style scoped src="./css/PropHabitacionesHotel.css"></style>
