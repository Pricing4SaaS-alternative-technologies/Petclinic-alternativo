import { useRouter } from 'vue-router'
<template>
  <div class="clinicas-container">
    <h2>Consulta aquí tus clínicas</h2>

    <div v-if="jwtValido">
      <button class="boton-grande" @click="modalCreacion = true">Añadir Clínica</button>
      <div v-if="clinicas.length > 0" class="clinica-list">

        <div v-for="clinica in clinicas" :key="clinica.id" class="clinica-card">
          <h3>{{ clinica.nombre }}</h3>
          <p><strong>Dirección:</strong> {{ clinica.direccion }}</p>
          <p><strong>Teléfono:</strong> {{ clinica.telefono }}</p>
          <p><strong>Plan:</strong> {{ clinica.plan }}</p>
          <button class="boton-grande" @click="iniciaEdicion(clinica)">Editar clinica</button>
          <button class="boton-grande" @click="eliminarClinica(clinica)">Borrar clinica</button>
        </div>
      </div>

      <div v-else class="sin-clinicas">
        <p>No tienes clínicas registradas.</p>
      </div>
    </div>

    <div v-else class="no-auth">
      <p class="error">No estás autorizado para ver esta información.</p>
    </div>
    <!-- Modal para crear mascota -->
    <div class="modal-overlay" v-if="modalCreacion">
      <div class="modal">
        <h3>Nueva Clinica</h3>
        <form @submit.prevent="crearClinica">

          <label>Nombre:</label>
          <input type="text" v-model="clinicaForm.nombre" required />

          <label>Dirección</label>
          <input type="text" v-model="clinicaForm.direccion" required />

          <label>Teléfono:</label>
          <input type="text" v-model="clinicaForm.telefono" required />

          <div class="modal-buttons">
            <button type="submit">Guardar</button>
            <button type="button" class="cancelar" @click="modalCreacion = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

        <!-- Modal para editar Clinica -->
    <div class="modal-overlay" v-if="modalEdicion">
      <div class="modal">
        <h3>Editando Clinica: {{ clinicaSeleccionada.nombre }}</h3>
        <form @submit.prevent="editarClinica">

          <label>Nombre:</label>
          <input type="text" v-model="clinicaForm.nombre" required />

          <label>Dirección</label>
          <input type="text" v-model="clinicaForm.direccion" required />

          <label>Teléfono:</label>
          <input type="text" v-model="clinicaForm.telefono" required />

          <div class="modal-buttons">
            <button type="submit">Guardar</button>
            <button type="button" class="cancelar" @click="modalEdicion = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/axios'

export default {
  data () {
    return {
      info_usuario: null,
      jwtValido: false,
      clinicas: [],
      modalCreacion: false,
      modalEdicion: false,
      clinicaSeleccionada: null,
      clinicaForm: {
        nombre: '',
        direccion: '',
        telefono: ''
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
        this.fetchClinicasPropias()
      } catch (e) {
        console.error('Error al parsear el usuario:', e)
        this.jwtValido = false
      }
    },
    async fetchClinicasPropias () {
      // no hace falta revisar token por que el propio checkAuth llama a esta función si todo va bien
      try {
        const res = await api.get(`http://localhost:5000/api/clinicas/listar/${this.info_usuario.id}`)
        this.clinicas = res.data
      } catch (err) {
        console.error('Error al cargar clínicas', err)
      }
    },

    async crearClinica () {
      if (this.jwtValido) {
        const payload = { ...this.clinicaForm }
        try {
          await api.post('http://localhost:5000/api/clinicas/crear', payload)
          this.modalCreacion = false
          this.clinicaForm = { nombre: '', direccion: '', telefono: '' }
          await this.fetchClinicasPropias()
        } catch (error) {
          console.error('Error al crear clínica:', error.message, error)
        }
      } else {
        alert('No tienes permiso para crear clínicas.')
      }
    },
    async eliminarClinica (clinica) {
      if (this.jwtValido) {
        if (confirm(`¿Estás seguro de que quieres eliminar la clínica ${clinica.nombre}?`)) {
          try {
            await api.delete(`http://localhost:5000/api/clinicas/eliminar/${clinica.id}`)
            await this.fetchClinicasPropias()
          } catch (error) {
            console.error('Error al eliminar clínica:', error.message, error)
          }
        }
      } else {
        alert('No tienes permiso para eliminar clínicas.')
      }
    },
    iniciaEdicion (clinica) {
      if (this.jwtValido) {
        this.clinicaSeleccionada = clinica
        this.clinicaForm = { ...clinica }
        this.modalEdicion = true
      } else {
        alert('No tienes permiso para editar clínicas.')
      }
    },
    async editarClinica () {
      if (this.jwtValido) {
        try {
          const payload = {...this.clinicaForm}
          await api.put(`http://localhost:5000/api/clinicas/editar/${this.clinicaSeleccionada.id}`, payload)
          this.modalEdicion = false
          this.clinicaForm = { nombre: '', direccion: '', telefono: '' }
          await this.fetchClinicasPropias()
        } catch (error) {
          console.error('Error al editar clínica:', error.message, error)
        }
      } else {
        alert('No tienes permiso para editar clínicas.')
      }
    }
  }
}
</script>

<style scoped>
.clinica-card {
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f9f9f9;
}

.clinica-list {
  border: 1px solid #090909;
  overflow-y: auto;
  border-radius: 10px;
  max-height: 30%;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f9f9f9;
}

.boton-grande {
  padding: 1rem 2rem;
  font-size: 1.2rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.boton-grande:hover {
  background-color: #43a047;
}

.error {
  color: red;
  font-weight: bold;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.modal label {
  display: block;
  margin-top: 1rem;
  font-weight: bold;
}

.modal input,
.modal select {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.3rem;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
}

.modal-buttons button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.modal-buttons .cancelar {
  background-color: #f44336;
  color: white;
}

.modal-buttons .cancelar:hover {
  background-color: #d32f2f;
}
</style>
