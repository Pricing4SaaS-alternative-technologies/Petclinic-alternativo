import Vue from 'vue'
import App from './App'
import router from './router'
import { SpaceProvider } from '@npm_team/space-vue-client'

Vue.config.productionTip = false

// SPACE configuration
const spaceConfig = {
  url: 'http://localhost:5403/',
  apiKey: 'SPACE_API_KEY',
  allowConnectionWithSpace: true
}

// eslint-disable-next-line no-new
new Vue({
  el: '#app',
  router,
  components: { App, SpaceProvider },
  data () {
    return {
      spaceConfig
    }
  },
  template: `
    <SpaceProvider :config="spaceConfig">
      <App/>
    </SpaceProvider>
  `
})
