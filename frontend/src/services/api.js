import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000',
})

// Add request interceptor to debug authentication
api.interceptors.request.use((config) => {
  console.log('API Request:', config.method?.toUpperCase(), config.url)
  console.log('Headers:', config.headers)
  return config
})

// Add response interceptor to debug errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log('API Error:', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)

export async function parseText(text) {
  const { data } = await api.post('/parse', { text })
  return data // { title, start, end }
}

export async function createEvent(payload) {
  const { data } = await api.post('/events', payload)
  return data // saved event
}

export async function listEvents() {
  const { data } = await api.get('/events')
  return data // array of events
}

export async function deleteEvent(eventId) {
  const { data } = await api.delete(`/events/${eventId}`)
  return data
}

export default api