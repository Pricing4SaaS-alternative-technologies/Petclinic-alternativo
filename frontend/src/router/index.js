import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import AuthPage from '@/components/AuthPage'
import MisMascotas from '@/components/MisMascotas.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/auth',
      name: 'auth',
      component: AuthPage
    },
    {
      path: '/mis-mascotas',
      name: 'MisMascotas',
      component: MisMascotas
    }
  ],
  mode: 'history'
})
