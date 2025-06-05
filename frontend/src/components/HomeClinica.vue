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
        </div>
      </div>

      <div v-else class="sin-clinicas">
        <p>No tienes clínicas registradas.</p>
        <button class="boton-grande" @click="modalCreacion = true">Añadir Clínica</button>
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
          <input type="text" v-model="nuevaClinica.nombre" required />

          <label>Dirección</label>
          <input type="text" v-model="nuevaClinica.direccion" required />

          <label>Teléfono:</label>
          <input type="text" v-model="nuevaClinica.telefono" required />

          <div class="modal-buttons">
            <button type="submit">Guardar</button>
            <button type="button" class="cancelar" @click="mostrarModal = false">Cancelar</button>
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
      nuevaClinica: {
        nombre: '',
        direccion: '',
        telefono: '',
        plan: 'BASICO' // Por defecto, el plan es BASICO
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
        const payload = {...this.nuevaClinica}
        api.post('http://localhost:5000/api/clinicas/crear', payload)
          .then(response => {
            this.modalCreacion = false
            this.nuevaClinica = { nombre: '', direccion: '', telefono: '', plan: 'BASICO' }
          })
        await this.fetchClinicasPropias()
          .catch(error => {
            console.error('Error al crear clínica:', error.message, error)
          })
      } else {
        alert('No tienes permiso para crear clínicas.')
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
