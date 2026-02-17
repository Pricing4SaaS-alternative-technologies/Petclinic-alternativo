<template>
  <SpaceProvider :config="spaceConfig">
    <div id="app">
      <Navbar />
      <router-view/>
    </div>
  </SpaceProvider>
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import { SpaceProvider } from '@npm_team/space-vue-client'
import '@/App.css'

export default {
  name: 'App',
  components: {
    Navbar,
    SpaceProvider
  },
  data () {
    return {
      spaceConfig: {
        allowConnectionWithSpace: false
      }
    }
  }
}
</script>
