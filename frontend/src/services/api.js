import axios from 'axios'

const apiClient = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || '') + '/api',
  headers: { 'Content-Type': 'application/json' }
})

// Attach JWT to every request if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Redirect to login on 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('user_email')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login:  (email, password) => apiClient.post('/auth/login',  { email, password }),
  signup: (email, password) => apiClient.post('/auth/signup', { email, password }),
  logout: ()               => apiClient.post('/auth/logout'),
  me:     ()               => apiClient.get('/auth/me'),
}

export const portfolioApi = {
  getHoldings: ()                       => apiClient.get('/portfolio/'),
  getHistory:  (period = '1mo')         => apiClient.get('/portfolio/history', { params: { period } }),
  deposit:     (currency, amount)       => apiClient.post('/portfolio/deposit',  { currency, amount }),
  withdraw:    (currency, amount)       => apiClient.post('/portfolio/withdraw', { currency, amount }),
}

export const tradeApi = {
  exchange:   (from_currency, to_currency, amount) =>
    apiClient.post('/trade/exchange', { from_currency, to_currency, amount }),
  transfer:   (to_email, currency, amount) =>
    apiClient.post('/trade/transfer', { to_email, currency, amount }),
  getHistory: () => apiClient.get('/trade/history'),
  getRate:    (from_currency, to_currency) =>
    apiClient.get('/trade/rate', { params: { from_currency, to_currency } }),
}

export const forexApi = {
  getRate:       (from, to) => apiClient.get(`/forex/rate/${from}/${to}`),
  getRates:      (pairs)    => apiClient.get('/forex/rates', pairs ? { params: { pairs } } : {}),
  getCurrencies: ()         => apiClient.get('/forex/currencies'),
}

export const preferencesApi = {
  get:    ()     => apiClient.get('/preferences/'),
  update: (data) => apiClient.put('/preferences/', data),
}

export const llmApi = {
  chat:        (messages)  => apiClient.post('/llm/chat', { messages }),
  // Admin-only key management
  getKeys:     ()          => apiClient.get('/llm/keys'),
  createKey:   (data)      => apiClient.post('/llm/keys', data),
  activateKey: (keyId)     => apiClient.put(`/llm/keys/${keyId}/activate`),
  deleteKey:   (keyId)     => apiClient.delete(`/llm/keys/${keyId}`),
}

export const newsApi = {
  getNews: (currency, limit, q) => apiClient.get('/news', { params: { currency, limit, q } }),
}

export default apiClient
