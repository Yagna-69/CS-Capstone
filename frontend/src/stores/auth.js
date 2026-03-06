import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const accessToken  = ref(localStorage.getItem('access_token')  || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const userId       = ref(localStorage.getItem('user_id')       || null)
  const email        = ref(localStorage.getItem('user_email')    || null)

  const isLoggedIn = computed(() => !!accessToken.value)

  function _saveSession(data) {
    accessToken.value  = data.access_token
    refreshToken.value = data.refresh_token
    userId.value       = data.user_id
    email.value        = data.email
    localStorage.setItem('access_token',  data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user_id',       data.user_id)
    localStorage.setItem('user_email',    data.email)
  }

  function _clearSession() {
    accessToken.value  = null
    refreshToken.value = null
    userId.value       = null
    email.value        = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_email')
  }

  async function login(emailVal, password) {
    const { data } = await authApi.login(emailVal, password)
    _saveSession(data)
  }

  // Returns { requiresConfirmation: bool }
  async function signup(emailVal, password) {
    const response = await authApi.signup(emailVal, password)
    if (response.status === 202) {
      return { requiresConfirmation: true }
    }
    _saveSession(response.data)
    return { requiresConfirmation: false }
  }

  async function logout() {
    try { await authApi.logout() } catch { /* ignore if token already invalid */ }
    _clearSession()
  }

  return { accessToken, userId, email, isLoggedIn, login, signup, logout }
})
