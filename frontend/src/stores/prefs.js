import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * Lightweight store for user preferences that affect multiple views.
 * The dashboard reads `displayCurrency` to label and convert portfolio totals.
 * SettingsView writes here after saving so the dashboard reacts immediately
 * without a page reload.
 */
export const usePrefsStore = defineStore('prefs', () => {
  // Resolved once the auth store has a userId
  const displayCurrency = ref('USD')

  /** Call this on app boot / login to seed from the user-scoped localStorage key. */
  function load(userId) {
    try {
      const key = `fxtrade_prefs_local_${userId || 'anon'}`
      const stored = JSON.parse(localStorage.getItem(key) || '{}')
      if (stored.defaultCurrency) displayCurrency.value = stored.defaultCurrency
    } catch { /* ignore */ }
  }

  /** Call this after the user saves preferences in SettingsView. */
  function set(currency) {
    if (currency) displayCurrency.value = currency
  }

  function $reset() {
    displayCurrency.value = 'USD'
  }

  return { displayCurrency, load, set, $reset }
})
