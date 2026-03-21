import Vue from 'vue'
import App from './App'
import router from './router'
import { SpaceProvider } from '@npm_team/space-vue-client'
// import api from './api/axios' // Tus otros imports...

Vue.config.productionTip = false

// 1. Nos traemos tu configuración aquí
const spaceConfig = {
  url: 'http://localhost:5403/',
  apiKey: '27a13d852ad3b63e0410507e062f66021b48cfb556f895adbc0dde0d96552127',
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
