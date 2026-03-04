import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const api = {
  async getItems() {
    const response = await apiClient.get('/api/items')
    return response.data
  },

  async getItem(id) {
    const response = await apiClient.get(`/api/items/${id}`)
    return response.data
  },

  async createItem(item) {
    const response = await apiClient.post('/api/items', item)
    return response.data
  },

  async healthCheck() {
    const response = await apiClient.get('/health')
    return response.data
  }
}

export default apiClient
