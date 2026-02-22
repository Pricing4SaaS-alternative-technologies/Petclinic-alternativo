import axios from 'axios'
import { tokenService } from '@npm_team/space-vue-client'
import { spaceState } from '@/main'

export const syncSpaceToken = async (router) => {
  const user = JSON.parse(localStorage.getItem('user'))
  const jwt = localStorage.getItem('jwt')

  if (!user || !jwt) {
    if (router) router.push('/login')
    return
  }
  let antiguoPayload
  try {
    antiguoPayload = spaceState.payload || null
  } catch (error) {
    console.error('Error obteniendo el payload antiguo:', error)
  }
  console.log('Antiguo Payload:', antiguoPayload)
  const antiguoStr = antiguoPayload ? JSON.stringify(antiguoPayload.subscriptionContext) : null

  try {
    const res = await axios.post(
      `http://localhost:5000/api/contratos/generate-token/${user.id}`,
      {},
      { headers: { Authorization: `Bearer ${jwt}` } }
    )

    const nuevoToken = res.data.token
    console.log('Token:', nuevoToken)

    const nuevoPayload = nuevoToken ? JSON.parse((atob(nuevoToken.split('.')[1]))) : null
    console.log('Nuevo Payload:', nuevoPayload)
    const nuevoStr = nuevoPayload ? JSON.stringify(nuevoPayload.subscriptionContext) : null

    if (antiguoStr !== nuevoStr) {
      console.log('Antiguo Contexto:', antiguoStr)
      console.log('Nuevo Contexto:', nuevoStr)
      tokenService.update(nuevoToken)
      console.log('¡EL CONTENIDO DEL TOKEN HA CAMBIADO REALMENTE!')
      console.log('Nuevo Contexto:', nuevoPayload.subscriptionContext)
    } else {
      console.log('El token se ha refrescado (iat nuevo), pero los permisos son idénticos.')
    }
  } catch (error) {
    console.error('Error sincronizando token:', error)
  }
}
