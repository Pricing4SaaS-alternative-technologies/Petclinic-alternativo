import Vue from 'vue'
import App from './App'
import router from './router'
import { SpaceProvider } from '@npm_team/space-vue-client'

Vue.config.productionTip = false

// SPACE configuration
const spaceConfig = {
  url: 'http://localhost:5403/',
  apiKey: '1725e7429f19b0da6b8f024ec27f2b16572df165f5c6b3f498a8e4bb24edf4b9',
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
