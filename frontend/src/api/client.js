import axios from 'axios'

// Local default: TaskFlow backend on port 8002.
// For deployment, set VITE_API_URL (e.g. your Railway URL) in Vercel env vars.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8002',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('taskflow_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('taskflow_token')
      localStorage.removeItem('taskflow_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api