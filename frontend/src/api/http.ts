import axios from 'axios'

const http = axios.create({ baseURL: '/dblens-api' })

function getRuoYiToken() {
  const tokenPair = document.cookie
    .split('; ')
    .find(item => item.startsWith('Admin-Token='))

  if (!tokenPair) return null

  const value = tokenPair.slice('Admin-Token='.length)
  return value ? decodeURIComponent(value) : null
}

http.interceptors.request.use((config) => {
  const token = getRuoYiToken()
  if (token) {
    config.headers = config.headers ?? {}
    if (!config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

http.interceptors.response.use(
  r => r,
  err => {
    const msg = err.response?.data?.detail || err.message
    return Promise.reject(new Error(msg))
  }
)

export default http
