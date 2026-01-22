import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import AuthPage from '@/components/AuthPage'
import HomeVisitas from '@/components/HomeVisitas'
import HomeVisitasPropietarios from '@/components/HomeVisitasPropietarios'
import HomeAdopciones from '@/components/HomeAdopciones'
import PricingPlans from '@/components/PricingPlans.vue'
import PropHabitacionesHotel from '../components/PropHabitacionesHotel.vue'
import PropDetallesHabitacionHotel from '../components/PropHabitacionesHotelDetalles.vue'

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
    { path: '/adopciones',
      name: 'adopciones',
      component: HomeAdopciones
    },
    { path: '/pricing-plans',
      name: 'pricing-plans',
      component: PricingPlans
    },
    {
      path: '/habitaciones-hotel',
      name: 'habitaciones-hotel',
      component: PropHabitacionesHotel
    },
    {
      path: '/detalles-habitacion/:id',
      name: 'detalles-habitacion',
      component: PropDetallesHabitacionHotel,
      props: true
    }

  ],
  mode: 'history'
})
