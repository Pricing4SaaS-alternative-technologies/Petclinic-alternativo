import { useRouter } from 'vue-router'
<template>
  <div class="clinicas-container">
    <h2>Consulta aquí tus clínicas</h2>

    <div v-if="jwtValido">
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
        <button class="boton-grande" @click="añadirClinica">+ Añadir Clínica</button>
      </div>
    </div>

    <div v-else class="no-auth">
      <p class="error">No estás autorizado para ver esta información.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      info_usuario: null,
      jwtValido: false,
      clinicas: []
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
      try {
        const res = await axios.get('http://localhost:5000/api/clinicas/listar-todas')
        this.clinicas = res.data
      } catch (err) {
        console.error('Error al cargar clínicas', err)
      }
    }
  }
}
</script>
