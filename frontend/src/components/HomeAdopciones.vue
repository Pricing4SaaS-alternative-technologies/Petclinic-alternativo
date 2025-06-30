<template>
  <div class="adopciones-container" v-if="jwtValido">
    <!-- Header -->
    <div class="adopciones-header">
      <h2>🐾 Adopciones</h2>
      <button class="btn-crear" @click="openCrear">➕ Nueva Adopción</button>
    </div>

    <!-- Tres columnas -->
    <div class="adopciones-body">
      <!-- Izquierda: Mis Adopciones -->
      <section class="panel izquierda">
        <h3>Mis Adopciones</h3>
        <ul v-if="misAdopCreadas.length">
          <li v-for="a in misAdopCreadas" :key="a.id" class="card">
            <span class="mascota">{{ a.mascota.nombre }}</span>
            <span class="desc">{{ a.descripcion }}</span>

            <!-- CREADA: editar / borrar -->
            <template v-if="a.estado === 'creada'">
              <button @click="abrirEditar(a)">✏️</button>
              <button @click="abrirConfirmEliminar(a.id)">🗑️</button>
            </template>
            <!-- PENDIENTE: aceptar / rechazar -->
            <template v-else-if="a.estado === 'pendiente'">
              <span>Solicita: {{ a.dueño_nuevo.usuario }}</span>
              <button @click="aceptar(a.id)">✅</button>
              <button @click="rechazar(a.id)">❌</button>
            </template>
            <!-- APROBADA/RECHAZADA: solo lectura -->
            <template v-else>
              <span>Estado: {{ a.estado }}</span>
            </template>
          </li>
        </ul>
        <p v-else class="no-data">No tienes adopciones.</p>
      </section>

      <!-- Centro: Disponibles -->
      <section class="panel centro">
        <h3>Adopciones Disponibles</h3>
        <ul v-if="disponibles.length">
          <li v-for="a in disponibles" :key="a.id" class="card">
            <span>{{ a.mascota.nombre }}</span>
            <span>{{ a.descripcion }}</span>
            <button @click="solicitar(a.id)">Solicitar</button>
          </li>
        </ul>
        <p v-else class="no-data">No hay adopciones disponibles.</p>
      </section>

      <!-- Derecha: Mis Solicitudes -->
      <section class="panel derecha">
        <h3>Mis Solicitudes</h3>
        <ul v-if="misSolicitudes.length">
          <li v-for="a in misSolicitudes" :key="a.id" class="card">
            <span>{{ a.mascota.nombre }}</span>
            <span>Dueño actual: {{ a.dueño_anterior.usuario }}</span>
            <span>Estado: {{ a.estado }}</span>
          </li>
        </ul>
        <p v-else class="no-data">No tienes solicitudes.</p>
      </section>
    </div>

    <!-- Modal Crear -->
    <div class="modal-overlay" v-if="mostrarCrear">
      <div class="modal">
        <h3>Proponer Adopción</h3>
        <label>Selecciona mascota</label>
        <select v-model="nueva.mascota_id">
          <option disabled value="">--Elige--</option>
          <option v-for="m in misMascotas" :key="m.id" :value="m.id">
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

    <div class="modal-overlay" v-if="mostrarEditar">
    <div class="modal">
      <h3>Editar Descripción</h3>
      <label>Nueva descripción</label>
      <input v-model="editar.descripcion" />
      <div class="modal-buttons">
        <button @click="actualizarEditar">Guardar</button>
        <button class="cancelar" @click="cerrarEditar">Cancelar</button>
      </div>
    </div>
  </div>

  <!-- Modal Confirmar Eliminación -->
  <div class="modal-overlay" v-if="mostrarConfirmEliminar">
    <div class="modal">
      <h3>¿Eliminar adopción?</h3>
      <p>¿Estás seguro de que deseas eliminar esta adopción?</p>
      <div class="modal-buttons">
        <button @click="confirmarEliminar">Eliminar</button>
        <button class="cancelar" @click="cerrarConfirmEliminar">Cancelar</button>
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
      misAdopCreadas: [],
      disponibles: [],
      misSolicitudes: [],
      misMascotas: [],
      mostrarCrear: false,
      nueva: { mascota_id: '', descripcion: '' },
      mostrarEditar: false,
      editar: { id: null, descripcion: '' },
      mostrarConfirmEliminar: false,
      eliminarId: null
    }
  },
  async created () {
    const token = localStorage.getItem('jwt')
    const raw = localStorage.getItem('user')
    if (!token || !raw) return
    this.info_usuario = JSON.parse(raw)
    if (this.info_usuario.tipo !== 'prop_mascota') return
    this.jwtValido = true

    // carga todo de una vez
    const { data } = await api.get('/adopciones')
    this.todas = data
    this.actualizarListas()
    await this.fetchMisMascotas()
  },

  methods: {
    async recargar () {
      const { data } = await api.get('/adopciones')
      this.todas = data
      this.actualizarListas()
      this.fetchMisMascotas()
    },
    actualizarListas () {
      const u = this.info_usuario.id

      // 1) “Mis adopciones” = tú eres dueño_anterior
      this.misAdopCreadas = this.todas.filter(a =>
        a.dueño_anterior && a.dueño_anterior.id === u
      )

      // 2) “Disponibles” = estado CREADA y ni dueño_anterior ni dueño_nuevo son tú
      this.disponibles = this.todas.filter(a =>
        a.estado === 'creada' &&
        (!a.dueño_anterior || a.dueño_anterior.id !== u) &&
        (!a.dueño_nuevo || a.dueño_nuevo.id !== u)
      )

      // 3) “Mis solicitudes” = estado PENDIENTE y tú eres dueño_nuevo
      this.misSolicitudes = this.todas.filter(a =>
        a.estado === 'pendiente' &&
        a.dueño_nuevo && a.dueño_nuevo.id === u
      )
    },
    fetchMisCreadas () {
      return api.get('/adopciones/mine/creadas')
        .then(r => (this.misAdopCreadas = r.data))
    },
    fetchDisponibles () {
      return api.get('/adopciones')
        .then(r => {
          this.disponibles = r.data.filter(a =>
            a.estado === 'creada' &&
            (!a.dueño_nuevo || a.dueño_nuevo.id !== this.info_usuario.id)
          )
        })
    },
    fetchMisSolicitudes () {
      return api.get('/adopciones/mine/pendientes')
        .then(r => (this.misSolicitudes = r.data))
    },
    fetchMisMascotas () {
      return api.get('/mascotas/listar-tus-mascotas')
        .then(r => (this.misMascotas = r.data))
    },
    openCrear () {
      this.mostrarCrear = true
      this.fetchMisMascotas()
    },
    cerrarCrear () {
      this.mostrarCrear = false
      this.nueva = { mascota_id: '', descripcion: '' }
    },
    crear () {
      api.post('/adopciones', this.nueva)
        .then(() => {
          this.cerrarCrear()
          this.recargar()
        })
        .catch(err => console.error(err))
    },
    abrirEditar (a) {
      this.editar = { id: a.id, descripcion: a.descripcion }
      this.mostrarEditar = true
    },
    cerrarEditar () {
      this.mostrarEditar = false
      this.editar = { id: null, descripcion: '' }
    },
    cerrarConfirmEliminar () {
      this.mostrarConfirmEliminar = false
      this.eliminarId = null
    },
    abrirConfirmEliminar (id) {
      this.eliminarId = id
      this.mostrarConfirmEliminar = true
    },
    confirmarEliminar () {
      api.delete(`/adopciones/${this.eliminarId}`)
        .then(() => {
          this.cerrarConfirmEliminar()
          this.recargar()
        })
        .catch(err => console.error(err))
    },
    solicitar (id) {
      if (!confirm('¿Confirmas solicitud?')) return
      api.put(`/adopciones/${id}/solicitar`)
        .then(() => this.recargar())
    },
    aceptar (id) {
      api.put(`/adopciones/${id}/aceptar`)
        .then(() => this.recargar())
    },
    rechazar (id) {
      api.put(`/adopciones/${id}/rechazar`)
        .then(() => this.recargar())
    },
    actualizarEditar () {
      api.patch(`/adopciones/${this.editar.id}`, { descripcion: this.editar.descripcion })
        .then(() => {
          this.cerrarEditar()
          this.recargar()
        })
    },
    borrar (id) {
      api.delete(`/adopciones/${id}`)
        .then(() => this.recargar())
    }
  }
}
</script>

<style scoped>
@import './css/HomeAdopciones.css';
</style>
