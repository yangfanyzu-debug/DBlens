import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

http.interceptors.response.use(
  r => r,
  err => {
    const msg = err.response?.data?.detail || err.message
    return Promise.reject(new Error(msg))
  }
)

export default http
