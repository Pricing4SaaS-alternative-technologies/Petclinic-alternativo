<template>
    <div>
        <p> Petclinic Alternativo </p>
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
      const path = 'http://localhost:5000/api/v1.0/mensaje'
      axios.get(path).then((respuesta) => {
        this.mensaje = respuesta.data
      }).catch((error) => {
        console.log(error)
      })
    }
  },
  created () {
    this.getMensaje()
  }
}
</script>
