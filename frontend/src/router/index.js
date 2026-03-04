import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import AuthPage from '@/components/AuthPage'
import Visitas from '@/components/Visitas'
import VisitasPropietarios from '@/components/VisitasPropietarios'
import CalendarioVisitas from '@/components/CalendarioVisitas'
import CalendarioReservasHabitacion from '@/components/CalendarioReservasHabitacion'
import Adopciones from '@/components/Adopciones'
import PricingPlans from '@/components/PricingPlans.vue'
import PropHabitacionesHotel from '../components/PropHabitacionesHotel.vue'
import PropDetallesHabitacionHotel from '../components/PropHabitacionesHotelDetalles.vue'
import PropMisReservas from '../components/PropHabitacionesHotelReservas.vue'

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
      path: '/visitas',
      name: 'visitas',
      component: Visitas
    },
    {
      path: '/mis-visitas',
      name: 'mis-visitas',
      component: VisitasPropietarios
    },
    {
      path: '/calendario-visitas',
      name: 'calendario-visitas',
      component: CalendarioVisitas
    },
    {
      path: '/adopciones',
      name: 'adopciones',
      component: Adopciones
    },
    {
      path: '/pricing-plans',
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
    },
    {
      path: '/mis-reservas',
      name: 'mis-reservas',
      component: PropMisReservas
    },
    {
      path: '/calendario-reservas/:habitacion_id',
      name: 'calendario-reservas',
      component: CalendarioReservasHabitacion,
      props: true
    }

  ],
  mode: 'history'
})
