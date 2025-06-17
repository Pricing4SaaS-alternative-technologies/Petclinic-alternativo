<template>
  <div class="visitas-container">
    <h2>🩺 Visitas</h2>
    <button class="btn-crear" @click="openCrear">➕ Nueva Visita</button>

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

        <!-- 1) Clínica -->
        <label>Clínica</label>
        <select v-model="nueva.clinica_id" @change="onChangeClinica" required>
          <option disabled value="">Selecciona clínica</option>
          <option v-for="c in clinicas" :key="c.id" :value="c.id">
            {{ c.nombre }}
          </option>
        </select>

        <!-- 2) Propietario de mascota -->
        <label>Propietario</label>
        <select v-model="nueva.dueno_id" @change="onChangePropietario" required>
          <option disabled value="">Selecciona dueño</option>
          <option v-for="p in propietarios" :key="p.id" :value="p.id">
            {{ p.usuario }}
          </option>
        </select>

        <!-- 3) Mascota -->
        <label>Mascota</label>
        <select v-model="nueva.mascota_id" required>
          <option disabled value="">Selecciona mascota</option>
          <option v-for="m in mascotasDelPropietario" :key="m.id" :value="m.id">
            {{ m.nombre }}
          </option>
        </select>

        <!-- 4) Fecha y Descripción -->
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

    <!-- Modal Editar (igual que antes) -->
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
import api from '@/api/axios'

export default {
  name: 'HomeVisitas',
  data () {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return {
      usuarioId: user.id,
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
  methods: {
    // abre modal y carga clínicas
    openCrear () {
      this.mostrarCrear = true
      this.nueva = { clinica_id: '', dueno_id: '', mascota_id: '', date_time: '', description: '' }
      this.propietarios = []
      this.mascotasDelPropietario = []
      this.visitas = []
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

    // tras elegir clínica, cargo propietarios
    async onChangeClinica () {
      this.nueva.dueno_id = ''
      this.nueva.mascota_id = ''
      this.propietarios = []
      this.mascotasDelPropietario = []
      try {
        const { data } = await api.get(
          `/clinicas/${this.nueva.clinica_id}/props_mascotas`
        )
        this.propietarios = data
      } catch (e) {
        console.error('Error al cargar propietarios:', e)
      }
    },

    // tras elegir propietario, cargo mascotas
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

    // POST visita
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
        this.cerrarCrear()
        this.cargarVisitas()
      } catch (e) {
        console.error('Error al crear visita:', e)
      }
    },

    // GET visitas de la mascota seleccionada
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

    // PATCH visita
    async editarVisita () {
      try {
        await api.patch(
          `/clinicas/${this.nueva.clinica_id}` +
          `/props_mascotas/${this.nueva.dueno_id}` +
          `/mascotas/${this.nueva.mascota_id}/visitas/${this.seleccionada.id}`,
          this.seleccionada
        )
        this.cerrarEditar()
        this.cargarVisitas()
      } catch (e) {
        console.error('Error al editar visita:', e)
      }
    },

    // DELETE visita
    async eliminarVisita (id) {
      if (!confirm('¿Eliminar esta visita?')) return
      try {
        await api.delete(
          `/clinicas/${this.nueva.clinica_id}` +
          `/props_mascotas/${this.nueva.dueno_id}` +
          `/mascotas/${this.nueva.mascota_id}/visitas/${id}`
        )
        this.cargarVisitas()
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
      this.nueva = { clinica_id: '', dueno_id: '', mascota_id: '', date_time: '', description: '' }
    },

    cerrarEditar () {
      this.mostrarEditar = false
      this.seleccionada = null
    },

    formatearFecha (iso) {
      const [d, t] = iso.split('T')
      return `${d.replace(/-/g, '/')} ${t.substring(0, 5)}`
    }
  }
}
</script>

<style scoped>
@import './css/HomeVisitas.css';
</style>
