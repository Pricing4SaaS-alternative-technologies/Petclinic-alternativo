import Vue from 'vue'
import App from './App'
import router from './router'
import { SpaceProvider } from '@npm_team/space-vue-client'

Vue.config.productionTip = false

// SPACE configuration
const spaceConfig = {
  url: 'http://localhost:5403/',
  apiKey: '8bf040d8893421e6eac7c4b81fc191c68fd912847e9c187a62b4232a53e5f7f7',
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
