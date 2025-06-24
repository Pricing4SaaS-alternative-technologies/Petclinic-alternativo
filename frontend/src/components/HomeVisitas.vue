<template>
  <div class="visitas-container" v-if="jwtValido">
    <h2>🩺 Visitas</h2>
    <button class="btn-crear" @click="openCrear">➕ Nueva Visita</button>

    <ul v-if="visitas.length" class="visita-lista">
      <li v-for="v in visitas" :key="v.id" class="visita-card">
        <span>{{ formatearFecha(v.date_time) }}</span>
        <span>{{ v.dueno }}</span>
        <span>{{ v.mascota }}</span>
        <span>{{ v.description }}</span>
        <div class="acciones">
          <button @click="abrirEditar(v)">✏️</button>
          <button @click="abrirEliminar(v)">🗑️</button>
        </div>
      </li>
    </ul>
    <p v-else class="no-visitas">No hay visitas registradas.</p>

    <!-- Modal Crear -->
    <div class="modal-overlay" v-if="mostrarCrear">
      <div class="modal">
        <h3>Crear Visita</h3>
        <label>Propietario</label>
        <select v-model="nueva.dueno_id" @change="cargarMascotasDelPropietario" required>
          <option disabled value="">Selecciona dueño</option>
          <option v-for="p in propietarios" :key="p.id" :value="p.id">
            {{ p.usuario }}
          </option>
        </select>

        <label>Mascota</label>
        <select v-model="nueva.mascota_id" required>
          <option disabled value="">Selecciona mascota</option>
          <option v-for="m in mascotasDelPropietario" :key="m.id" :value="m.id">
            {{ m.nombre }}
          </option>
        </select>

        <label>Fecha y hora</label>
        <input type="date" v-model="nueva.date_time" required />

        <label>Descripción</label>
        <input v-model="nueva.description" required />

        <div class="modal-buttons">
          <button @click="crearVisita">Guardar</button>
          <button class="cancelar" @click="cerrarCrear">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Modal Editar -->
    <div class="modal-overlay" v-if="mostrarEditar">
      <div class="modal">
        <h3>Editar Visita</h3>
        <label>Fecha y hora</label>
        <input type="date" v-model="seleccionada.date_time" />

        <label>Descripción</label>
        <input v-model="seleccionada.description" />

        <div class="modal-buttons">
          <button @click="editarVisita">Actualizar</button>
          <button class="cancelar" @click="cerrarEditar">Cancelar</button>
        </div>
      </div>
    </div>
    <!-- Modal Eliminar -->
    <div class="modal-overlay" v-if="mostrarEliminar">
      <div class="modal">
        <h3>Eliminar Visita</h3>
        <p>¿Seguro que quieres eliminar la visita del {{ formatearFecha(seleccionadaEliminar.date_time) }}?</p>
        <div class="modal-buttons">
          <button @click="confirmarEliminarVisita">Eliminar</button>
          <button class="cancelar" @click="cerrarEliminar">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="no-auth">
    <p class="error">No estás autorizado. Por favor, inicia sesión como veterinario.</p>
  </div>
</template>

<script>
import api from '@/api/axios'

