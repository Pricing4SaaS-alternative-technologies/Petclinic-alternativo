<template>
  <Feature id="petclinic-visitCalendar">
    <template #on>
      <div class="calendario-container" v-if="jwtValido">
        <div class="calendario-header">
          <h1 class="calendario-title">📅 Calendario de Visitas</h1>
          <p class="calendario-description">
            Visualiza todas las próximas visitas de tus mascotas en un calendario interactivo
          </p>
        </div>

        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Cargando calendario...</p>
        </div>

        <div v-else class="calendario-content">
          <div class="calendario-controls">
            <button @click="mesAnterior" class="nav-btn">← Mes Anterior</button>
            <h2 class="mes-actual">{{ nombreMes }} {{ añoActual }}</h2>
            <button @click="mesSiguiente" class="nav-btn">Mes Siguiente →</button>
          </div>

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
                :class="['dia', { 'otro-mes': !dia.mesActual }, { 'hoy': dia.esHoy }, { 'tiene-visita': dia.visitas.length > 0 }]"
                @click="seleccionarDia(dia)"
              >
                <div class="numero-dia">{{ dia.numero }}</div>
                <div v-if="dia.visitas.length > 0" class="visitas-en-celda">
                  <div v-for="(visita) in dia.visitas.slice(0, 2)" :key="visita.id" class="visita-mini">
                    <span class="visita-mini-hora">{{ formatearHora(visita.date_time) }}</span>
                    <span class="visita-mini-mascota">{{ visita.mascota }}</span>
                  </div>
                  <div v-if="dia.visitas.length > 2" class="visita-mini-mas">
                    +{{ dia.visitas.length - 2 }} más
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="detalles-panel">
            <div v-if="diaSeleccionado" class="dia-detalles">
              <h3>{{ formatearFechaLarga(diaSeleccionado.fecha) }}</h3>
              <div v-if="diaSeleccionado.visitas.length > 0" class="visitas-del-dia">
                <div v-for="visita in diaSeleccionado.visitas" :key="visita.id" class="visita-detalle">
                  <div class="visita-header">
                    <span class="mascota-nombre">🐾 {{ visita.mascota }}</span>
                    <span class="hora">{{ formatearHora(visita.date_time) }}</span>
                  </div>
                  <p class="visita-descripcion">{{ visita.description }}</p>
                </div>
              </div>
              <div v-else class="sin-visitas">
                <p>No hay visitas registradas para este día</p>
              </div>
            </div>
            <div v-else class="sin-seleccion">
              <p>Selecciona un día para ver los detalles de las visitas</p>
            </div>
          </div>
        </div>

        <div v-if="visitasProximas.length > 0" class="proximas-visitas">
          <h3>Próximas Visitas</h3>
          <ul class="lista-proximas">
            <li v-for="visita in visitasProximas" :key="visita.id" class="visita-item">
              <div class="visita-item-content">
                <span class="fecha-hora">{{ formatearFecha(visita.date_time) }}</span>
                <span class="mascota">{{ visita.mascota }}</span>
                <span class="descripcion">{{ visita.description }}</span>
              </div>
            </li>
          </ul>
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>
      </div>

      <p v-else class="error-message">
        No estás autorizado. Inicia sesión como dueño de mascota.
      </p>
    </template>
    <template #fallback>
      <p class="error-message">
        El plan asignado no permite el acceso al calendario de visitas. Contacta con tu clínica para más información.
      </p>
    </template>
  </Feature>
</template>

<script>
import api from '@/api/axios'
import { syncSpaceToken } from '@/utils/spaceSync'
import { Feature } from '@npm_team/space-vue-client'

export default {
  name: 'CalendarioVisitas',
  components: {
    Feature
  },
  data () {
    return {
      jwtValido: false,
      loading: true,
      error: '',
      visitas: [],
      mesActual: new Date().getMonth(),
      añoActual: new Date().getFullYear(),
      diaSeleccionado: null,
      diasCalendario: [],
      info_usuario: null
    }
  },
  computed: {
    nombreMes () {
      const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
      return meses[this.mesActual]
    },
    visitasProximas () {
      return this.visitas
        .filter(v => new Date(v.date_time) >= new Date())
        .sort((a, b) => new Date(a.date_time) - new Date(b.date_time))
        .slice(0, 5)
    }
  },
  async created () {
    await this.checkAuth()
    window.addEventListener('logout', this.checkAuth)
  },
  beforeUnmount () {
    window.removeEventListener('logout', this.checkAuth)
  },
  mounted () {
    this.generarCalendario()
  },
  watch: {
    mesActual () {
      this.generarCalendario()
    },
    visitas () {
      this.generarCalendario()
    }
  },
  methods: {
    async checkAuth () {
      const token = localStorage.getItem('jwt')
      const raw = localStorage.getItem('user')
      if (!token || !raw) {
        this.jwtValido = false
        return
      }
      this.info_usuario = JSON.parse(raw)
      if (this.info_usuario.tipo !== 'prop_mascota') {
        this.jwtValido = false
        return
      }
      this.jwtValido = true
      await syncSpaceToken(this.$router)
      this.cargarDatos()
    },
    async cargarDatos () {
      try {
        this.loading = true
        this.error = ''
        const clinicaId = this.info_usuario.clinica_id
        const { data } = await api.get(`/clinicas/${clinicaId}/props_mascotas/mine/visitas`)
        this.visitas = data
        this.generarCalendario()
      } catch (e) {
        this.error = 'Error al cargar los datos. Intenta de nuevo.'
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
      const fechaStr = fecha.toISOString().split('T')[0]
      const visitasDelDia = this.visitas.filter(v => {
        const visitaFecha = v.date_time.split('T')[0]
        return visitaFecha === fechaStr
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
        visitas: visitasDelDia
      }
    },
    seleccionarDia (dia) {
      if (!dia.mesActual) return
      this.diaSeleccionado = dia
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
    formatearFecha (isoString) {
      const fecha = new Date(isoString)
      const dia = fecha.getDate().toString().padStart(2, '0')
      const mes = (fecha.getMonth() + 1).toString().padStart(2, '0')
      const año = fecha.getFullYear()
      const horas = fecha.getHours().toString().padStart(2, '0')
      const minutos = fecha.getMinutes().toString().padStart(2, '0')
      return `${dia}/${mes}/${año} ${horas}:${minutos}`
    },
    formatearFechaLarga (fecha) {
      const opciones = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
      return fecha.toLocaleDateString('es-ES', opciones)
    },
    formatearHora (isoString) {
      const fecha = new Date(isoString)
      const horas = fecha.getHours().toString().padStart(2, '0')
      const minutos = fecha.getMinutes().toString().padStart(2, '0')
      return `${horas}:${minutos}`
    }
  }
}
</script>

<style scoped>
@import './css/CalendarioVisitas.css';
</style>
