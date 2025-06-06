import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('jwt')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    const token = localStorage.getItem('jwt')
    if (error.response && error.response.status === 401 && token) {
      localStorage.removeItem('jwt')
      localStorage.removeItem('user')
      window.dispatchEvent(new Event('logout'))
      window.location.href = '/auth'
      console.warn('Token expirado o inválido, se ha cerrado la sesion automáticamente.')
    }
    return Promise.reject(error)
  }
)

export default api
