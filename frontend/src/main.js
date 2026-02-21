// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import { tokenService, SpaceProvider } from '@npm_team/space-vue-client'
// eslint-disable-next-line no-unused-vars
import api from './api/axios'

Vue.config.productionTip = false

Vue.prototype.$tokenService = tokenService

const spaceState = Vue.observable({
  payload: tokenService.getPayload()
})

tokenService.subscribe(() => {
  spaceState.payload = tokenService.getPayload()
})

Vue.prototype.$spaceState = spaceState

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App, SpaceProvider },
  template: '<App/>'
})
