<template>
  <div class="calendario-reservas-container" v-if="jwtValido">
    <div class="calendario-header">
      <h1 class="calendario-title">📅 Calendario de Reservas</h1>
      <p class="calendario-description">
        Visualiza todas las reservas de la habitación "<strong>{{ habitacionNombre }}</strong>" en un calendario interactivo
      </p>
      <button @click="volverAtras" class="btn-volver">
        <i class="fas fa-arrow-left"></i> Volver
      </button>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando calendario de reservas...</p>
    </div>

    <div v-else class="calendario-content">
      <!-- Controles del calendario -->
      <div class="calendario-controls">
        <button @click="mesAnterior" class="nav-btn">← Mes Anterior</button>
        <h2 class="mes-actual">{{ nombreMes }} {{ añoActual }}</h2>
        <button @click="mesSiguiente" class="nav-btn">Mes Siguiente →</button>
      </div>

      <!-- Calendario -->
      <div class="calendario-wrapper">
        <div class="dias-semana">
          <div class="dia-semana">Lun</div>
          <div class="dia-semana">Mar</div>
          <div class="dia-semana">Mié</div>
          <div class="dia-semana">Jue</div>
          <div class="dia-semana">Vie</div>
          <div class="dia-semana">Sab</div>
          <div class="dia-semana">Dom</div>
        </div>
        <div class="dias-calendario">
          <div
            v-for="dia in diasCalendario"
            :key="`${dia.fecha}`"
            :class="['dia', { 'otro-mes': !dia.mesActual }, { 'hoy': dia.esHoy }]"
          >
            <div class="numero-dia">{{ dia.numero }}</div>
            <div v-if="dia.reservas.length > 0" class="reservas-en-celda">
              <div v-for="reserva in dia.reservas" :key="reserva.id" class="reserva-barra" :style="{ backgroundColor: generarColor(reserva.id) }">
                <span class="reserva-nombre">{{ reserva.mascota_nombre }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel de información de reservas -->
      <div class="leyenda-reservas">
        <h3>Reservas en este mes</h3>
        <div v-if="reservasDelMes.length > 0" class="lista-reservas">
          <div v-for="reserva in reservasDelMes" :key="reserva.id" class="reserva-item" :style="{ borderLeftColor: generarColor(reserva.id) }">
            <div class="reserva-mascota">🐾 {{ reserva.mascota_nombre }}</div>
            <div class="reserva-dueño">👤 {{ reserva.dueño_nombre }}</div>
            <div class="reserva-fechas">
              {{ formatearFecha(reserva.fecha_inicio) }} - {{ formatearFecha(reserva.fecha_fin) }}
            </div>
            <div class="reserva-dias">{{ calcularDias(reserva.fecha_inicio, reserva.fecha_fin) }} días</div>
          </div>
        </div>
        <div v-else class="sin-reservas">
          <p><i class="fas fa-calendar-check"></i> No hay reservas en este mes</p>
        </div>
      </div>
    </div>

    <p v-if="error" class="error-message">{{ error }}</p>
  </div>

  <p v-else class="error-message">
    No estás autorizado. Inicia sesión como dueño de clínica.
  </p>
</template>

<script>
import api from '@/api/axios'

export default {
  name: 'CalendarioReservasHabitacion',
  props: {
    habitacion_id: {
      type: [String, Number],
      required: true
    }
  },
  data () {
    return {
      jwtValido: false,
      loading: true,
      error: '',
      reservas: [],
      habitacionNombre: '',
      mesActual: new Date().getMonth(),
      añoActual: new Date().getFullYear(),
      info_usuario: null,
      diasCalendario: [],
      colorMap: {}
    }
  },
  computed: {
    nombreMes () {
      const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
      return meses[this.mesActual]
    },
    reservasDelMes () {
      return this.reservas.filter(r => {
        const fechaInicio = r.fecha_inicio.split('T')[0]
        const fechaFin = r.fecha_fin.split('T')[0]
        const primerDia = `${this.añoActual}-${String(this.mesActual + 1).padStart(2, '0')}-01`
        const ultimoDiaDate = new Date(this.añoActual, this.mesActual + 1, 0)
        const ultimoDia = `${ultimoDiaDate.getFullYear()}-${String(ultimoDiaDate.getMonth() + 1).padStart(2, '0')}-${String(ultimoDiaDate.getDate()).padStart(2, '0')}`

        return (fechaInicio <= ultimoDia && fechaFin > primerDia)
      }).sort((a, b) => new Date(a.fecha_inicio) - new Date(b.fecha_inicio))
    }
  },
  created () {
    this.checkAuth()
    if (this.jwtValido) {
      this.cargarDatos()
    }
    window.addEventListener('logout', this.checkAuth)
  },
  beforeUnmount () {
    window.removeEventListener('logout', this.checkAuth)
  },
  mounted () {
    // Los datos ya se cargan en created() si el auth es válido
  },
  watch: {
    mesActual () {
      this.generarCalendario()
    },
    reservas () {
      this.generarCalendario()
    }
  },
  methods: {
    checkAuth () {
      const token = localStorage.getItem('jwt')
      const raw = localStorage.getItem('user')
      if (!token || !raw) {
        this.jwtValido = false
        return
      }
      try {
        this.info_usuario = JSON.parse(raw)
        // Validar que el objeto tiene la estructura esperada
        if (!this.info_usuario || typeof this.info_usuario.tipo !== 'string') {
          this.jwtValido = false
          localStorage.removeItem('jwt')
          localStorage.removeItem('user')
          return
        }
        if (this.info_usuario.tipo !== 'prop_clinica' && this.info_usuario.tipo !== 'admin') {
          this.jwtValido = false
          return
        }
        this.jwtValido = true
      } catch (e) {
        this.jwtValido = false
        localStorage.removeItem('jwt')
        localStorage.removeItem('user')
        console.error('Error al parsear usuario:', e)
      }
    },
    async cargarDatos () {
      try {
        this.loading = true
        this.error = ''
        const { data } = await api.get(`/reservas/habitacion/${this.habitacion_id}`)
        this.reservas = data.reservas
        this.habitacionNombre = data.habitacion_nombre
        this.generarCalendario()
      } catch (e) {
        if (e.response && e.response.status === 403) {
          this.error = 'No tienes permiso para ver estas reservas.'
        } else if (e.response && e.response.status === 404) {
          this.error = 'La habitación no existe.'
        } else {
          this.error = 'Error al cargar los datos. Intenta de nuevo.'
        }
        console.error('Error en cargarDatos:', e)
      } finally {
        this.loading = false
      }
    },
    generarCalendario () {
      const primerDiaDelMes = new Date(this.añoActual, this.mesActual, 1)
      const ultimoDiaDelMes = new Date(this.añoActual, this.mesActual + 1, 0)
      const primerDiaDeLaSemana = primerDiaDelMes.getDay() === 0 ? 6 : primerDiaDelMes.getDay() - 1

      const dias = []

      const diasDelMesAnterior = new Date(this.añoActual, this.mesActual, 0).getDate()
      for (let i = primerDiaDeLaSemana - 1; i >= 0; i--) {
        const numero = diasDelMesAnterior - i
        const fecha = new Date(this.añoActual, this.mesActual - 1, numero)
        dias.push(this.crearDiaCalendario(numero, fecha, false))
      }

      for (let numero = 1; numero <= ultimoDiaDelMes.getDate(); numero++) {
        const fecha = new Date(this.añoActual, this.mesActual, numero)
        dias.push(this.crearDiaCalendario(numero, fecha, true))
      }

      let contadorMesSiguiente = 1
      const diasRestantes = 42 - dias.length
      for (let i = 0; i < diasRestantes; i++) {
        const fecha = new Date(this.añoActual, this.mesActual + 1, contadorMesSiguiente)
        dias.push(this.crearDiaCalendario(contadorMesSiguiente, fecha, false))
        contadorMesSiguiente++
      }

      this.diasCalendario = dias
    },
    crearDiaCalendario (numero, fecha, mesActual) {
      const fechaStr = this.formatearFechaLocal(fecha)
      const reservasDelDia = this.reservas.filter(r => {
        const inicio = r.fecha_inicio.split('T')[0]
        const fin = r.fecha_fin.split('T')[0]
        return fechaStr >= inicio && fechaStr <= fin
      })

      const hoy = new Date()
      const esHoy = fecha.getDate() === hoy.getDate() &&
        fecha.getMonth() === hoy.getMonth() &&
        fecha.getFullYear() === hoy.getFullYear()

      return {
        numero,
        fecha,
        fechaStr,
        mesActual,
        esHoy,
        reservas: reservasDelDia
      }
    },
    mesAnterior () {
      this.mesActual--
      if (this.mesActual < 0) {
        this.mesActual = 11
        this.añoActual--
      }
    },
    mesSiguiente () {
      this.mesActual++
      if (this.mesActual > 11) {
        this.mesActual = 0
        this.añoActual++
      }
    },
    calcularDias (fechaInicio, fechaFin) {
      const inicio = new Date(fechaInicio)
      const fin = new Date(fechaFin)
      const diferencia = fin - inicio
      return Math.ceil(diferencia / (1000 * 60 * 60 * 24))
    },
    formatearFecha (isoString) {
      const fecha = new Date(isoString)
      const dia = fecha.getDate().toString().padStart(2, '0')
      const mes = (fecha.getMonth() + 1).toString().padStart(2, '0')
      const año = fecha.getFullYear()
      return `${dia}/${mes}/${año}`
    },
    formatearFechaLocal (fecha) {
      const dia = fecha.getDate().toString().padStart(2, '0')
      const mes = (fecha.getMonth() + 1).toString().padStart(2, '0')
      const año = fecha.getFullYear()
      return `${año}-${mes}-${dia}`
    },
    generarColor (reservaId) {
      if (!this.colorMap[reservaId]) {
        const colores = [
          '#3498db',
          '#e74c3c',
          '#2ecc71',
          '#f39c12',
          '#9b59b6',
          '#1abc9c',
          '#e67e22',
          '#34495e'
        ]
        this.colorMap[reservaId] = colores[Object.keys(this.colorMap).length % colores.length]
      }
      return this.colorMap[reservaId]
    },
    volverAtras () {
      this.$router.back()
    }
  }
}
</script>

<style scoped>
@import './css/CalendarioReservasHabitacion.css';
</style>
