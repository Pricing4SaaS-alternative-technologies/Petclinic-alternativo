import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import AuthPage from '@/components/AuthPage'
import HomeVisitas from '@/components/HomeVisitas'
import HomeVisitasPropietarios from '@/components/HomeVisitasPropietarios.vue'

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
    { path: '/visitas',
      name: 'visitas',
      component: HomeVisitas
    },
    { path: '/mis-visitas',
      name: 'mis-visitas',
      component: HomeVisitasPropietarios
    }
  ],
  mode: 'history'
})
