import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api'

// All localStorage keys that belong to the currently logged-in user.
// Wipe these on logout so the next account starts clean.
const USER_LS_KEYS = [
  'access_token',
  'refresh_token',
  'user_id',
  'user_email',
  'fxtrade_wishlist',
  'fxtrade_profile',
  'fxtrade_prefs_local',
  'fxtrade_notif_local',
]

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
    USER_LS_KEYS.forEach(k => { try { localStorage.removeItem(k) } catch { /* ignore */ } })
  }

  async function login(emailVal, password) {
    const { data } = await authApi.login(emailVal, password)
    _saveSession(data)
  }

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

    // Reset all Pinia stores that hold user-specific data so a new login
    // starts from a clean slate without a full page reload.
    try {
      const { usePortfolioStore } = await import('@/stores/portfolio')
      usePortfolioStore().$reset()
    } catch { /* ignore */ }

    try {
      const { useLlmStore } = await import('@/stores/llm')
      useLlmStore().clearChat()
    } catch { /* ignore */ }

    try {
      const { usePrefsStore } = await import('@/stores/prefs')
      usePrefsStore().$reset()
    } catch { /* ignore */ }

    // Wipe user-scoped settings keys (keyed by userId in SettingsView)
    const currentUid = userId.value
    if (currentUid) {
      ;[`fxtrade_profile_${currentUid}`, `fxtrade_prefs_local_${currentUid}`, `fxtrade_notif_local_${currentUid}`]
        .forEach(k => { try { localStorage.removeItem(k) } catch { /* ignore */ } })
    }

    _clearSession()
  }

  return { accessToken, userId, email, isLoggedIn, login, signup, logout }
})
