import Vue from 'vue'
import App from './App'
import router from './router'
import { SpaceProvider } from '@npm_team/space-vue-client'
// import api from './api/axios' // Tus otros imports...

Vue.config.productionTip = false

// 1. Nos traemos tu configuración aquí
const spaceConfig = {
  url: 'http://localhost:5403/',
  apiKey: '1725e7429f19b0da6b8f024ec27f2b16572df165f5c6b3f498a8e4bb24edf4b9',
  allowConnectionWithSpace: true
}

// 2. Envolvemos la <App/> entera
// eslint-disable-next-line no-new
new Vue({
  el: '#app',
  router,
  components: { App, SpaceProvider },
  data () {
    return {
      spaceConfig // Hacemos la config reactiva para el template
    }
  },
  // ¡AQUÍ ESTÁ LA MAGIA! El Provider abraza a toda la App desde fuera.
  template: `
    <SpaceProvider :config="spaceConfig">
      <App/>
    </SpaceProvider>
  `
})
