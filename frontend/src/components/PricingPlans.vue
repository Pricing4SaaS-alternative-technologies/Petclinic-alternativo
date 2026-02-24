<template>
  <div class="pricing-container">
    <h1 class="page-title">My clinics</h1>
    <h2 class="page-subtitle">Manage your pricing plan</h2>

    <div v-if="jwtValido">
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

    // Computed property para los add-ons (AHORA FILTRADO)
    addOns () {
      if (!this.datosPricing || !this.datosPricing.addOns) return {}

      // Si no tenemos el plan actual cargado, no mostramos addons por seguridad
      if (!this.planUserActual) return {}

      const allAddons = this.datosPricing.addOns
      const filteredAddons = {}

      Object.keys(allAddons).forEach(key => {
        const addon = allAddons[key]
        // Solo incluimos el addon si el plan actual del usuario está en availableFor
        if (addon.availableFor && addon.availableFor.includes(this.planUserActual)) {
          filteredAddons[key] = addon
        }
      })

      return filteredAddons
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
        if (parsedContrato !== null && parsedContrato !== '') {
          this.planUserActual = parsedContrato.subscriptionPlans.petclinic || parsedContrato.subscriptionPlans.PetClinic || null
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
        const version = '1.0.3'

        const response = await api.get(`http://localhost:5000/api/contratos/services/${serviceName}/pricing/${version}`)

        console.log('Datos de los pricings:', response.data)

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

    getAddonQuantity (addonKey) {
      const rawContrato = localStorage.getItem('contrato')
      if (!rawContrato) return 0

      try {
        const contrato = JSON.parse(rawContrato)
        if (!contrato.subscriptionAddOns) return 0

        const petClinicAddons = contrato.subscriptionAddOns.PetClinic || contrato.subscriptionAddOns.petclinic || {}

        if (petClinicAddons[addonKey] !== undefined) {
          if (typeof petClinicAddons[addonKey] === 'number') {
            return petClinicAddons[addonKey]
          } else if (petClinicAddons[addonKey].quantity !== undefined) {
            return petClinicAddons[addonKey].quantity
          }
        }

        const oldAddonData = contrato.subscriptionAddOns[addonKey]
        if (oldAddonData && oldAddonData.quantity !== undefined) {
          return oldAddonData.quantity
        }

        return 0
      } catch (e) {
        console.error('Error leyendo cantidad de addon:', e)
        return 0
      }
    },

    // Función para obtener nombres amigables de features
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

    // Función para obtener nombres amigables de límites
    getLimitName (limitKey) {
      const limitMap = {
        maxRegisteredPets: 'Max Pets',
        maxRegisteredClinics: 'Max Clinics',
        maxPetHotelRooms: 'Max Pet Hotel Rooms',
        maxRegisteredPetOwners: 'Max Pet Owners'
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
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })

        console.log(`Cambiando al plan ${planName}`, response.data)

        const nuevoPlan = response.data.subscriptionPlans.PetClinic || response.data.subscriptionPlans.petclinic || planName

        this.planUserActual = nuevoPlan

        const contratoActual = JSON.parse(localStorage.getItem('contrato') || '{}')

        if (!contratoActual.subscriptionPlans) {
          contratoActual.subscriptionPlans = {}
        }

        // Actualizar el plan en el localStorage
        contratoActual.subscriptionPlans.PetClinic = nuevoPlan
        localStorage.setItem('contrato', JSON.stringify(contratoActual))

        window.dispatchEvent(new Event('contrato-updated')) // Para notificar a otros componentes que el contrato ha sido actualizado

        alert(`Plan cambiado a ${planName} exitosamente`)
        this.$router.go()
      } catch (error) {
        console.error('Error al cambiar de plan:', error)
        this.errorEdicion = 'Error al cambiar de plan. Por favor, intenta nuevamente.'
      }
    },

    async subscribeToAddon (addonKey) {
      if (!this.jwtValido) {
        alert('Debes iniciar sesión para contratar un addon.')
        return
      }

      // Confirmación simple al usuario
      if (!confirm(`¿Estás seguro de que deseas suscribirte al addon: ${addonKey}?`)) {
        return
      }

      this.loading = true
      this.errorEdicion = ''

      try {
        const response = await api.put(`http://localhost:5000/api/contratos/contractAddon/${this.info_usuario.id}`, {
          addons: addonKey
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt')}`,
            'Content-Type': 'application/json'
          }
        })

        console.log('Addon contratado exitosamente:', response.data)

        localStorage.setItem('contrato', JSON.stringify(response.data))

        window.dispatchEvent(new Event('contrato-updated'))

        alert(`Te has suscrito a ${addonKey} correctamente.`)
        // Opcional: recargar contrato localmente para actualizar badge sin refrescar
        this.obtenerContrato()
        this.$router.go()
      } catch (error) {
        console.error('Error al contratar addon:', error)
        this.errorEdicion = error.response?.data?.error || 'Error al procesar la suscripción del addon.'
        alert(this.errorEdicion)
      } finally {
        this.loading = false
      }
    },

    async actualizarDatosUsuario () {
      const rawContrato = localStorage.getItem('contrato')
      const parsedContrato = rawContrato ? JSON.parse(rawContrato) : null

      if (parsedContrato !== null) {
        this.planUserActual = parsedContrato.subscriptionPlans.PetClinic || parsedContrato.subscriptionPlans.petclinic || this.planUserActual
      }
    },

    async obtenerContrato () {
      try {
        const token = localStorage.getItem('token') || localStorage.getItem('jwt')
        const response = await api.get(`http://localhost:5000/api/contratos/getContract/${this.info_usuario.id}`, {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          }
        })

        const contrato = response.data
        console.log('¡CONTRATO RECUPERADO!', contrato)
        if (contrato) {
          this.planUserActual = contrato.subscriptionPlans.PetClinic || contrato.subscriptionPlans.petclinic
          localStorage.setItem('contrato', JSON.stringify(contrato))
        }
        return contrato
      } catch (error) {
        if (error.response && error.response.status === 404) {
          console.warn('El usuario no tiene un contrato activo.')
          return null
        }
        console.error('Error al obtener el contrato:', error)
      }
    },
    // Obtiene el máximo permitido (soporta posibles errores tipográficos del Swagger como subscriptionContraint)
    getAddonMaxQuantity (addon) {
      const constraints = addon.subscriptionConstraints || addon.subscriptionContraint || {}
      return constraints.maxQuantity || 'Sin límite'
    },

    // Genera el texto de cuánto aumenta ("+3 Max Pets")
    getAddonIncrementText (addon) {
      if (!addon.usageLimitsExtensions) return null

      const keys = Object.keys(addon.usageLimitsExtensions)
      if (keys.length === 0) return null

      const limitKey = keys[0]
      let limitValue = addon.usageLimitsExtensions[limitKey]

      // En el JSON, puede venir directamente como número (3) o como objeto { value: 3 }
      if (typeof limitValue === 'object' && limitValue !== null) {
        limitValue = limitValue.value
      }

      const friendlyName = this.getLimitName(limitKey)
      return `+${limitValue} ${friendlyName}`
    },

    // Comprueba si el usuario ya ha llegado al tope de compras de este add-on
    isAddonMaxedOut (addonKey, addon) {
      const currentQty = this.getAddonQuantity(addonKey)
      const maxQty = this.getAddonMaxQuantity(addon)

      if (maxQty === 'Sin límite') return false
      return currentQty >= maxQty
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
@import './css/PricingPlan.css'
</style>
