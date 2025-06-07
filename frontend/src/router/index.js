import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import AuthPage from '@/components/AuthPage'

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
    }
  ],
  mode: 'history'
})
