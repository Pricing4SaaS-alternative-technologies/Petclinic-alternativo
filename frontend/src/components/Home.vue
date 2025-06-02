import { useRouter } from 'vue-router'

<template>
  <div>
    <p>{{ mensaje.message }}</p>
    <p> {{ mensaje.tipo }}</p>
    <p v-if="mensaje.error" class="error">{{ mensaje.error }}</p>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'Home',
  data () {
    return {
      mensaje: {
        message: 'Sin mensaje!',
        tipo: 'usuario no loggeado'
      }
    }
  },
  methods: {

    getMensaje () {
      // Obtener el token desde localStorage
      const token = localStorage.getItem('jwt')
      console.log('Token:', token)
      // Si no hay token, establecemos un mensaje por defecto
      if (!token) {
        this.mensaje.message = 'No estas loggeado!'
        this.mensaje.tipo = 'usuario no loggeado'
        return
      }

      axios.get('http://localhost:5000/api/v1.0/mensaje', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
        .then(respuesta => {
        // Si la solicitud es exitosa, se muestra el mensaje devuelto
          this.mensaje = respuesta.data
        })
        .catch(error => {
          console.log('Error al obtener mensaje:', error)
          this.mensaje = 'Hubo un error procesando la solicitud'
        })
    }
  },
  created () {
    this.getMensaje()
  }
}
</script>