export default {
  name: 'HomeVisitas',
  data () {
    return {
      info_usuario: null,
      jwtValido: false,
      usuarioId: null,
      clinicas: [],
      propietarios: [],
      mascotasDelPropietario: [],
      visitas: [],
      mostrarCrear: false,
      mostrarEditar: false,
      mostrarEliminar: false,
      seleccionadaEliminar: null,
      seleccionada: null,
      nueva: {
        clinica_id: '',
        dueno_id: '',
        mascota_id: '',
        date_time: '',
        description: ''
      }
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
        if (this.info_usuario.tipo !== 'veterinario') {
          this.jwtValido = false
          return
        }
        this.jwtValido = true
        this.usuarioId = this.info_usuario.id
        this.clinicaId = this.info_usuario.clinica_id
        this.fetchMisVisitas()
      } catch (e) {
        console.error('Error al parsear usuario:', e)
        this.jwtValido = false
      }
    },

    // carga todas las visitas del dueño de clínica
    async fetchMisVisitas () {
      try {
        const { data } = await api.get('/visitas/mine')
        this.visitas = data
      } catch (e) {
        console.error('No se pudieron cargar tus visitas:', e)
      }
    },

    openCrear () {
      this.mostrarCrear = true
      this.nueva = { clinica_id: '', dueno_id: '', mascota_id: '', date_time: '', description: '' }
      this.propietarios = []
      this.mascotasDelPropietario = []
      this.cargarPropietariosMascotas()
    },

    async cargarPropietariosMascotas () {
      this.nueva.mascota_id = ''
      this.mascotasDelPropietario = []
      try {
        const { data } = await api.get(`/clinicas/${this.clinicaId}/props_mascotas`)
        this.propietarios = data
      } catch (e) {
        console.error('Error al cargar propietarios:', e)
      }
    },

    async cargarMascotasDelPropietario () {
      this.nueva.mascota_id = ''
      this.mascotasDelPropietario = []
      try {
        const { data } = await api.get(
          `/clinicas/${this.clinicaId}` +
          `/props_mascotas/${this.nueva.dueno_id}/mascotas`
        )
        this.mascotasDelPropietario = data
      } catch (e) {
        console.error('Error al cargar mascotas:', e)
      }
    },

    async cargarVisitas () {
      if (!this.nueva.mascota_id) return
      try {
        const { data } = await api.get(
          `/clinicas/${this.clinicaId}` +
          `/props_mascotas/${this.nueva.dueno_id}` +
          `/mascotas/${this.nueva.mascota_id}/visitas`
        )
        this.visitas = data
      } catch (e) {
        console.error('Error al cargar visitas:', e)
      }
    },

    async crearVisita () {
      try {
        await api.post(
          `/clinicas/${this.clinicaId}` +
          `/props_mascotas/${this.nueva.dueno_id}` +
          `/mascotas/${this.nueva.mascota_id}/visitas`,
          {
            date_time: this.nueva.date_time,
            description: this.nueva.description
          }
        )
        await this.fetchMisVisitas()
        this.cerrarCrear()
      } catch (e) {
        console.error('Error al crear visita:', e)
      }
    },

    async editarVisita () {
      try {
        await api.patch(
          `/clinicas/${this.clinicaId}` +
          `/props_mascotas/${this.seleccionada.dueno_id}` +
          `/mascotas/${this.seleccionada.mascota_id}/visitas/${this.seleccionada.id}`,
          {
            date_time: this.seleccionada.date_time,
            description: this.seleccionada.description
          }
        )
        await this.fetchMisVisitas()
        this.cerrarEditar()
      } catch (e) {
        console.error('Error al editar visita:', e)
      }
    },

    async confirmarEliminarVisita () {
      try {
        await api.delete(
          `/clinicas/${this.clinicaId}` +
          `/props_mascotas/${this.seleccionadaEliminar.dueno_id}` +
          `/mascotas/${this.seleccionadaEliminar.mascota_id}/visitas/${this.seleccionadaEliminar.id}`
        )
        await this.fetchMisVisitas()
        this.cerrarEliminar()
      } catch (e) {
        console.error('Error al eliminar visita:', e)
      }
    },

    abrirEditar (v) {
      this.seleccionada = { ...v }
      this.mostrarEditar = true
    },

    cerrarCrear () {
      this.mostrarCrear = false
    },

    cerrarEditar () {
      this.mostrarEditar = false
      this.seleccionada = null
    },

    abrirEliminar (v) {
      this.seleccionadaEliminar = { ...v }
      this.mostrarEliminar = true
    },

    cerrarEliminar (v) {
      this.seleccionadaEliminar = null
      this.mostrarEliminar = false
    },

    formatearFecha (iso) {
      const [year, month, day] = iso.split('T')[0].split('-')
      return `${day}/${month}/${year}`
    }
  }
}
</script>

<style scoped>
@import './css/HomeVisitas.css';
</style>
