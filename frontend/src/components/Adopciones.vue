<template>
  <div class="visitas-container" v-if="jwtValido">
    <h2>🐾 Adopciones</h2>

    <div class="adopciones-layout">
      <!-- =======================
           Mis adopciones
           ======================= -->
      <section class="panel">
        <div class="panel-header">
          <h3>Mis adopciones</h3>
          <div class="panel-actions">
            <button
              v-if="info_usuario && info_usuario.tipo === 'prop_mascota'"
              class="btn-crear"
              @click="abrirModalCrear"
            >
              ➕ Crear adopción
            </button>
            <button class="btn-crear" @click="cargarMisAdopciones">↻ Refrescar</button>
          </div>
        </div>

        <p v-if="errorMis" class="mensaje-error">{{ errorMis }}</p>

        <ul v-if="misAdopciones.length" class="listado">
          <li
            v-for="a in misAdopciones"
            :key="a.id"
            class="item"
            :class="{ active: adopcionSeleccionada && adopcionSeleccionada.id === a.id }"
            @click="seleccionarAdopcion(a)"
          >
            <div class="item-top">
              <span class="item-title">{{ a.mascota_nombre }}</span>
              <span class="badge" :class="a.adopcion_cerrada ? 'badge-cerrada' : 'badge-abierta'">
                {{ a.adopcion_cerrada ? 'Cerrada' : 'Abierta' }}
              </span>
            </div>
            <div class="item-desc">{{ a.descripcion }}</div>
            <div class="item-meta">
              <span>Creada: {{ formatearFechaSimple(a.fecha_creacion) }}</span>
              <span v-if="a.dueño_nuevo_id">Adoptante: {{ a.dueño_nuevo_nombre }}</span>
              <span v-else>Sin adoptante</span>
            </div>
          </li>
        </ul>
        <p v-else class="no-visitas">No tienes adopciones creadas.</p>

        <!-- Peticiones de la adopción seleccionada -->
        <div class="subpanel" v-if="adopcionSeleccionada">
          <div class="panel-header">
            <h3>Peticiones ({{ adopcionSeleccionada.mascota_nombre }})</h3>
            <div class="panel-actions">
              <button
                class="btn-eliminar"
                @click="abrirModalEliminar"
                :disabled="tienePeticionesSinRechazar"
                :title="tienePeticionesSinRechazar ? 'No se puede eliminar una adopción con peticiones pendientes o aprobadas' : 'Eliminar adopción'"
              >
                🗑️ Eliminar
              </button>
              <button class="btn-crear" @click="cargarPeticionesDeAdopcion(adopcionSeleccionada.id)">
                ↻ Refrescar
              </button>
            </div>
          </div>

          <p v-if="errorPeticiones" class="mensaje-error">{{ errorPeticiones }}</p>

          <ul v-if="peticiones.length" class="listado">
            <li v-for="p in peticiones" :key="p.id" class="item">
              <div class="item-top">
                <span class="item-title">{{ p.solicitante_nombre }}</span>
                <span class="badge" :class="badgeEstado(p.estado_peticion)">
                  {{ p.estado_peticion }}
                </span>
              </div>

              <div class="item-desc">
                <strong>Razón:</strong> {{ p.razon_adopcion }}
              </div>

              <div class="item-meta">
                <span>Fecha: {{ formatearFechaSimple(p.fecha_solicitud) }}</span>
              </div>

              <div class="acciones" v-if="puedeDecidir(p)">
                <button @click="abrirModalAceptar(p)">✅ Aprobar</button>
                <button @click="abrirModalRechazar(p)">❌ Rechazar</button>
              </div>
              <p v-else class="no-visitas">
                Petición ya resuelta o adopción cerrada.
              </p>
            </li>
          </ul>
          <p v-else class="no-visitas">No hay peticiones para esta adopción.</p>
        </div>
      </section>

      <!-- =======================
           Adopciones disponibles
           ======================= -->
      <section class="panel">
        <div class="panel-header">
          <h3>Adopciones disponibles (mi clínica)</h3>
          <button class="btn-crear" @click="cargarAdopcionesClinica">↻ Refrescar</button>
        </div>

        <p v-if="errorClinica" class="mensaje-error">{{ errorClinica }}</p>

        <ul v-if="adopcionesClinica.length" class="listado">
          <li v-for="a in adopcionesClinica" :key="a.id" class="item">
            <div class="item-top">
              <span class="item-title">{{ a.mascota_nombre }}</span>
              <span class="badge" :class="a.adopcion_cerrada ? 'badge-cerrada' : 'badge-abierta'">
                {{ a.adopcion_cerrada ? 'Cerrada' : 'Abierta' }}
              </span>
            </div>

            <div class="item-desc">{{ a.descripcion }}</div>

            <div class="item-meta">
              <span>Dueño anterior: {{ a.dueño_anterior_nombre }}</span>
              <span>Creada: {{ formatearFechaSimple(a.fecha_creacion) }}</span>
            </div>

            <div class="acciones" v-if="puedeSolicitar(a)">
              <button
                @click="abrirModalSolicitud(a)"
                :disabled="tienePeticionPendiente(a)"
                :title="tienePeticionPendiente(a) ? 'Tu petición está a la espera de ser revisada' : 'Solicitar adopción'"
              >
                📩 Solicitar adopción
              </button>
            </div>

            <p v-else class="no-visitas">
              {{ a.dueño_anterior_id === usuarioId ? 'Es tu adopción.' : 'No disponible.' }}
            </p>
          </li>
        </ul>
        <p v-else class="no-visitas">No hay adopciones disponibles.</p>
      </section>
    </div>

    <!-- Modal solicitud -->
    <div class="modal-overlay" v-if="mostrarSolicitud">
      <div class="modal">
        <h3>Solicitar adopción</h3>
        <p>
          Mascota: <strong>{{ adopcionSolicitud.mascota_nombre }}</strong>
        </p>

        <label>Razón de adopción</label>
        <input v-model="razonSolicitud" maxlength="255" />

        <p v-if="errorSolicitud" class="mensaje-error">{{ errorSolicitud }}</p>

        <div class="modal-buttons">
          <button @click="crearSolicitud">Enviar</button>
          <button class="cancelar" @click="cerrarSolicitud">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Modal crear adopción -->
    <div class="modal-overlay" v-if="mostrarCrear">
      <div class="modal">
        <h3>Crear adopción</h3>

        <label>Mascota</label>
        <select v-model="nuevaAdopcion.mascota_id">
          <option disabled value="">-- Selecciona una mascota --</option>
          <option v-for="m in misMascotas" :key="m.id" :value="m.id">
            {{ m.nombre }}
          </option>
        </select>

        <label>Descripción</label>
        <input v-model="nuevaAdopcion.descripcion" maxlength="255" />

        <p v-if="errorCreacion" class="mensaje-error">{{ errorCreacion }}</p>

        <div class="modal-buttons">
          <button @click="crearAdopcion">Enviar</button>
          <button class="cancelar" @click="cerrarCrear">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Modal aceptar -->
    <div class="modal-overlay" v-if="mostrarAceptar">
      <div class="modal">
        <h3>Aprobar petición</h3>
        <p>
          ¿Seguro que quieres aprobar la petición de
          <strong>{{ peticionAccion.solicitante_nombre }}</strong>
          para <strong>{{ adopcionSeleccionada.mascota_nombre }}</strong>?
        </p>

        <div class="modal-buttons">
          <button @click="aceptarPeticion">Aprobar</button>
          <button class="cancelar" @click="cerrarAceptar">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Modal rechazar -->
    <div class="modal-overlay" v-if="mostrarRechazar">
      <div class="modal">
        <h3>Rechazar petición</h3>
        <p>
          ¿Seguro que quieres rechazar la petición de
          <strong>{{ peticionAccion.solicitante_nombre }}</strong>
          para <strong>{{ adopcionSeleccionada.mascota_nombre }}</strong>?
        </p>

        <div class="modal-buttons">
          <button @click="rechazarPeticion">Rechazar</button>
          <button class="cancelar" @click="cerrarRechazar">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Modal eliminar adopción -->
    <div class="modal-overlay" v-if="mostrarEliminar">
      <div class="modal">
        <h3>Eliminar adopción</h3>
        <p>
          ¿Estás seguro de que deseas eliminar la adopción de
          <strong>{{ adopcionSeleccionada.mascota_nombre }}</strong>?
        </p>
        <p class="advertencia">Esta acción no se puede deshacer.</p>

        <p v-if="errorEliminar" class="mensaje-error">{{ errorEliminar }}</p>

        <div class="modal-buttons">
          <button class="btn-eliminar" @click="eliminarAdopcion">Eliminar</button>
          <button class="cancelar" @click="cerrarEliminar">Cancelar</button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="no-auth">
    <p class="error">No estás autorizado. Inicia sesión como propietario de mascota.</p>
  </div>
