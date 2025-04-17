import { useRouter } from 'vue-router'

<template>
  <div>
    <p>{{ mensaje }}</p>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'Home',
  data () {
    return {
      mensaje: 'Sin mensaje!'
    }
  },
  methods: {

    getMensaje () {
      // Obtener el token desde localStorage
      const token = localStorage.getItem('jwt')
      // Si no hay token, establecemos un mensaje por defecto
      if (!token) {
        this.mensaje = 'No estas loggeado!'
        return
      }

      // const path = 'http://localhost:5000/api/v1.0/mensaje'
      console.log('Token:', token)
      axios.get('http://localhost:5000/api/v1.0/mensaje', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then(respuesta => {
        // Si la solicitud es exitosa, se muestra el mensaje devuelto
          this.mensaje = respuesta.data
        })
        .catch(error => {
          console.log('Error al obtener mensaje:', error)
          // Si hay un error (por ejemplo, 401 Unauthorized), mostramos "No hay mensaje"
          this.mensaje = 'Hubo un error procesando la solicitud'
        })
    }
  },
  created () {
    this.getMensaje()
  }
}
</script>
