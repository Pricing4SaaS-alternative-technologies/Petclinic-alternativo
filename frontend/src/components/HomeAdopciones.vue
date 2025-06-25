<template>
  <div class="adopciones-container" v-if="jwtValido">
    <h2>🐾 Adopciones</h2>
    <button class="btn-crear" @click="openCrear">➕ Nueva Adopción</button>

    <section>
      <h3>Todas las adopciones</h3>
      <ul class="adop-lista">
        <li v-for="a in todas" :key="a.id">
          <span>{{ formFecha(a.fecha_creacion) }}</span>
          <span>{{ a.mascota.nombre }}</span>
          <span>Dueño actual: {{ a.dueño_anterior.usuario }}</span>
          <span>Estado: {{ a.estado }}</span>
        </li>
      </ul>
    </section>

    <section>
      <h3>Mis adopciones pendientes</h3>
      <ul class="adop-lista">
        <li v-for="a in pendientes" :key="a.id">
          <span>
            {{ a.mascota.nombre }}
            (solicitante: {{ a.dueño_nuevo ? a.dueño_nuevo.usuario : '–' }})
          </span>
          <button @click="aceptar(a.id)">Aceptar</button>
          <button @click="rechazar(a.id)">Rechazar</button>
        </li>
        <li v-if="!pendientes.length" class="no-data">No tienes propuestas pendientes</li>
      </ul>
    </section>

    <!-- Modal Crear -->
    <div class="modal-overlay" v-if="mostrarCrear">
      <div class="modal">
        <h3>Proponer Adopción</h3>
        <label>Selecciona mascota a adoptar</label>
        <select v-model="nueva.mascota_id">
          <option disabled value="">--elige--</option>
          <option
            v-for="m in misMascotas" :key="m.id" :value="m.id">
            {{ m.nombre }}
          </option>
        </select>
        <label>Descripción</label>
        <input v-model="nueva.descripcion" />
        <div class="modal-buttons">
          <button @click="crear">Enviar</button>
          <button class="cancelar" @click="cerrarCrear">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
  <p v-else class="error">Inicia sesión como dueño de mascota.</p>
</template>

<script>
import api from '@/api/axios'
export default {
  data () {
    return {
      jwtValido: false,
      info_usuario: null,
      todas: [],
      pendientes: [],
      misMascotas: [],
      mostrarCrear: false,
      nueva: { mascota_id: '', descripcion: '' }
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
    async checkAuth () {
      const token = localStorage.getItem('jwt')
      const raw = localStorage.getItem('user')
      if (!token || !raw) {
        this.jwtValido = false
        return false
      }
      this.info_usuario = JSON.parse(raw)
      if (this.info_usuario.tipo !== 'prop_mascota') {
        this.jwtValido = false
        return false
      }
      this.jwtValido = true
      await Promise.all([
        this.fetchTodas(),
        this.fetchPendientes(),
        this.fetchMisMascotas()
      ])
    },
    async fetchTodas () {
      const { data } = await api.get('/adopciones')
      this.todas = data
    },
    async fetchPendientes () {
      const { data } = await api.get('/adopciones/mine/pendientes')
      this.pendientes = data
    },
    async fetchMisMascotas () {
      const { data } = await api.get('/mascotas/listar-tus-mascotas')
      this.misMascotas = data
    },
    formFecha (iso) {
      const [y, m, d] = iso.split('T')[0].split('-')
      return `${d}/${m}/${y}`
    },
    openCrear () { this.mostrarCrear = true },
    cerrarCrear () {
      this.mostrarCrear = false
      this.nueva = { mascota_id: '', descripcion: '' }
    },
    async crear () {
      await api.post('/adopciones', this.nueva)
      this.cerrarCrear()
      this.fetchTodas()
      this.fetchPendientes()
    },
    async aceptar (id) {
      await api.put(`/adopciones/${id}/aceptar`)
      this.fetchTodas(); this.fetchPendientes()
    },
    async rechazar (id) {
      await api.put(`/adopciones/${id}/rechazar`)
      this.fetchTodas(); this.fetchPendientes()
    }
  }
}
</script>

<style scoped>
@import './css/HomeAdopciones.css';
</style>
