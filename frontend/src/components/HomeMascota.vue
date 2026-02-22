<template>
  <div>
    <div class="mascotas-wrapper">
      <div class="mascotas-content">
        <div class="mascotas-header">
          <h2>🐶 Mis Mascotas</h2>
        </div>
        <button class="btn-crear" @click="mostrarModal = true">➕ Añadir Mascota</button>
        <ul v-if="mascotas.length" class="mascota-lista">
          <li v-for="mascota in mascotas" :key="mascota.id" class="mascota-card">
            <div class="mascota-info">
              <h3>{{ mascota.nombre }}</h3>
              <div class="mascota-tipo">Tipo: <span class="tipo-valor">{{ mascota.tipo }}</span></div>
              <div class="mascota-fecha">Cumpleaños: <span class="fecha-valor">{{ formatearFecha(mascota.cumpleaños) }}</span></div>
            </div>
            <div class="mascota-acciones">
              <button class="btn-editar" @click="abrirEdicion(mascota)" title="Editar">✏️</button>
              <button class="btn-eliminar" @click="abrirModalEliminar(mascota)" title="Eliminar">🗑️</button>
            </div>
          </li>
        </ul>
        <p v-else class="no-mascotas">No tienes mascotas registradas.</p>
      </div>
    </div>

    <div class="modal-overlay" v-if="mostrarModal">
      <div class="modal">
        <h3>Nueva Mascota</h3>
        <form @submit.prevent="crearMascota">
          <label>Nombre:</label>
          <input v-model="nuevaMascota.nombre" required />

          <label>Tipo:</label>
          <select v-model="nuevaMascota.tipo" required>
            <option disabled value="">Seleccione un tipo</option>
            <option value="perro">PERRO</option>
            <option value="gato">GATO</option>
            <option value="reptil">REPTIL</option>
            <option value="pajaro">PAJARO</option>
            <option value="hamster">HAMSTER</option>
            <option value="tortuga">TORTUGA</option>
          </select>

          <label>Cumpleaños:</label>
          <input type="date" v-model="nuevaMascota.cumpleaños" required />

          <p v-if="errorCreacion" class="mensaje-error">{{ errorCreacion }}</p>

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
          <p v-if="errorEdicion" class="mensaje-error">{{ errorEdicion }}</p>
          <div class="modal-buttons">
            <button type="submit">Guardar</button>
            <button type="button" class="cancelar" @click="cerrarEdicion">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="mostrarModalEliminar">
      <div class="modal">
        <h3>Eliminar Mascota</h3>
        <p>¿Estás seguro de que deseas eliminar a <strong>{{ mascotaSeleccionada.nombre }}</strong>?</p>
        <p class="advertencia">Esta acción no se puede deshacer.</p>
        <div class="modal-buttons">
          <button type="button" @click="confirmarEliminar" class="btn-eliminar">Eliminar</button>
          <button type="button" class="cancelar" @click="cerrarModalEliminar">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { syncSpaceToken } from '@/utils/spaceSync'

export default {
  name: 'MisMascotas',
  data () {
    return {
      mascotas: [],
      mostrarModal: false,
      mostrarModalEditar: false,
      mostrarModalEliminar: false,
      errorCreacion: '',
      errorEdicion: '',
      nuevaMascota: {
        nombre: '',
        cumpleaños: '',
        tipo: ''
      },
      mascotaSeleccionada: null
    }
  },
  computed: {
    spaceKey () {
      return this.$spaceState.payload ? this.$spaceState.payload.iat : 'sin-token'
    }
  },
  methods: {
    async cargarMascotas () {
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user || !user.id) return

      try {
        const res = await axios.get('http://localhost:5000/api/mascotas/listar-tus-mascotas', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })
        this.mascotas = res.data
        await syncSpaceToken(this.$router)
      } catch (error) {
        console.error('Error al cargar mascotas:', error)
      }
    },
    async crearMascota () {
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user || !user.id) return

      try {
        if (this.nuevaMascota.nombre.length > 50) {
          this.errorCreacion = 'El nombre no puede tener más de 50 caracteres'
          return
        }
        this.errorCreacion = ''
        if (this.nuevaMascota.cumpleaños < '1800-01-01') {
          this.errorCreacion = 'La fecha de cumpleaños no puede ser anterior al 1 de enero de 1800'
          return
        }
        this.errorCreacion = ''
        await axios.post('http://localhost:5000/api/mascotas/crear-mascota', {
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
        if (error.response && error.response.data && error.response.data.error) {
          this.errorCreacion = error.response.data.error
        } else {
          this.errorCreacion = 'Error al crear mascota'
        }
      }
    },
    async editarNombreMascota () {
      if (this.mascotaSeleccionada.nombre.length > 50) {
        this.errorEdicion = 'El nombre no puede tener más de 50 caracteres'
        return
      }
      this.errorEdicion = ''
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
    abrirModalEliminar (mascota) {
      this.mascotaSeleccionada = { ...mascota }
      this.mostrarModalEliminar = true
    },
    cerrarModalEliminar () {
      this.mostrarModalEliminar = false
      this.mascotaSeleccionada = null
    },
    async confirmarEliminar () {
      try {
        await axios.delete(`http://localhost:5000/api/mascotas/${this.mascotaSeleccionada.id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`
          }
        })
        this.cerrarModalEliminar()
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
  async created () {
    await syncSpaceToken(this.$router)
    this.cargarMascotas()
  }
}
</script>

<style scoped>
@import './css/HomeMascota.css';
</style>
