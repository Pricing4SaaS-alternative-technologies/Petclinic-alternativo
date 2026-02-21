import axios from 'axios'
import { tokenService } from '@npm_team/space-vue-client'

/* Lógica centralizada para sincronizar el token de SPACE */
export const syncSpaceToken = async (router) => {
  console.log('Sincronizando token de SPACE...')

  const user = JSON.parse(localStorage.getItem('user'))
  const jwt = localStorage.getItem('jwt')

  if (!user || !jwt) {
    if (router) router.push('/login')
    return
  }

  try {
    const payload = tokenService.getPayload()

    // Si no hay token o es de otro usuario, lo regeneramos
    if (!payload || payload.sub !== String(user.id)) {
      const res = await axios.post(
        `http://localhost:5000/api/contratos/generate-token/${user.id}`,
        {},
        {
          headers: { Authorization: `Bearer ${jwt}` }
        }
      )

      console.log('SPACE: Nuevo token obtenido y actualizado')
      console.log('Token obtenido', res.data.token)
      tokenService.update(res.data.token)
    }
  } catch (error) {
    console.error('Error en la sincronización de SPACE:', error)
    // Opcional: si falla el token de precios, podrías redirigir o manejar el error
  }
}
