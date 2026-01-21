<template>
  <div id="app">
    <Navbar />
    <router-view/>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import '@/App.css'

export default {
  name: 'App',
  components: {
    Navbar
  }
}
</script>
