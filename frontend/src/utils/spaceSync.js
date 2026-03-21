import axios from 'axios'
import { tokenService } from '@npm_team/space-vue-client'

export const syncSpaceToken = async (router) => {
  const user = JSON.parse(localStorage.getItem('user'))
  const jwt = localStorage.getItem('jwt')
  const spaceToken = localStorage.getItem('spaceToken')

  if (!user || !jwt) {
    if (router) router.push('/login')
    return
  }
  let antiguoPayload
  try {
    if (!spaceToken) {
      console.warn('No disponemos de payload anterior en LocalStorage')
      antiguoPayload = null
    } else {
      antiguoPayload = JSON.parse((atob(spaceToken.split('.')[1]))) || null
    }
  } catch (error) {
    console.error('Error obteniendo el payload antiguo:', error)
  }

  const antiguoPricingContext = antiguoPayload ? JSON.stringify(antiguoPayload.pricingContext) : null
  console.log('Antiguo Pricing:', antiguoPricingContext)
  const antiguoSubscriptionContext = antiguoPayload ? JSON.stringify(antiguoPayload.subscriptionContext) : null
  console.log('Antiguo Subscription:', antiguoSubscriptionContext)

  try {
    const res = await axios.post(
      `http://localhost:5000/api/contratos/generate-token/${user.id}`,
      {},
      { headers: { Authorization: `Bearer ${jwt}` } }
    )

    const nuevoToken = res.data.token
    console.log('Token:', nuevoToken)
    const nuevoPayload = nuevoToken ? JSON.parse((atob(nuevoToken.split('.')[1]))) : null

    const nuevoPricing = nuevoPayload ? JSON.stringify(nuevoPayload.pricingContext) : null
    console.log('Nuevo Pricing:', nuevoPricing)
    const nuevoSubscriptionContext = nuevoPayload ? JSON.stringify(nuevoPayload.subscriptionContext) : null
    console.log('Nuevo Subscription:', nuevoSubscriptionContext)

    if (antiguoPricingContext !== nuevoPricing || antiguoSubscriptionContext !== nuevoSubscriptionContext) {
      localStorage.setItem('spaceToken', nuevoToken)
      console.log('¡EL CONTENIDO DEL TOKEN HA CAMBIADO REALMENTE!')
      console.log('Nuevo Contexto:', nuevoPayload.subscriptionContext)
    } else {
      console.log('El token se ha refrescado (iat nuevo), pero los permisos son idénticos.')
    }
    tokenService.update(nuevoToken)
  } catch (error) {
    console.error('Error sincronizando token:', error)
  }
}
