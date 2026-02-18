<template>
  <div>
    <div class="clinicas-wrapper">
      <div class="clinicas-content">
        <!-- Header con emoji y título -->
        <div class="clinicas-header">
          <h2 class="clinicas-title">
            <i class="fas fa-crown"></i>
            <span>Consulta aquí tus clínicas</span>
          </h2>
        </div>

        <div v-if="jwtValido && has_plan">
          <!-- Info del plan -->
          <div class="plan-badge">
            <strong>Plan:</strong> {{ contract_info.subscriptionPlans["PetClinic"] || contract_info.subscriptionPlans["petclinic"]}}
          </div>

          <!-- Botones de acción principales -->
          <div class="action-buttons">
            <button class="btn-primary" @click="abrirModalCreacion">
              <i class="fas fa-plus-circle"></i>
              Añadir Clínica
            </button>
            <button class="btn-secondary" @click="$router.push('/pricing-plans')">
              <i class="fas fa-star"></i>
              Pricing plans
            </button>
          </div>

        <!-- Lista de clínicas -->
        <div v-if="clinicas.length > 0" class="clinicas-grid">
          <div v-for="clinica in clinicas" :key="clinica.id" class="clinica-card">
            <div class="card-header">
              <h3>{{ clinica.nombre }}</h3>
            </div>
            <div class="card-body">
              <div class="info-row">
                <i class="fas fa-map-marker-alt"></i>
                <div>
                  <span class="label">Dirección:</span>
                  <span class="value">{{ clinica.direccion }}</span>
                </div>
              </div>
              <div class="info-row">
                <i class="fas fa-phone"></i>
                <div>
                  <span class="label">Teléfono:</span>
                  <span class="value">{{ clinica.telefono }}</span>
                </div>
              </div>
            </div>
            <div class="card-actions">
              <button class="btn-edit" @click="iniciaEdicion(clinica)">
                <i class="fas fa-edit"></i>
                Editar clínica
              </button>
              <button class="btn-delete" @click="abrirModalEliminacion(clinica)">
                <i class="fas fa-trash-alt"></i>
                Borrar clínica
              </button>
            </div>
          </div>
        </div>

        <!-- Sin clínicas -->
        <div v-else class="sin-clinicas">
          <div class="empty-state">
            <i class="fas fa-hospital empty-icon"></i>
            <h3>No tienes clínicas asociadas</h3>
            <p>Añade tu primera clínica para empezar a gestionar tu negocio</p>
            <button class="btn-primary" @click="abrirModalCreacion">
              <i class="fas fa-plus-circle"></i>
              Añadir Primera Clínica
            </button>
          </div>
        </div>
      </div>

      <!-- Sin plan -->
      <div v-else-if="!has_plan" class="no-plan">
        <div class="warning-state">
          <i class="fas fa-exclamation-triangle"></i>
          <h3>No perteneces a ningún plan</h3>
          <p>Contrata un plan para acceder a todas las funciones</p>
          <button class="btn-primary" @click="$router.push('/pricing-plans')">
            <i class="fas fa-star"></i>
            Ver Planes
          </button>
        </div>
      </div>

      <!-- No autorizado -->
      <div v-else class="no-auth">
        <div class="error-state">
          <i class="fas fa-lock"></i>
          <p class="error">No estás autorizado para ver esta información.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal para crear clínica -->
  <div class="modal-overlay" v-if="modalCreacion" @click.self="modalCreacion = false">
      <div class="modal-clinica">
        <div class="modal-header">
          <h3><i class="fas fa-plus-circle"></i> Nueva Clínica</h3>
          <button class="close-btn" @click="modalCreacion = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="crearClinica">
          <div class="form-group">
            <label><i class="fas fa-hospital"></i> Nombre:</label>
            <input type="text" v-model="clinicaForm.nombre" placeholder="Nombre de la clínica" required />
          </div>

          <div class="form-group">
            <label><i class="fas fa-map-marker-alt"></i> Dirección:</label>
            <input type="text" v-model="clinicaForm.direccion" placeholder="Dirección completa" required />
          </div>

          <div class="form-group">
            <label><i class="fas fa-phone"></i> Teléfono:</label>
            <input type="text" v-model="clinicaForm.telefono" placeholder="Número de teléfono" required />
          </div>

          <p v-if="errorCreacion" class="mensaje-error">
            <i class="fas fa-exclamation-circle"></i> {{ errorCreacion }}
          </p>

          <div class="modal-buttons">
            <button type="submit" class="btn-save">
              <i class="fas fa-check"></i> Guardar
            </button>
            <button type="button" class="btn-cancel" @click="modalCreacion = false">
              <i class="fas fa-times"></i> Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal para editar clínica -->
    <div class="modal-overlay" v-if="modalEdicion" @click.self="modalEdicion = false">
      <div class="modal-clinica">
        <div class="modal-header">
          <h3><i class="fas fa-edit"></i> Editando: {{ clinicaSeleccionada.nombre }}</h3>
          <button class="close-btn" @click="modalEdicion = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="editarClinica">
          <div class="form-group">
            <label><i class="fas fa-hospital"></i> Nombre:</label>
            <input type="text" v-model="clinicaForm.nombre" required />
          </div>

          <div class="form-group">
            <label><i class="fas fa-map-marker-alt"></i> Dirección:</label>
            <input type="text" v-model="clinicaForm.direccion" required />
          </div>

          <div class="form-group">
            <label><i class="fas fa-phone"></i> Teléfono:</label>
            <input type="text" v-model="clinicaForm.telefono" required />
          </div>

          <p v-if="errorEdicion" class="mensaje-error">
            <i class="fas fa-exclamation-circle"></i> {{ errorEdicion }}
          </p>

          <div class="modal-buttons">
            <button type="submit" class="btn-save">
              <i class="fas fa-check"></i> Guardar
            </button>
            <button type="button" class="btn-cancel" @click="modalEdicion = false">
              <i class="fas fa-times"></i> Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal para confirmar eliminación -->
    <div class="modal-overlay" v-if="modalEliminacion" @click.self="modalEliminacion = false">
      <div class="modal-confirmacion">
        <div class="modal-header-warning">
          <h3><i class="fas fa-exclamation-triangle"></i> Confirmar Eliminación</h3>
          <button class="close-btn" @click="modalEliminacion = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body-confirmacion">
          <p>¿Estás seguro de que quieres eliminar la clínica <strong>{{ clinicaSeleccionada ? clinicaSeleccionada.nombre : '' }}</strong>?</p>
          <p class="warning-text">Esta acción no se puede deshacer.</p>
        </div>
        <div class="modal-buttons">
          <button type="button" class="btn-confirmar-eliminar" @click="confirmarEliminacion">
            <i class="fas fa-trash-alt"></i> Sí, Eliminar
          </button>
          <button type="button" class="btn-cancel" @click="modalEliminacion = false">
            <i class="fas fa-times"></i> Cancelar
          </button>
        </div>
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
      modalEliminacion: false,
      clinicaSeleccionada: null,
      clinicaForm: {
        nombre: '',
        direccion: '',
        telefono: ''
      },
      errorCreacion: '',
      errorEdicion: '',
      contract_info: null,
      has_plan: false

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
    abrirModalCreacion () {
      this.clinicaForm = { nombre: '', direccion: '', telefono: '' }
      this.errorCreacion = ''
      this.modalCreacion = true
    },
    checkAuth () {
      const token = localStorage.getItem('jwt')
      const rawUser = localStorage.getItem('user')
      const rawContrato = localStorage.getItem('contrato')
      const parsedContrato = rawContrato ? JSON.parse(rawContrato) : null

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
        if (parsedContrato !== null && parsedContrato !== '') {
          this.contract_info = parsedContrato
          this.has_plan = true
        }
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
      this.errorCreacion = ''

      // Validaciones
      if (this.clinicaForm.nombre.length > 50) {
        this.errorCreacion = 'El nombre no puede tener más de 50 caracteres.'
        return
      }
      if (this.clinicaForm.direccion.length > 100) {
        this.errorCreacion = 'La dirección no puede tener más de 100 caracteres.'
        return
      }
      if (!/^\d{9}$/.test(this.clinicaForm.telefono)) {
        this.errorCreacion = 'El teléfono debe tener exactamente 9 dígitos numéricos.'
        return
      }

      if (this.jwtValido && this.has_plan) {
        const payload = { ...this.clinicaForm }
        try {
          await api.post('http://localhost:5000/api/clinicas/crear', payload)
          this.modalCreacion = false
          this.clinicaForm = { nombre: '', direccion: '', telefono: '' }
          await this.fetchClinicasPropias()
        } catch (error) {
          this.errorCreacion = 'Error al crear clínica.'
          console.error('Error al crear clínica:', error.message, error)
        }
      } else {
        alert('No tienes permiso para crear clínicas.')
      }
    },
    abrirModalEliminacion (clinica) {
      if (this.jwtValido && this.has_plan) {
        this.clinicaSeleccionada = clinica
        this.modalEliminacion = true
      } else {
        alert('No tienes permiso para eliminar clínicas.')
      }
    },
    async confirmarEliminacion () {
      try {
        await api.delete(`http://localhost:5000/api/clinicas/eliminar/${this.clinicaSeleccionada.id}`)
        this.modalEliminacion = false
        this.clinicaSeleccionada = null
        await this.fetchClinicasPropias()
      } catch (error) {
        console.error('Error al eliminar clínica:', error.message, error)
      }
    },
    iniciaEdicion (clinica) {
      if (this.jwtValido && this.has_plan) {
        this.clinicaSeleccionada = clinica
        this.clinicaForm = { ...clinica }
        this.modalEdicion = true
      } else {
        alert('No tienes permiso para editar clínicas.')
      }
    },
    async editarClinica () {
      this.errorEdicion = ''

      // Validaciones
      if (this.clinicaForm.nombre.length > 50) {
        this.errorEdicion = 'El nombre no puede tener más de 50 caracteres.'
        return
      }
      if (this.clinicaForm.direccion.length > 100) {
        this.errorEdicion = 'La dirección no puede tener más de 100 caracteres.'
        return
      }
      if (!/^\d{9}$/.test(this.clinicaForm.telefono)) {
        this.errorEdicion = 'El teléfono debe tener exactamente 9 dígitos numéricos.'
        return
      }

      if (this.jwtValido && this.has_plan) {
        try {
          const payload = { ...this.clinicaForm }
          await api.put(`http://localhost:5000/api/clinicas/editar/${this.clinicaSeleccionada.id}`, payload)
          this.modalEdicion = false
          this.clinicaForm = { nombre: '', direccion: '', telefono: '' }
          await this.fetchClinicasPropias()
        } catch (error) {
          this.errorEdicion = 'Error al editar clínica.'
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
@import './css/HomeClinica.css';
</style>
