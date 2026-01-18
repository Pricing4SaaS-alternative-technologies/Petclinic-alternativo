<template>
  <div class="pricing-container">
    <h1 class="page-title">My clinics</h1>
    <h2 class="page-subtitle">Manage your pricing plan</h2>

    <div v-if="jwtValido">
      <!-- Mostrar planes disponibles -->
      <div class="plans-grid">
        <div v-for="(plan, planName) in pricingPlans" :key="planName" class="plan-card"
          :class="{ 'current-plan': isCurrentPlan(planName) }">
          <div class="plan-header">
            <h3>{{ planName }}</h3>
            <div class="plan-price">
              <span v-if="plan.price === 0">FREE</span>
              <span v-else>€{{ plan.price }}/month</span>
            </div>
            <p class="plan-description">{{ plan.description }}</p>
          </div>

          <div class="plan-features">
            <h4>Features:</h4>
            <ul>
              <li v-for="(isActive, featureKey) in plan.features" :key="featureKey">
                <span class="feature-icon" :class="{ 'feature-active': isActive, 'feature-inactive': !isActive }">
                  {{ isActive ? '✓' : '✗' }}
                </span>
                <span class="feature-name">{{ getFeatureName(featureKey) }}</span>
                <span v-if="featureDescriptions[featureKey]" class="feature-description">
                  {{ featureDescriptions[featureKey] }}
                </span>
              </li>
            </ul>
          </div>

          <div class="plan-limits">
            <h4>Usage Limits:</h4>
            <ul>
              <li v-for="(limitValue, limitKey) in plan.usageLimits" :key="limitKey">
                <span class="limit-name">{{ getLimitName(limitKey) }}:</span>
                <span class="limit-value" v-if="limitValue === 'Unlimited' || limitValue === 100000000">Unlimited</span>
                <span class="limit-value" v-else>{{ limitValue }}</span>
              </li>
            </ul>
          </div>

          <div class="plan-actions">
            <button class="change-plan-btn" @click="changePlan(planName)" :disabled="isCurrentPlan(planName)">
              {{ isCurrentPlan(planName) ? 'CURRENT PLAN' : 'Change to plan' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Add-ons section -->
      <div v-if="addOns && Object.keys(addOns).length" class="addons-section">
        <h3>Available Add-ons</h3>
        <div class="addons-grid">
          <div v-for="(addon, addonKey) in addOns" :key="addonKey" class="addon-card">
            <h4>{{ addon.name }}</h4>
            <p class="addon-description">{{ addon.description }}</p>
            <p class="addon-price">€{{ addon.price }}</p>
            <p class="addon-available">Available for: {{ addon.availableFor.join(', ') }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-auth">
      <p class="error">You are not authorized to view this information. Please log in.</p>
    </div>

    <div v-if="errorEdicion" class="error-message">
      {{ errorEdicion }}
    </div>
  </div>
</template>

<script>
import api from '../api/axios'

export default {
  name: 'PricingPlans',

  data () {
    return {
      info_usuario: null,
      jwtValido: false,
      datosPricing: null,
      planUserActual: null, // Esto deberías obtenerlo del backend según el usuario
      errorEdicion: '',
      loading: false
    }
  },

  computed: {
    // Computed property para los planes principales
    pricingPlans () {
      if (!this.datosPricing || !this.datosPricing.plans) return {}
      return this.datosPricing.plans
    },

    // Computed property para los add-ons
    addOns () {
      if (!this.datosPricing || !this.datosPricing.addOns) return {}
      return this.datosPricing.addOns
    },

    // Computed property para las descripciones de features
    featureDescriptions () {
      if (!this.datosPricing || !this.datosPricing.features) return {}
      const descriptions = {}
      Object.keys(this.datosPricing.features).forEach(key => {
        descriptions[key] = this.datosPricing.features[key].description
      })
      return descriptions
    }
  },

  created () {
    this.checkAuth()
    window.addEventListener('logout', this.checkAuth)
  },

  beforeUnmount () {
    window.removeEventListener('logout', this.checkAuth)
  },

  methods: {
    checkAuth () {
      const token = localStorage.getItem('jwt')
      const rawUser = localStorage.getItem('user')
      const rawContrato = localStorage.getItem('contrato')
      const parsedContrato = rawContrato ? JSON.parse(rawContrato) : null

      if (!token || !rawUser) {
        this.jwtValido = false
        return
      }

      try {
        this.info_usuario = JSON.parse(rawUser)
        this.jwtValido = true
        this.obtenerPlanes()
        if (parsedContrato !== null && parsedContrato !== '') {
          this.planUserActual = parsedContrato.subscriptionPlans['petclinic'] || parsedContrato.subscriptionPlans['PetClinic'] || null
        }
      } catch (e) {
        console.error('Error al parsear el usuario:', e)
        this.jwtValido = false
      }
    },

    async obtenerPlanes () {
      if (!this.jwtValido) return

      this.loading = true
      this.errorEdicion = ''

      try {
        const serviceName = 'PetClinic'
        const version = '1.0.0'

        const response = await api.get(`http://localhost:5000/api/contratos/services/${serviceName}/pricing/${version}`)

        console.log('Datos de pricing:', response.data)

        if (response.data) {
          this.datosPricing = response.data
        } else {
          this.errorEdicion = 'No se recibieron datos de pricing'
        }
      } catch (error) {
        console.error('Error al obtener planes:', error)
      } finally {
        this.loading = false
      }
    },

    // Función para obtener nombres amigables de features
    getFeatureName (featureKey) {
      const featureMap = {
        'petHotelCalendar': 'Pet Hotel Calendar',
        'visitCalendar': 'Visit Calendar',
        'registeredPets': 'Registered Pets',
        'registeredClinics': 'Registered Clinics',
        'petHotelManagement': 'Pet Hotel Management',
        'registeredPetOwners': 'Registered Pet Owners'
      }
      return featureMap[featureKey] || featureKey
    },

    // Función para obtener nombres amigables de límites
    getLimitName (limitKey) {
      const limitMap = {
        'maxRegisteredPets': 'Max Pets',
        'maxRegisteredClinics': 'Max Clinics',
        'maxPetHotelRooms': 'Max Pet Hotel Rooms',
        'maxRegisteredPetOwners': 'Max Pet Owners'
      }
      return limitMap[limitKey] || limitKey
    },

    // Verificar si este es el plan actual del usuario
    isCurrentPlan (planName) {
      return this.planUserActual === planName
    },

    // Función para cambiar de plan
    async changePlan (planName) {
      if (!this.jwtValido) return

      try {
        const response = await api.put(`http://localhost:5000/api/contratos/update/${this.info_usuario.id}`, {
          newPlan: planName
        }, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`, // Asegurar el token
            'Content-Type': 'application/json'
          }
        })

        console.log(`Cambiando al plan ${planName}`, response.data)

        // Actualizar el plan actual del usuario
        this.planUserActual = response.data.subscriptionPlans['petclinic']

        // Mostrar mensaje de éxito
        alert(`Plan cambiado a ${planName} exitosamente`)
        await this.loadUserInfo()
      } catch (error) {
        console.error('Error al cambiar de plan:', error)
        this.errorEdicion = 'Error al cambiar de plan. Por favor, intenta nuevamente.'
      }
    },

    // Función para formatear números grandes
    formatNumber (value) {
      if (value >= 100000000) return 'Unlimited'
      return value.toLocaleString()
    }
  }
}
</script>

<style scoped>
@import './css/PricingPlan.css';
</style>
