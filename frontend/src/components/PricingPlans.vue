<template>
  <div class="pricing-container">
    <h1 class="page-title">My clinics</h1>
    <h2 class="page-subtitle">Manage your pricing plan</h2>

    <div v-if="jwtValido">
      <div class="plans-grid">
        <div v-for="plan in orderedPricingPlans" :key="plan.name" class="plan-card"
          :class="{ 'current-plan': isCurrentPlan(plan.name) }">

          <div class="plan-header">
            <h3>{{ plan.name }}</h3>
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
            <button class="change-plan-btn" @click="changePlan(plan.name)" :disabled="isCurrentPlan(plan.name)">
              {{ isCurrentPlan(plan.name) ? 'CURRENT PLAN' : 'Change to plan' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="addOns && Object.keys(addOns).length" class="addons-section">
        <h3>Available Add-ons</h3>
        <div class="addons-grid">
          <div v-for="(addon, addonKey) in addOns" :key="addonKey" class="addon-card">
            <div v-if="getAddonQuantity(addonKey) > 0" class="addon-quantity-badge">
              Contratado: {{ getAddonQuantity(addonKey) }}
              <span v-if="getAddonMaxQuantity(addon) !== 'Sin límite'">
                / {{ getAddonMaxQuantity(addon) }}
              </span>
            </div>

            <h4>{{ addon.name || addonKey }}</h4>
            <p class="addon-description">{{ addon.description }}</p>
            <p class="addon-price">€{{ addon.price }}</p>

            <div class="addon-details" style="margin: 15px 0; font-size: 0.9em; background: #f8f9fa; padding: 10px; border-radius: 8px;">
              <p v-if="getAddonIncrementText(addon)" style="margin: 0 0 5px 0;">
                <strong>Aumenta:</strong> {{ getAddonIncrementText(addon) }}
              </p>
              <p style="margin: 0;">
                <strong>Límite de compra:</strong> Máximo {{ getAddonMaxQuantity(addon) }}
              </p>
            </div>

            <button
              class="change-plan-btn"
              @click="subscribeToAddon(addonKey)"
              :disabled="isAddonMaxedOut(addonKey, addon)"
              :style="isAddonMaxedOut(addonKey, addon) ? 'background-color: #ccc; cursor: not-allowed;' : ''"
            >
              {{ isAddonMaxedOut(addonKey, addon) ? 'Límite alcanzado' : 'Subscribe' }}
            </button>
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
      planUserActual: null,
      errorEdicion: '',
      loading: false
    }
  },

  computed: {
    // Orden visual: SILVER -> GOLD -> PLATINUM
    orderedPricingPlans () {
      if (!this.datosPricing || !this.datosPricing.plans) return []

      const order = ['SILVER', 'GOLD', 'PLATINUM']

      return order
        .filter(planName => this.datosPricing.plans[planName])
        .map(planName => {
          return {
            name: planName,
            ...this.datosPricing.plans[planName]
          }
        })
    },

    addOns () {
      if (!this.datosPricing || !this.datosPricing.addOns || !this.planUserActual) return {}

      const allAddons = this.datosPricing.addOns
      const filteredAddons = {}

      Object.keys(allAddons).forEach(key => {
        const addon = allAddons[key]
        if (addon.availableFor && addon.availableFor.includes(this.planUserActual)) {
          filteredAddons[key] = addon
        }
      })
      return filteredAddons
    },

    featureDescriptions () {
      if (!this.datosPricing || !this.datosPricing.features) return {}
      const descriptions = {}
      Object.keys(this.datosPricing.features).forEach(key => {
        descriptions[key] = this.datosPricing.features[key].description
      })
      return descriptions
    }
  },

  async created () {
    this.checkAuth()
    window.addEventListener('logout', this.checkAuth)
    await this.obtenerContrato()
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
        if (parsedContrato) {
          this.planUserActual = parsedContrato.subscriptionPlans.PetClinic || parsedContrato.subscriptionPlans.petclinic || null
        }
      } catch (e) {
        this.jwtValido = false
      }
    },

    async obtenerPlanes () {
      if (!this.jwtValido) return
      this.loading = true
      try {
        const serviceName = 'PetClinic'
        const version = '1.0.3'
        const response = await api.get(`http://localhost:5000/api/contratos/services/${serviceName}/pricing/${version}`)
        if (response.data) {
          this.datosPricing = response.data
        }
      } catch (error) {
        console.error('Error al obtener planes:', error)
      } finally {
        this.loading = false
      }
    },

    getAddonQuantity (addonKey) {
      const rawContrato = localStorage.getItem('contrato')
      if (!rawContrato) return 0
      try {
        const contrato = JSON.parse(rawContrato)
        const petClinicAddons = contrato.subscriptionAddOns?.PetClinic || contrato.subscriptionAddOns?.petclinic || {}
        const addonData = petClinicAddons[addonKey]

        if (addonData !== undefined) {
          return typeof addonData === 'number' ? addonData : (addonData.quantity || 0)
        }
        return 0
      } catch (e) {
        return 0
      }
    },

    getFeatureName (featureKey) {
      const featureMap = {
        petHotelCalendar: 'Pet Hotel Calendar',
        visitCalendar: 'Visit Calendar',
        registeredPets: 'Registered Pets',
        registeredClinics: 'Registered Clinics',
        petHotelManagement: 'Pet Hotel Management',
        registeredPetOwners: 'Registered Pet Owners'
      }
      return featureMap[featureKey] || featureKey
    },

    getLimitName (limitKey) {
      const limitMap = {
        maxRegisteredPets: 'Max Pets',
        maxRegisteredClinics: 'Max Clinics',
        maxPetHotelRooms: 'Max Pet Hotel Rooms',
        maxRegisteredPetOwners: 'Max Pet Owners'
      }
      return limitMap[limitKey] || limitKey
    },

    isCurrentPlan (planName) {
      return this.planUserActual === planName
    },

    async changePlan (planName) {
      if (!this.jwtValido) return
      try {
        const response = await api.put(`http://localhost:5000/api/contratos/update/${this.info_usuario.id}`, {
          newPlan: planName
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('jwt')}` }
        })

        const nuevoPlan = response.data.subscriptionPlans.PetClinic || response.data.subscriptionPlans.petclinic || planName
        this.planUserActual = nuevoPlan

        const contratoActual = JSON.parse(localStorage.getItem('contrato') || '{}')
        if (!contratoActual.subscriptionPlans) contratoActual.subscriptionPlans = {}
        contratoActual.subscriptionPlans.PetClinic = nuevoPlan
        localStorage.setItem('contrato', JSON.stringify(contratoActual))

        window.dispatchEvent(new Event('contrato-updated'))
        alert(`Plan cambiado a ${planName} exitosamente`)
        this.$router.go()
      } catch (error) {
        this.errorEdicion = 'Error al cambiar de plan.'
      }
    },

    async subscribeToAddon (addonKey) {
      if (!this.jwtValido) return
      if (!confirm(`¿Estás seguro de que deseas suscribirte al addon: ${addonKey}?`)) return

      this.loading = true
      try {
        const response = await api.put(`http://localhost:5000/api/contratos/contractAddon/${this.info_usuario.id}`, {
          addons: addonKey
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('jwt')}` }
        })

        localStorage.setItem('contrato', JSON.stringify(response.data))
        window.dispatchEvent(new Event('contrato-updated'))
        alert(`Te has suscrito a ${addonKey} correctamente.`)
        this.$router.go()
      } catch (error) {
        alert(error.response?.data?.error || 'Error en la suscripción.')
      } finally {
        this.loading = false
      }
    },

    async obtenerContrato () {
      try {
        const token = localStorage.getItem('jwt') || localStorage.getItem('token')
        const response = await api.get(`http://localhost:5000/api/contratos/getContract/${this.info_usuario.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.data) {
          this.planUserActual = response.data.subscriptionPlans.PetClinic || response.data.subscriptionPlans.petclinic
          localStorage.setItem('contrato', JSON.stringify(response.data))
        }
      } catch (error) {
        console.error('Error al obtener contrato')
      }
    },

    getAddonMaxQuantity (addon) {
      const constraints = addon.subscriptionConstraints || addon.subscriptionContraint || {}
      return constraints.maxQuantity || 'Sin límite'
    },

    getAddonIncrementText (addon) {
      if (!addon.usageLimitsExtensions) return null
      const keys = Object.keys(addon.usageLimitsExtensions)
      if (keys.length === 0) return null
      const limitKey = keys[0]
      const val = addon.usageLimitsExtensions[limitKey]
      const num = (typeof val === 'object') ? val.value : val
      return `+${num} ${this.getLimitName(limitKey)}`
    },

    isAddonMaxedOut (addonKey, addon) {
      const currentQty = this.getAddonQuantity(addonKey)
      const maxQty = this.getAddonMaxQuantity(addon)
      return maxQty !== 'Sin límite' && currentQty >= maxQty
    }
  }
}
</script>

<style scoped>
@import './css/PricingPlan.css';
/* He eliminado los estilos de .current-badge de aquí
   para que no interfieran con tu CSS original */
</style>