</template>

<script>
import api from '@/api/axios'

export default {
  data () {
    return {
      info_usuario: null,
      jwtValido: false,
      usuarioId: null,
      clinicaId: null,

      misAdopciones: [],
      adopcionSeleccionada: null,
      peticiones: [],

      misPeticiones: [],

      adopcionesClinica: [],

      misMascotas: [],

      errorMis: '',
      errorPeticiones: '',
      errorClinica: '',
      errorSolicitud: '',
      errorCreacion: '',
      errorEliminar: '',

      mostrarSolicitud: false,
      adopcionSolicitud: null,
      razonSolicitud: '',

      mostrarCrear: false,
      nuevaAdopcion: {
        mascota_id: '',
        descripcion: ''
      },

      mostrarAceptar: false,
      mostrarRechazar: false,
      peticionAccion: null,

      mostrarEliminar: false
    }
  },
  created () {
    this.checkAuth()
    window.addEventListener('logout', this.checkAuth)
  },
  beforeUnmount () {
    window.removeEventListener('logout', this.checkAuth)
  },
  computed: {
    tienePeticionesSinRechazar () {
      return this.peticiones.some(p => (p.estado_peticion || '').toLowerCase() !== 'rechazada')
    }
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

        if (this.info_usuario.tipo !== 'prop_mascota' && this.info_usuario.tipo !== 'admin') {
          this.jwtValido = false
          return
        }

        this.jwtValido = true
        this.usuarioId = this.info_usuario.id
        this.clinicaId = this.info_usuario.clinica_id

        this.cargarMisAdopciones()
        this.cargarAdopcionesClinica()
        this.cargarMisPeticiones()
      } catch (e) {
        console.error('Error al parsear usuario:', e)
        this.jwtValido = false
      }
    },

    async cargarMisAdopciones () {
      this.errorMis = ''
      this.adopcionSeleccionada = null
      this.peticiones = []
      try {
        const { data } = await api.get(`/adopciones/usuario/${this.usuarioId}`)
        this.misAdopciones = data
      } catch (e) {
        console.error('Error al cargar mis adopciones:', e.response)
        this.errorMis = (e.response && e.response.data && e.response.data.msg) || 'Error al cargar mis adopciones'
      }
    },

    async cargarAdopcionesClinica () {
      this.errorClinica = ''
      try {
        const { data } = await api.get(`/adopciones/clinica/${this.clinicaId}`)
        this.adopcionesClinica = data
        await this.cargarMisPeticiones()
      } catch (e) {
        console.error('Error al cargar adopciones de clínica:', e.response)
        this.errorClinica = (e.response && e.response.data && e.response.data.msg) || 'Error al cargar adopciones de clínica'
      }
    },

    async cargarMisPeticiones () {
      try {
        const { data } = await api.get(`/peticiones_adopcion/usuario/${this.usuarioId}`)
        this.misPeticiones = data
      } catch (e) {
        console.error('Error al cargar mis peticiones:', e.response)
        this.misPeticiones = []
      }
    },

    async cargarMisMascotas () {
      try {
        const { data } = await api.get('/mascotas/listar-tus-mascotas')
        this.misMascotas = data
      } catch (e) {
        console.error('Error al cargar mascotas:', e.response)
        this.misMascotas = []
      }
    },

    async seleccionarAdopcion (adopcion) {
      this.adopcionSeleccionada = adopcion
      await this.cargarPeticionesDeAdopcion(adopcion.id)
    },

    async cargarPeticionesDeAdopcion (adopcionId) {
      this.errorPeticiones = ''
      try {
        const { data } = await api.get(`/peticiones_adopcion/adopcion/${adopcionId}`)
        this.peticiones = data
      } catch (e) {
        console.error('Error al cargar peticiones:', e.response)
        this.errorPeticiones = (e.response && e.response.data && e.response.data.msg) || 'Error al cargar peticiones'
      }
    },

    // ===== Solicitudes =====
    puedeSolicitar (adopcion) {
      if (!adopcion) return false
      if (adopcion.adopcion_cerrada) return false
      if (adopcion.dueño_anterior_id === this.usuarioId) return false
      return true
    },

    estadoPeticionUsuario (adopcion) {
      if (!adopcion) return ''
      const peticion = this.misPeticiones.find(p => p.adopcion_id === adopcion.id)
      return (peticion && peticion.estado_peticion ? peticion.estado_peticion : '').toLowerCase()
    },

    tienePeticionPendiente (adopcion) {
      return this.estadoPeticionUsuario(adopcion) === 'pendiente'
    },

    abrirModalSolicitud (adopcion) {
      this.adopcionSolicitud = adopcion
      this.razonSolicitud = ''
      this.errorSolicitud = ''
      this.mostrarSolicitud = true
    },

    cerrarSolicitud () {
      this.mostrarSolicitud = false
      this.adopcionSolicitud = null
      this.razonSolicitud = ''
      this.errorSolicitud = ''
    },

    async crearSolicitud () {
      this.errorSolicitud = ''
      if (!this.razonSolicitud.trim()) {
        this.errorSolicitud = 'Razón de adopción requerida'
        return
      }
      if (this.razonSolicitud.length > 255) {
        this.errorSolicitud = 'La razón no puede tener más de 255 caracteres'
        return
      }

      try {
        await api.post('/peticiones_adopcion/crear', {
          adopcion_id: this.adopcionSolicitud.id,
          razon_adopcion: this.razonSolicitud.trim()
        })
        this.cerrarSolicitud()
        await this.cargarMisPeticiones()
      } catch (e) {
        console.error('Error al crear solicitud:', e.response)
        this.errorSolicitud = (e.response && e.response.data && e.response.data.msg) || 'Error al crear solicitud'
      }
    },

    // ===== Crear adopción =====
    async abrirModalCrear () {
      this.errorCreacion = ''
      this.nuevaAdopcion = { mascota_id: '', descripcion: '' }
      await this.cargarMisMascotas()
      this.mostrarCrear = true
    },

    cerrarCrear () {
      this.mostrarCrear = false
      this.nuevaAdopcion = { mascota_id: '', descripcion: '' }
      this.errorCreacion = ''
    },

    async crearAdopcion () {
      this.errorCreacion = ''
      const descripcion = (this.nuevaAdopcion.descripcion || '').trim()
      if (!this.nuevaAdopcion.mascota_id) {
        this.errorCreacion = 'Selecciona una mascota'
        return
      }
      if (!descripcion) {
        this.errorCreacion = 'Descripción requerida'
        return
      }
      if (descripcion.length > 255) {
        this.errorCreacion = 'La descripción no puede tener más de 255 caracteres'
        return
      }

      try {
        await api.post('/adopciones/crear', {
          mascota_id: this.nuevaAdopcion.mascota_id,
          descripcion
        })
        this.cerrarCrear()
        await this.cargarMisAdopciones()
        await this.cargarAdopcionesClinica()
      } catch (e) {
        console.error('Error al crear adopción:', e.response)
        this.errorCreacion = (e.response && e.response.data && e.response.data.msg) || 'Error al crear adopción'
      }
    },

    // ===== Aprobar / Rechazar =====
    badgeEstado (estado) {
      const e = (estado || '').toLowerCase()
      if (e === 'aprobada') return 'badge-aprobada'
      if (e === 'rechazada') return 'badge-rechazada'
      return 'badge-pendiente'
    },

    puedeDecidir (peticion) {
      if (!this.adopcionSeleccionada || this.adopcionSeleccionada.adopcion_cerrada) return false
      const e = (peticion.estado_peticion || '').toLowerCase()
      return e === 'pendiente'
    },

    abrirModalAceptar (peticion) {
      this.peticionAccion = peticion
      this.mostrarAceptar = true
    },

    cerrarAceptar () {
      this.mostrarAceptar = false
      this.peticionAccion = null
    },

    abrirModalRechazar (peticion) {
      this.peticionAccion = peticion
      this.mostrarRechazar = true
    },

    cerrarRechazar () {
      this.mostrarRechazar = false
      this.peticionAccion = null
    },

    async aceptarPeticion () {
      try {
        await api.put(`/peticiones_adopcion/aceptar/${this.peticionAccion.id}`)
        this.cerrarAceptar()

        await this.cargarMisAdopciones()
        if (this.adopcionSeleccionada) {
          const updated = this.misAdopciones.find(a => a.id === this.adopcionSeleccionada.id)
          this.adopcionSeleccionada = updated || null
          if (this.adopcionSeleccionada) await this.cargarPeticionesDeAdopcion(this.adopcionSeleccionada.id)
        }
      } catch (e) {
        console.error('Error al aceptar petición:', e.response)
        this.errorPeticiones = (e.response && e.response.data && e.response.data.msg) || 'Error al aceptar petición'
      }
    },

    async rechazarPeticion () {
      try {
        await api.put(`/peticiones_adopcion/rechazar/${this.peticionAccion.id}`)
        this.cerrarRechazar()
        if (this.adopcionSeleccionada) await this.cargarPeticionesDeAdopcion(this.adopcionSeleccionada.id)
      } catch (e) {
        console.error('Error al rechazar petición:', e.response)
        this.errorPeticiones = (e.response && e.response.data && e.response.data.msg) || 'Error al rechazar petición'
      }
    },

    // ===== Eliminar adopción =====
    abrirModalEliminar () {
      this.errorEliminar = ''
      this.mostrarEliminar = true
    },

    cerrarEliminar () {
      this.mostrarEliminar = false
      this.errorEliminar = ''
    },

    async eliminarAdopcion () {
      this.errorEliminar = ''
      if (!this.adopcionSeleccionada) return

      try {
        await api.delete(`/adopciones/eliminar/${this.adopcionSeleccionada.id}`)
        this.cerrarEliminar()
        await this.cargarMisAdopciones()
        await this.cargarAdopcionesClinica()
      } catch (e) {
        console.error('Error al eliminar adopción:', e.response)
        this.errorEliminar = (e.response && e.response.data && e.response.data.msg) || 'Error al eliminar adopción'
      }
    },

    formatearFechaSimple (iso) {
      const d = new Date(iso)
      if (Number.isNaN(d.getTime())) return iso
      const dd = String(d.getDate()).padStart(2, '0')
      const mm = String(d.getMonth() + 1).padStart(2, '0')
      const yyyy = d.getFullYear()
      const hh = String(d.getHours()).padStart(2, '0')
      const min = String(d.getMinutes()).padStart(2, '0')
      return `${dd}/${mm}/${yyyy} ${hh}:${min}`
    }
  }
}
</script>

<style scoped>
@import './css/Adopciones.css';
</style>
