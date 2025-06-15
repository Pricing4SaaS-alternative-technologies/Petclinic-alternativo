<template>
  <div class="visitas-container">
    <h2>🩺 Visitas</h2>
    <button class="btn-crear" @click="mostrarCrear = true">➕ Nueva Visita</button>

    <ul v-if="visitas.length" class="visita-lista">
      <li v-for="v in visitas" :key="v.id" class="visita-card">
        <span>{{ formatearFecha(v.date_time) }}</span> –
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
        <label>Fecha y hora</label>
        <input type="datetime-local" v-model="nueva.date_time" />
        <label>Descripción</label>
        <input v-model="nueva.description" />
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
</template>

<script>
import axios from 'axios'
export default {
  name: 'HomeVisitas',
  data () {
    return {
      visitas: [],
      mostrarCrear: false,
      mostrarEditar: false,
      nueva: { date_time: '', description: '' },
      seleccionada: null,

      clinicaId: localStorage.getItem('clinica_id'),
      usuarioId: localStorage.getItem('usuario_id'),
      mascotaId: localStorage.getItem('mascota_id')
    }
  },
  methods: {
    async cargarVisitas () {
      const url = `/api/clinicas/${this.clinicaId}/props_mascotas/${this.usuarioId}/mascotas/${this.mascotaId}/visitas`
      const { data } = await axios.get(url, this._authHeader())
      this.visitas = data
    },
    async crearVisita () {
      const url = `/api/clinicas/${this.clinicaId}/props_mascotas/${this.usuarioId}/mascotas/${this.mascotaId}/visitas`
      await axios.post(url, this.nueva, this._authHeader())
      this.cerrarCrear()
      await this.cargarVisitas()
    },
    async editarVisita () {
      const url = `/api/clinicas/${this.clinicaId}/props_mascotas/${this.usuarioId}/mascotas/${this.mascotaId}/visitas/${this.seleccionada.id}`
      await axios.patch(url, this.seleccionada, this._authHeader())
      this.cerrarEditar()
      await this.cargarVisitas()
    },
    async eliminarVisita (id) {
      if (!confirm('¿Eliminar esta visita?')) return
      const url = `/api/clinicas/${this.clinicaId}/props_mascotas/${this.usuarioId}/mascotas/${this.mascotaId}/visitas/${id}`
      await axios.delete(url, this._authHeader())
      await this.cargarVisitas()
    },
    abrirEditar (v) {
      this.seleccionada = { ...v }
      this.mostrarEditar = true
    },
    cerrarCrear () {
      this.mostrarCrear = false
      this.nueva = { date_time: '', description: '' }
    },
    cerrarEditar () {
      this.mostrarEditar = false
      this.seleccionada = null
    },
    formatearFecha (iso) {
      const [d, t] = iso.split('T')
      return `${d.replace(/-/g, '/')} ${t.substring(0, 5)}`
    },
    _authHeader () {
      return { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
    }
  },
  created () {
    this.cargarVisitas()
  }
}
</script>

<style scoped>
@import './css/HomeVisitas.css';
</style>
