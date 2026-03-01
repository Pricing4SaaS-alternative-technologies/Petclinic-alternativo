<template>
  <div class="detalles-habitacion-container">
    <div v-if="notificacion.visible" :class="['notification', notificacion.tipo]">
      <p>{{ notificacion.mensaje }}</p>
    </div>
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
            <div v-if="info_usuario.tipo === 'prop_mascota'">
              <div class="action-buttons">
                <button class="see-reservas-btn" @click="abrirModalDisponibilidad">
                  <i class="far fa-calendar-alt"></i> Consultar Disponibilidad
                </button>
                <button class="see-reservas-btn" @click="verMisReservas">
                  <i class="fas fa-paw"></i> Mis reservas
                </button>
              </div>
            </div>
            <div v-else-if="info_usuario.tipo === 'prop_clinica' || info_usuario.tipo_usuario === 'admin'">
              <div class="action-buttons">
                <button class="see-reservas-btn" @click="verCalendarioReservas">
                  <i class="far fa-calendar-alt"></i> Ver calendario
                </button>
                <button class="see-reservas-btn" @click="abrirModalEditar">
                  <i class="fas fa-edit"></i> Editar habitación
                </button>
                <button v-if="!habitacion.reservable" class="eliminar-reservas-btn" @click="confirmarEliminar" :disabled="habitacion.reservable == true">
                  <i class="fas fa-trash"></i> Eliminar habitación
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Disponibilidad -->
    <div v-if="modalVisible" class="modal-overlay" @click="cerrarModal">
      <div class="modal-disponibilidad" @click.stop>
        <h3>Disponibilidad de la habitación</h3>
        <form @submit.prevent="confirmarReserva">
          <!-- Selector de fechas -->
          <div class="fechas-container">
            <div class="fecha-group">
              <label>
                <i class="far fa-calendar-alt"></i> Fecha de entrada
              </label>
              <input
                type="date"
                v-model="fechaInicio"
                class="fecha-input"
                :min="fechaMinima"
                @input="validarFechas"
              >
              <div v-if="errorFechaInicio" class="fecha-error">
                <i class="fas fa-exclamation-circle"></i> {{ errorFechaInicio }}
              </div>
            </div>

            <div class="fecha-group">
              <label>
                <i class="far fa-calendar-alt"></i> Fecha de salida
              </label>
              <input
                type="date"
                v-model="fechaFin"
                class="fecha-input"
                :min="fechaInicio || fechaMinima"
                @input="validarFechas"
              >
              <div v-if="errorFechaFin" class="fecha-error">
                <i class="fas fa-exclamation-circle"></i> {{ errorFechaFin }}
              </div>
            </div>
          </div>

          <!-- Selector de mascotas -->
          <div class="mascota-group">
            <label>
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
              class="mascota-select"
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
            <div v-else class="no-mascotas-mensaje">
              <p><i class="fas fa-info-circle"></i>
                {{ todasLasMascotas.length === 0 ?
                  'No tienes mascotas registradas.' :
                  'No tienes mascotas compatibles con esta habitación.'
                }}
              </p>
            </div>
          </div>

          <!-- Mensaje de error general -->
          <div v-if="errorReserva" class="error-reserva">
            <i class="fas fa-exclamation-circle"></i> {{ errorReserva }}
          </div>

          <!-- Botones del modal -->
          <div class="modal-buttons">
            <button type="button" class="btn-cancelar" @click="cerrarModal">
              Cancelar
            </button>
            <button
              type="submit"
              class="btn-confirmar"
            >
              <i v-if="creandoReserva" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-calendar-check"></i>
              {{ creandoReserva ? 'Creando reserva...' : 'Confirmar Reserva' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal de Edición de Habitación -->
    <div v-if="modalEditarVisible" class="modal-overlay" @click="cerrarModalEditar">
      <div class="modal" @click.stop>
        <h3><i class="fas fa-edit"></i> Editar Habitación</h3>

        <div v-if="errorEditar" class="error-message-modal">
          <i class="fas fa-exclamation-circle"></i> {{ errorEditar }}
        </div>

        <div v-if="successEditar" class="success-message-modal">
          <i class="fas fa-check-circle"></i> {{ successEditar }}
        </div>

        <form @submit.prevent="guardarEdicion">
            <div class="form-group">
              <label for="edit-nombre">
                <i class="fas fa-signature"></i> Nombre de la habitación *
              </label>
              <input
                type="text"
                id="edit-nombre"
                v-model="formEditar.nombre"
                required
                maxlength="100"
                :disabled="cargandoEditar"
                placeholder="Ej: Suite para perros grandes"
              />
              <small class="text-muted">Máximo 100 caracteres</small>
            </div>

            <div class="form-group">
              <label for="edit-descripcion">
                <i class="fas fa-align-left"></i> Descripción *
              </label>
              <textarea
                id="edit-descripcion"
                v-model="formEditar.descripcion"
                required
                maxlength="255"
                rows="3"
                :disabled="cargandoEditar"
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
                  :class="{ selected: formEditar.tamaño === tamaño.value }"
                >
                  <input
                    type="radio"
                    v-model="formEditar.tamaño"
                    :value="tamaño.value"
                    required
                    :disabled="cargandoEditar"
                  />
                  {{ tamaño.label }}
                </label>
              </div>
            </div>

            <div v-if="formEditar.reservable == false" class="form-group">
              <label><i class="fas fa-ruler-combined"></i> Tipo *</label>
              <div class="radio-group">
                <label
                  v-for="tipo in tipos"
                  :key="tipo.value"
                  :class="{ selected: formEditar.tipo === tipo.value }"
                >
                  <input
                    type="radio"
                    v-model="formEditar.tipo"
                    :value="tipo.value"
                    required
                    :disabled="cargandoEditar"
                  />
                  {{ tipo.label }}
                </label>
              </div>
            </div>

            <div class="form-group">
              <label for="edit-url_imagen">
                <i class="fas fa-image"></i> URL de la imagen (opcional)
              </label>
              <input
                type="url"
                id="edit-url_imagen"
                v-model="formEditar.url_imagen"
                maxlength="255"
                :disabled="cargandoEditar"
                placeholder="https://ejemplo.com/imagen.jpg"
              />
              <small class="text-muted">Enlace a una imagen representativa</small>
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="formEditar.reservable"
                  :disabled="cargandoEditar"
                />
                <span class="checkmark"></span>
                Habitación reservable
              </label>
              <small class="text-muted">Si está desactivado, la habitación no podrá ser reservada</small>
            </div>

            <!-- Vista previa de la imagen -->
            <div v-if="formEditar.url_imagen" class="image-preview">
              <label><i class="fas fa-eye"></i> Vista previa:</label>
              <div class="preview-container">
                <img
                  :src="formEditar.url_imagen"
                  alt="Vista previa"
                  @error="handleImageError"
                />
              </div>
            </div>

            <div class="modal-buttons">
              <button type="submit" class="btn-crear" :disabled="cargandoEditar">
                <i v-if="cargandoEditar" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-save"></i>
                {{ cargandoEditar ? 'Guardando...' : 'Guardar Cambios' }}
              </button>
              <button type="button" class="cancelar" @click="cerrarModalEditar" :disabled="cargandoEditar">
                Cancelar
              </button>
            </div>
          </form>
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

      // Datos para el modal de disponibilidad
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
      creandoReserva: false,
      errorReserva: '',

      // Datos para el modal de edición
      modalEditarVisible: false,
      cargandoEditar: false,
      errorEditar: '',
      successEditar: '',
      formEditar: {
        nombre: '',
        descripcion: '',
        tamaño: 'mediano',
        reservable: true,
        url_imagen: '',
        tipo: 'perro'
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
      ],
      notificacion: {
        visible: false,
        mensaje: '',
        tipo: 'success'
      }
    }
  },

  computed: {
    mascotaSeleccionadaValida () {
      return this.mascotaSeleccionada && this.mascotaSeleccionada !== ''
    },

    formularioValido () {
      return (
        this.mascotaSeleccionadaValida &&
      this.fechasValidas &&
      !this.errorFechaInicio &&
      !this.errorFechaFin
      )
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
        this.errorReserva = ''
        this.creandoReserva = false
      }
    }
  },

  methods: {
    mostrarNotificacion (mensaje, tipo = 'success', callback = null) {
      this.notificacion.mensaje = mensaje
      this.notificacion.tipo = tipo
      this.notificacion.visible = true

      setTimeout(() => {
        this.notificacion.visible = false
        if (callback) {
          callback()
        }
      }, 2000)
    },
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
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        console.log('Datos de la habitación:', response.data)

        if (response.data) {
          this.habitacion = response.data
          // Cargar datos en el formulario de edición
          this.cargarDatosEdicion()
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

    cargarDatosEdicion () {
      this.formEditar = {
        nombre: this.habitacion.nombre || '',
        descripcion: this.habitacion.descripcion || '',
        tamaño: this.habitacion.tamaño || 'mediano',
        reservable: this.habitacion.reservable || false,
        url_imagen: this.habitacion.url_imagen || '',
        tipo: this.habitacion.tipo || 'perro'
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

    // Métodos para el modal de disponibilidad
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

    // Métodos para el modal de edición
    abrirModalEditar () {
      // Verificar que el usuario tenga permisos para editar
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user) {
        alert('Debes iniciar sesión para editar una habitación.')
        this.$router.push('/login')
        return
      }

      // Solo propietarios de clínica y administradores pueden editar
      if (user.tipo !== 'prop_clinica' && user.tipo_usuario !== 'admin') {
        alert('No tienes permisos para editar habitaciones.')
        return
      }

      this.modalEditarVisible = true
      this.errorEditar = ''
      this.successEditar = ''
    },

    cerrarModalEditar () {
      this.modalEditarVisible = false
      this.errorEditar = ''
      this.successEditar = ''
      this.cargandoEditar = false
      // Recargar datos originales
      this.cargarDatosEdicion()
    },

    handleImageError (event) {
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZWVlZWVlIi8+Cjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5OTk5Ij5JbWFnZW4gbm8gZGlzcG9uaWJsZTwvdGV4dD4KPC9zdmc+'
    },

    validarFormularioEdicion () {
      if (!this.formEditar.nombre || !this.formEditar.descripcion || !this.formEditar.tamaño) {
        this.errorEditar = 'Por favor, completa todos los campos obligatorios'
        return false
      }

      if (this.formEditar.nombre.length > 100) {
        this.errorEditar = 'El nombre no puede tener más de 100 caracteres'
        return false
      }

      if (this.formEditar.descripcion.length > 255) {
        this.errorEditar = 'La descripción no puede tener más de 255 caracteres'
        return false
      }

      if (this.formEditar.url_imagen && this.formEditar.url_imagen.length > 255) {
        this.errorEditar = 'La URL de la imagen no puede tener más de 255 caracteres'
        return false
      }

      return true
    },

    async guardarEdicion () {
      this.errorEditar = ''
      this.successEditar = ''

      if (!this.validarFormularioEdicion()) {
        return
      }

      this.cargandoEditar = true

      try {
        const response = await api.put(
          `http://localhost:5000/api/habitaciones_hotel/editar/${this.habitacionId}`,
          this.formEditar,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('jwt')}`
            }
          }
        )

        console.log('Respuesta de edición:', this.formEditar)
        this.successEditar = response.data.msg || 'Habitación actualizada exitosamente'

        // Actualizar los datos locales de la habitación
        this.habitacion = {
          ...this.habitacion,
          ...this.formEditar
        }

        // Cerrar el modal después de 2 segundos
        setTimeout(() => {
          this.cerrarModalEditar()
        }, 1000)
      } catch (error) {
        console.error('Error al editar la habitación:', error)

        if (error.response) {
          const { status, data } = error.response

          switch (status) {
            case 400:
              this.errorEditar = data.msg || 'Datos inválidos'
              break
            case 403:
              this.errorEditar = data.msg || 'No tienes permiso para editar esta habitación'
              break
            case 404:
              this.errorEditar = data.msg || 'Habitación no encontrada'
              break
            case 500:
              this.errorEditar = data.msg || 'Error en el servidor al actualizar la habitación'
              break
            default:
              this.errorEditar = data.msg || 'Error al actualizar la habitación'
          }
        } else if (error.request) {
          this.errorEditar = 'No se pudo conectar con el servidor. Verifica tu conexión.'
        } else {
          this.errorEditar = 'Error al realizar la solicitud. Por favor, intenta nuevamente.'
        }
      } finally {
        this.cargandoEditar = false
      }
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
      // Limpiar error previo
      this.errorReserva = ''

      // Validaciones con mensajes visuales
      if (!this.fechaInicio) {
        this.errorReserva = 'Por favor, selecciona una fecha de entrada'
        return
      }

      if (!this.fechaFin) {
        this.errorReserva = 'Por favor, selecciona una fecha de salida'
        return
      }

      if (this.errorFechaInicio) {
        this.errorReserva = this.errorFechaInicio
        return
      }

      if (this.errorFechaFin) {
        this.errorReserva = this.errorFechaFin
        return
      }

      if (!this.mascotaSeleccionada) {
        this.errorReserva = 'Por favor, selecciona una mascota'
        return
      }

      if (this.creandoReserva) {
        return // Evitar doble clic
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
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        if (response.status === 201) {
          this.cerrarModal()
          this.mostrarNotificacion(
            '¡Reserva creada exitosamente! Redirigiendo a "Mis Reservas"...',
            'success',
            () => {
              this.$router.push('/mis-reservas')
            }
          )
        }
      } catch (error) {
        console.error('Error al crear la reserva:', error)

        // Manejo de errores específicos del backend
        if (error.response) {
          const { status, data } = error.response

          switch (status) {
            case 400:
              this.mostrarNotificacion(`Error de validación: ${data.message}`, 'error')
              break
            case 403:
              this.mostrarNotificacion(`No tienes permiso: ${data.message}`, 'error')
              break
            case 404:
              this.mostrarNotificacion(`No encontrado: ${data.message}`, 'error')
              break
            case 409:
              this.mostrarNotificacion(`Conflicto: ${data.message}`, 'error')
              break
            default:
              this.mostrarNotificacion(`Error ${status}: ${data.message || 'Error al procesar la reserva'}`, 'error')
          }
        } else if (error.request) {
          this.mostrarNotificacion('No se pudo conectar con el servidor. Verifica tu conexión.', 'error')
        } else {
          this.mostrarNotificacion('Error al realizar la solicitud. Por favor, intenta nuevamente.', 'error')
        }
      } finally {
        this.creandoReserva = false
      }
    },

    confirmarEliminar () {
      if (!this.habitacion.id) {
        alert('No se puede eliminar la habitación: ID no disponible')
        return
      }

      const confirmacion = confirm(
        '¿Estás seguro de que deseas eliminar esta habitación?\n\n' +
    'Esta acción eliminará TODAS las reservas pasadas asociadas.\n' +
    'Esta acción no se puede deshacer.'
      )

      if (confirmacion) {
        this.eliminarHabitacion()
      }
    },

    async eliminarHabitacion () {
      try {
        const response = await api.delete(
          `http://localhost:5000/api/habitaciones_hotel/eliminar/${this.habitacionId}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('jwt')}`
            }
          }
        )

        alert(response.data.msg || 'Habitación eliminada con éxito')
        this.$router.push('/habitaciones-hotel')
      } catch (error) {
        console.error('Error al eliminar la habitación:', error)

        if (error.response) {
          const { status, data } = error.response

          switch (status) {
            case 400:
              alert(data.msg || 'No se puede eliminar la habitación')
              break
            case 403:
              alert(data.msg || 'No tienes permiso para eliminar esta habitación')
              break
            case 404:
              alert(data.msg || 'Habitación no encontrada')
              break
            case 500:
              alert(data.msg || 'Error en el servidor al eliminar la habitación')
              break
            default:
              alert(data.msg || 'Error al eliminar la habitación')
          }
        } else if (error.request) {
          alert('No se pudo conectar con el servidor. Verifica tu conexión.')
        } else {
          alert('Error al realizar la solicitud. Por favor, intenta nuevamente.')
        }
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
    },

    verCalendarioReservas () {
      // Navegar al calendario de reservas con solo el ID
      this.$router.push({
        name: 'calendario-reservas',
        params: {
          habitacion_id: this.habitacion_id || this.habitacionId
        }
      })
    }
  }
}
</script>

<style scoped src="./css/PropHabitacionesHotelDetalles.css"></style>
<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  z-index: 1000;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
}

.notification.success {
  background-color: #4CAF50; /* Verde éxito */
}

.notification.error {
  background-color: #f44336; /* Rojo error */
}

.notification p {
  margin: 0;
}
</style>
