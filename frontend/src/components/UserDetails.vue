<template>
  <div>
    <div class="perfil-wrapper">
      <div class="perfil-content">
        <div class="perfil-header">
          <h2 class="perfil-title">
            <i class="fas fa-user-circle"></i>
            <span>Mi Perfil</span>
          </h2>
        </div>

        <div v-if="jwtValido && usuarioCargado" class="perfil-main">

          <div class="perfil-card main-card">
            <div class="card-header">
              <h3>Datos Personales</h3>
            </div>
            <div class="card-body">
              <div class="info-row">
                <i class="fas fa-id-badge"></i>
                <div>
                  <span class="label">Nombre completo:</span>
                  <span class="value">{{ perfil.nombre }} {{ perfil.apellidos }}</span>
                </div>
              </div>
              <div class="info-row">
                <i class="fas fa-at"></i>
                <div>
                  <span class="label">Nombre de usuario:</span>
                  <span class="value">{{ perfil.usuario }}</span>
                </div>
              </div>
              <div class="info-row">
                <i class="fas fa-envelope"></i>
                <div>
                  <span class="label">Email:</span>
                  <span class="value">{{ perfil.email }}</span>
                </div>
              </div>
              <div class="info-row">
                <i class="fas fa-user-tag"></i>
                <div>
                  <span class="label">Tipo de cuenta:</span>
                  <span class="value badge-tipo">{{ formatTipoUsuario(perfil.tipo_usuario) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="perfil.tipo_usuario === 'PROP_MASCOTA'" class="perfil-card specific-card">
            <div class="card-header">
              <h3><i class="fas fa-paw"></i> Información de Contacto</h3>
            </div>
            <div class="card-body">
              <div class="info-row">
                <i class="fas fa-map-marker-alt"></i>
                <div>
                  <span class="label">Dirección:</span>
                  <span class="value">{{ perfil.direccion }}</span>
                </div>
              </div>
              <div class="info-row">
                <i class="fas fa-phone"></i>
                <div>
                  <span class="label">Teléfono:</span>
                  <span class="value">{{ perfil.telefono }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="perfil.tipo_usuario === 'PROP_CLINICA'" class="perfil-card specific-card">
            <div class="card-header">
              <h3><i class="fas fa-clinic-medical"></i> Datos de Administración</h3>
            </div>
            <div class="card-body">
              <div class="info-row">
                <i class="fas fa-phone-alt"></i>
                <div>
                  <span class="label">Teléfono corporativo:</span>
                  <span class="value">{{ perfil.telefono }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="perfil.tipo_usuario === 'VETERINARIO'" class="perfil-card specific-card">
            <div class="card-header">
              <h3><i class="fas fa-user-md"></i> Perfil Profesional</h3>
            </div>
            <div class="card-body">
              <div class="info-row">
                <i class="fas fa-city"></i>
                <div>
                  <span class="label">Ciudad base:</span>
                  <span class="value">{{ perfil.ciudad }}</span>
                </div>
              </div>
              <div class="info-row" v-if="perfil.especialidades && perfil.especialidades.length > 0">
                <i class="fas fa-star-of-life"></i>
                <div>
                  <span class="label">Especialidades:</span>
                  <div class="tags-container">
                    <span v-for="(esp, index) in perfil.especialidades" :key="index" class="tag">
                      {{ esp }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="action-buttons mt-4">
            <button class="btn-edit" @click="abrirModalEdicion">
              <i class="fas fa-user-edit"></i> Editar Perfil
            </button>
            </div>

            <div class="action-buttons mt-4">
              <button class="btn-delete" @click="confirmarEliminacion">
                <i class="fas fa-trash"></i> Eliminar Cuenta
              </button>
            </div>

        </div>

        <div v-else-if="jwtValido && !usuarioCargado && !errorCarga" class="loading-state">
           <i class="fas fa-spinner fa-spin"></i> Cargando información...
        </div>

        <div v-else-if="errorCarga" class="error-state">
           <i class="fas fa-exclamation-circle"></i>
           <p class="error">{{ errorCarga }}</p>
           <button class="btn-secondary" @click="fetchPerfilUsuario">Reintentar</button>
        </div>

        <div v-else class="no-auth">
          <div class="error-state">
            <i class="fas fa-lock"></i>
            <p class="error">Inicia sesión para ver tu perfil.</p>
            <button class="btn-primary" @click="$router.push('/login')">Ir al Login</button>
          </div>
        </div>

      </div>
    </div>

    <div class="modal-overlay" v-if="modalEdicion" @click.self="modalEdicion = false">
      <div class="modal-clinica"> <div class="modal-header">
          <h3><i class="fas fa-user-edit"></i> Editar Perfil</h3>
          <button class="close-btn" @click="modalEdicion = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="guardarEdicion">
          <div class="form-group">
            <label><i class="fas fa-user"></i> Nombre:</label>
            <input type="text" v-model="perfilForm.nombre" required />
          </div>
          <div class="form-group">
            <label><i class="fas fa-user"></i> Apellidos:</label>
            <input type="text" v-model="perfilForm.apellidos" required />
          </div>

          <div v-if="perfil.tipo_usuario === 'PROP_MASCOTA' || perfil.tipo_usuario === 'PROP_CLINICA'" class="form-group">
            <label><i class="fas fa-phone"></i> Teléfono:</label>
            <input type="text" v-model="perfilForm.telefono" required />
          </div>

          <p v-if="errorEdicion" class="mensaje-error">
            <i class="fas fa-exclamation-circle"></i> {{ errorEdicion }}
          </p>

          <div class="modal-buttons">
            <button type="submit" class="btn-save" :disabled="guardando">
              <i class="fas fa-check"></i> {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
            <button type="button" class="btn-cancel" @click="modalEdicion = false">
              <i class="fas fa-times"></i> Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import api from '../api/axios'

export default {
  name: 'UserDetails',
  data () {
    return {
      jwtValido: false,
      info_usuario_local: null, // Lo que hay en localStorage
      perfil: {}, // Los datos completos de la BBDD
      usuarioCargado: false,
      errorCarga: '',

      // Modal
      modalEdicion: false,
      perfilForm: {},
      errorEdicion: '',
      guardando: false
    }
  },
  async created () {
    await this.checkAuth()
    window.addEventListener('logout', this.handleLogout)
  },
  beforeUnmount () {
    window.removeEventListener('logout', this.handleLogout)
  },
  methods: {
    handleLogout () {
      this.jwtValido = false
      this.perfil = {}
      this.usuarioCargado = false
    },
    async checkAuth () {
      const token = localStorage.getItem('jwt')
      const rawUser = localStorage.getItem('user')

      if (!token || !rawUser) {
        this.jwtValido = false
        return
      }

      try {
        this.info_usuario_local = JSON.parse(rawUser)
        this.jwtValido = true
        await this.fetchPerfilUsuario()
      } catch (e) {
        console.error('Error al parsear el usuario:', e)
        this.jwtValido = false
      }
    },
    async fetchPerfilUsuario () {
      this.errorCarga = ''
      try {
        // Asegúrate de que esta ruta coincide con la de tu Blueprint en Flask
        // Si no le pasas el ID en la URL y usas get_jwt_identity() en Flask, la ruta sería '/api/usuarios/perfil'
        const res = await api.get('http://localhost:5000/api/usuarios/perfil')
        this.perfil = res.data.datos
        this.usuarioCargado = true
      } catch (err) {
        console.error('Error al cargar el perfil', err)
        this.errorCarga = 'No se pudo cargar la información del perfil.'
        this.usuarioCargado = false
      }
    },

    // Utilidad para mostrar el tipo de usuario de forma amigable
    formatTipoUsuario (tipo) {
      if (!tipo) return 'Usuario'
      const tiposMap = {
        PROP_MASCOTA: 'Propietario de Mascota',
        PROP_CLINICA: 'Administrador de Clínica',
        VETERINARIO: 'Veterinario Profesional'
      }
      return tiposMap[tipo] || tipo
    },

    // Métodos para el Modal
    abrirModalEdicion () {
      // Copiamos los datos para no modificar el original hasta guardar
      this.perfilForm = { ...this.perfil }
      this.errorEdicion = ''
      this.modalEdicion = true
    },
    async confirmarEliminacion () {
      const confirmacion = confirm('¿Estás seguro de que quieres eliminar tu cuenta? Esta acción es irreversible.')

      if (!confirmacion) return

      try {
        const user = JSON.parse(localStorage.getItem('user'))

        await api.delete(`http://localhost:5000/api/auth/delete_user/${user.id}`)

        // Limpiar sesión
        localStorage.removeItem('jwt')
        localStorage.removeItem('user')
        localStorage.removeItem('contrato')
        localStorage.removeItem('spaceToken')

        window.dispatchEvent(new Event('logout'))

        // Redirigir
        this.$router.push('/')
      } catch (error) {
        console.error('Error al eliminar usuario:', error)
        alert('No se pudo eliminar la cuenta.')
      }
    },

    async guardarEdicion () {
      this.errorEdicion = ''

      // Ejemplo de validación básica
      if (this.perfilForm.nombre.length === 0) {
        this.errorEdicion = 'El nombre es obligatorio.'
        return
      }

      this.guardando = true
      try {
        // Asumiendo que crearás un endpoint PUT para actualizar el perfil
        await api.put('http://localhost:5000/api/usuarios/perfil/editar', this.perfilForm)

        this.modalEdicion = false
        // Recargamos los datos desde el servidor para asegurar sincronización
        await this.fetchPerfilUsuario()

        // Opcional: Si cambias nombre/apellidos, puede que necesites actualizar el localStorage('user')
        // const rawUser = JSON.parse(localStorage.getItem('user'));
        // rawUser.nombre = this.perfilForm.nombre;
        // localStorage.setItem('user', JSON.stringify(rawUser));
      } catch (error) {
        this.errorEdicion = 'Error al actualizar el perfil.'
        console.error('Error al editar perfil:', error.message, error)
      } finally {
        this.guardando = false
      }
    }
  }
}
</script>

<style scoped>
@import './css/UserDetails.css';
</style>
