import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import AuthPage from '@/components/AuthPage'
import HomeVisitas from '@/components/HomeVisitas'
import HomeVisitasPropietarios from '@/components/HomeVisitasPropietarios'
import CalendarioVisitas from '@/components/CalendarioVisitas'
import HomeAdopciones from '@/components/HomeAdopciones'
import PricingPlans from '@/components/PricingPlans.vue'

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
    },
    { path: '/calendario-visitas',
      name: 'calendario-visitas',
      component: CalendarioVisitas
    },
    { path: '/adopciones',
      name: 'adopciones',
      component: HomeAdopciones
    },
    { path: '/pricing-plans',
      name: 'pricing-plans',
      component: PricingPlans
    }

  ],
  mode: 'history'
})
