<template>
  <div class="mascotas-container">
    <h2>🐶 Mis Mascotas</h2>

    <button class="btn-crear" @click="mostrarModal = true">➕ Añadir Mascota</button>

    <ul v-if="mascotas.length" class="mascota-lista">
      <li v-for="mascota in mascotas" :key="mascota.id" class="mascota-card">
        <strong>{{ mascota.nombre }}</strong>
        <button @click="abrirEdicion(mascota)">✏️</button>
        <button @click="eliminarMascota(mascota.id)">🗑️</button>
        <br />
        <span>Tipo: {{ mascota.tipo }}</span><br />
        <span>Cumpleaños: {{ formatearFecha(mascota.cumpleaños) }}</span>
        </li>
    </ul>
    <p v-else class="no-mascotas">No tienes mascotas registradas.</p>

    <!-- Modal para crear mascota -->
    <div class="modal-overlay" v-if="mostrarModal">
      <div class="modal">
        <h3>Nueva Mascota</h3>
        <form @submit.prevent="crearMascota">
          <label>Nombre:</label>
          <input v-model="nuevaMascota.nombre" required />

          <label>Tipo:</label>
          <select v-model="nuevaMascota.tipo" required>
            <option disabled value="">Seleccione un tipo</option>
            <option>PERRO</option>
            <option>GATO</option>
            <option>REPTIL</option>
            <option>SERPIENTE</option>
            <option>PAJARO</option>
            <option>HAMSTER</option>
            <option>TORTUGA</option>
          </select>

          <label>Cumpleaños:</label>
          <input type="date" v-model="nuevaMascota.cumpleaños" required />

          <div class="modal-buttons">
            <button type="submit">Guardar</button>
            <button type="button" class="cancelar" @click="mostrarModal = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
    <div class="modal-overlay" v-if="mostrarModalEditar">
  <div class="modal">
    <h3>Editar Nombre</h3>
    <form @submit.prevent="editarNombreMascota">
      <label>Nuevo nombre:</label>
      <input v-model="mascotaSeleccionada.nombre" required />
      <div class="modal-buttons">
        <button type="submit">Guardar</button>
        <button type="button" class="cancelar" @click="cerrarEdicion">Cancelar</button>
      </div>
    </form>
  </div>
</div>

  </div>
</template>

<style src="./css/misMascotas.css"></style>
<script>
import axios from 'axios'

export default {
  name: 'MisMascotas',
  data () {
    return {
      mascotas: [],
      mostrarModal: false,
      mostrarModalEditar: false,
      nuevaMascota: {
        nombre: '',
        cumpleaños: '',
        tipo: ''
      },
      mascotaSeleccionada: null
    }
  },
  methods: {
    async cargarMascotas () {
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user || !user.id) return

      try {
        const res = await axios.get(`http://localhost:5000/api/mascotas/${user.id}`)
        this.mascotas = res.data
      } catch (error) {
        console.error('Error al cargar mascotas:', error)
      }
    },
    async crearMascota () {
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user || !user.id) return

      try {
        await axios.post('http://localhost:5000/api/mascotas', {
          ...this.nuevaMascota,
          dueño_id: user.id
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        this.mostrarModal = false
        this.nuevaMascota = { nombre: '', cumpleaños: '', tipo: '' }
        await this.cargarMascotas()
      } catch (error) {
        console.error('Error al crear mascota:', error)
      }
    },
    async editarNombreMascota () {
      try {
        await axios.patch(`http://localhost:5000/api/mascotas/${this.mascotaSeleccionada.id}`, {
          nombre: this.mascotaSeleccionada.nombre
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })

        this.mostrarModalEditar = false
        this.mascotaSeleccionada = null
        await this.cargarMascotas()
      } catch (error) {
        console.error('Error al editar nombre:', error)
      }
    },
    async eliminarMascota (id) {
      if (!confirm('¿Estás seguro de que quieres eliminar esta mascota?')) return

      try {
        await axios.delete(`http://localhost:5000/api/mascotas/${id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })
        await this.cargarMascotas()
      } catch (error) {
        console.error('Error al eliminar mascota:', error)
      }
    },
    abrirEdicion (mascota) {
      this.mascotaSeleccionada = { ...mascota }
      this.mostrarModalEditar = true
    },
    cerrarEdicion () {
      this.mascotaSeleccionada = null
      this.mostrarModalEditar = false
    },
    formatearFecha (fechaISO) {
      const [a, m, d] = fechaISO.split('T')[0].split('-')
      return `${d}-${m}-${a}`
    }
  },
  created () {
    this.cargarMascotas()
  }
}
</script>

<style src="./css/misMascotas.css"></style>
