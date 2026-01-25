<template>
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

    <div v-else-if="mascotas.length === 0" class="no-mascotas">
      <p>No tienes mascotas registradas. Crea una para ver tus visitas.</p>
    </div>

    <div v-else class="calendario-content">
      <!-- Selector de mes/año -->
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
            :class="['dia', { 'otro-mes': !dia.mesActual }, { 'hoy': dia.esHoy }, { 'tiene-visita': dia.visitas.length > 0 }]"
            @click="seleccionarDia(dia)"
          >
            <div class="numero-dia">{{ dia.numero }}</div>
            <div v-if="dia.visitas.length > 0" class="visitas-en-celda">
              <div v-for="(visita) in dia.visitas.slice(0, 2)" :key="visita.id" class="visita-mini">
                <span class="visita-mini-hora">{{ formatearHora(visita.fecha) }}</span>
                <span class="visita-mini-mascota">{{ visita.mascota_nombre }}</span>
              </div>
              <div v-if="dia.visitas.length > 2" class="visita-mini-mas">
                +{{ dia.visitas.length - 2 }} más
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel de detalles -->
      <div class="detalles-panel">
        <div v-if="diaSeleccionado" class="dia-detalles">
          <h3>{{ formatearFechaLarga(diaSeleccionado.fecha) }}</h3>
          <div v-if="diaSeleccionado.visitas.length > 0" class="visitas-del-dia">
            <div v-for="visita in diaSeleccionado.visitas" :key="visita.id" class="visita-detalle">
              <div class="visita-header">
                <span class="mascota-nombre">🐾 {{ visita.mascota_nombre }}</span>
                <span class="hora">{{ formatearHora(visita.fecha) }}</span>
              </div>
              <p class="visita-descripcion">{{ visita.descripcion }}</p>
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

    <!-- Listado de próximas visitas (complementario) -->
    <div v-if="visitasProximas.length > 0" class="proximas-visitas">
      <h3>Próximas Visitas</h3>
      <ul class="lista-proximas">
        <li v-for="visita in visitasProximas" :key="visita.id" class="visita-item">
          <div class="visita-item-content">
            <span class="fecha-hora">{{ formatearFecha(visita.fecha) }}</span>
            <span class="mascota">{{ visita.mascota_nombre }}</span>
            <span class="descripcion">{{ visita.descripcion }}</span>
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

<script>
import api from '@/api/axios'

export default {
  name: 'CalendarioVisitas',
  data () {
    return {
      jwtValido: false,
      loading: true,
      error: '',
      mascotas: [],
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
        .filter(v => new Date(v.fecha) >= new Date())
        .sort((a, b) => new Date(a.fecha) - new Date(b.fecha))
        .slice(0, 5)
    }
  },
  created () {
    this.checkAuth()
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
    checkAuth () {
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
      this.cargarDatos()
    },
    async cargarDatos () {
      try {
        this.loading = true
        this.error = ''

        // Cargar mascotas
        const mascotasRes = await api.get('/mascotas/listar-tus-mascotas')
        this.mascotas = mascotasRes.data

        // Cargar visitas de todas las mascotas
        const visitasArray = []
        for (const mascota of this.mascotas) {
          try {
            const visitasRes = await api.get(`/visitas/mascota/${mascota.id}`)
            const mascotaVisitas = visitasRes.data.map(v => ({
              ...v,
              mascota_nombre: mascota.nombre
            }))
            visitasArray.push(...mascotaVisitas)
          } catch (e) {
            console.error(`Error al cargar visitas de mascota ${mascota.id}:`, e)
          }
        }
        this.visitas = visitasArray
        this.generarCalendario()
      } catch (e) {
        console.error('Error al cargar datos:', e)
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

      // Días del mes anterior
      const diasDelMesAnterior = new Date(this.añoActual, this.mesActual, 0).getDate()
      for (let i = primerDiaDeLaSemana - 1; i >= 0; i--) {
        const numero = diasDelMesAnterior - i
        const fecha = new Date(this.añoActual, this.mesActual - 1, numero)
        dias.push(this.crearDiaCalendario(numero, fecha, false))
      }

      // Días del mes actual
      for (let numero = 1; numero <= ultimoDiaDelMes.getDate(); numero++) {
        const fecha = new Date(this.añoActual, this.mesActual, numero)
        dias.push(this.crearDiaCalendario(numero, fecha, true))
      }

      // Días del mes siguiente
      let contadorMesSiguiente = 1
      const diasRestantes = 42 - dias.length // 6 semanas * 7 días
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
        const visitaFecha = v.fecha.split('T')[0]
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
