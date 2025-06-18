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
          <button @click="eliminarVisita(v.id)">🗑️</button>
        </div>
      </li>
    </ul>
    <p v-else class="no-visitas">No hay visitas registradas.</p>

    <!-- Modal Crear -->
    <div class="modal-overlay" v-if="mostrarCrear">
      <div class="modal">
        <h3>Crear Visita</h3>
        <label>Clínica</label>
        <select v-model="nueva.clinica_id" @change="onChangeClinica" required>
          <option disabled value="">Selecciona clínica</option>
          <option v-for="c in clinicas" :key="c.id" :value="c.id">
            {{ c.nombre }}
          </option>
        </select>

        <label>Propietario</label>
        <select v-model="nueva.dueno_id" @change="onChangePropietario" required>
          <option disabled value="">Selecciona dueño</option>
          <option v-for="p in propietarios" :key="p.id" :value="p.id">
            {{ p.usuario }}
          </option>
        </select>

        <label>Mascota</label>
        <select v-model="nueva.mascota_id" @change="cargarVisitas" required>
          <option disabled value="">Selecciona mascota</option>
          <option v-for="m in mascotasDelPropietario" :key="m.id" :value="m.id">
            {{ m.nombre }}
          </option>
        </select>

        <label>Fecha y hora</label>
        <input type="datetime-local" v-model="nueva.date_time" required />

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
        <input type="datetime-local" v-model="seleccionada.date_time" />

        <label>Descripción</label>
        <input v-model="seleccionada.description" />

        <div class="modal-buttons">
          <button @click="editarVisita">Actualizar</button>
          <button class="cancelar" @click="cerrarEditar">Cancelar</button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="no-auth">
    <p class="error">No estás autorizado. Por favor, inicia sesión como dueño de clínica.</p>
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
        if (this.info_usuario.tipo !== 'prop_clinica') {
          this.jwtValido = false
          return
        }
        this.jwtValido = true
        this.usuarioId = this.info_usuario.id
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
      this.cargarClinicas()
    },

    async cargarClinicas () {
      try {
        const { data } = await api.get(`/clinicas/listar/${this.usuarioId}`)
        this.clinicas = data
      } catch (e) {
        console.error('Error al cargar clínicas:', e)
      }
    },

    async onChangeClinica () {
      this.nueva.dueno_id = ''
      this.nueva.mascota_id = ''
      this.propietarios = []
      this.mascotasDelPropietario = []
      try {
        const { data } = await api.get(`/clinicas/${this.nueva.clinica_id}/props_mascotas`)
        this.propietarios = data
      } catch (e) {
        console.error('Error al cargar propietarios:', e)
      }
    },

    async onChangePropietario () {
      this.nueva.mascota_id = ''
      this.mascotasDelPropietario = []
      try {
        const { data } = await api.get(
          `/clinicas/${this.nueva.clinica_id}` +
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
          `/clinicas/${this.nueva.clinica_id}` +
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
          `/clinicas/${this.nueva.clinica_id}` +
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
          `/clinicas/${this.nueva.clinica_id}` +
          `/props_mascotas/${this.nueva.dueno_id}` +
          `/mascotas/${this.nueva.mascota_id}/visitas/${this.seleccionada.id}`,
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

    async eliminarVisita (id) {
      if (!confirm('¿Eliminar esta visita?')) return
      try {
        await api.delete(
          `/clinicas/${this.nueva.clinica_id}` +
          `/props_mascotas/${this.nueva.dueno_id}` +
          `/mascotas/${this.nueva.mascota_id}/visitas/${id}`
        )
        await this.fetchMisVisitas()
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
