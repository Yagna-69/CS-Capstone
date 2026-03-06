import { defineStore } from 'pinia'
import { ref } from 'vue'
import { portfolioApi } from '@/services/api'

export const usePortfolioStore = defineStore('portfolio', () => {
  const holdings = ref([])   // [{ 'currency-ticker-symbol', amount }, ...]
  const loading  = ref(false)
  const error    = ref(null)

  async function fetchHoldings() {
    loading.value = true
    error.value   = null
    try {
      const { data } = await portfolioApi.getHoldings()
      holdings.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to load portfolio.'
    } finally {
      loading.value = false
    }
  }

  async function deposit(currency, amount) {
    await portfolioApi.deposit(currency, amount)
    await fetchHoldings()
  }

  async function withdraw(currency, amount) {
    await portfolioApi.withdraw(currency, amount)
    await fetchHoldings()
  }

  return { holdings, loading, error, fetchHoldings, deposit, withdraw }
})
