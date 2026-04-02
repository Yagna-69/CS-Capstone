import { defineStore } from 'pinia'
import { ref } from 'vue'
import { forexApi } from '@/services/api'

/**
 * Centralized forex data pipeline store.
 * All components should subscribe to this store instead of fetching directly.
 * The store polls the API at a configurable interval and broadcasts updates.
 */
export const useForexStore = defineStore('forex', () => {
  // Configuration
  const REFRESH_INTERVAL_MS = 5_000  // Poll interval (configurable)
  
  // State
  const currencies = ref([])          // [{ code, name }, ...]
  const rates = ref({})               // { 'EURUSD': 1.0850, ... }
  const pairHistory = ref({})         // { 'EUR/USD:1d': { candles: [...], timestamp } }
  const lastUpdate = ref(null)        // Timestamp of last successful update
  const error = ref(null)
  
  let refreshTimer = null
  
  // Load currencies (one-time on init)
  async function loadCurrencies() {
    try {
      const { data } = await forexApi.getCurrencies()
      currencies.value = data.currencies || []
    } catch (e) {
      console.error('Failed to load currencies:', e)
      currencies.value = []
    }
  }
  
  // Poll live rates for all pairs
  async function fetchRates() {
    try {
      const { data } = await forexApi.getRates()
      rates.value = data.rates || {}
      lastUpdate.value = Date.now()
      error.value = null
    } catch (e) {
      console.error('Failed to fetch rates:', e)
      error.value = 'Could not fetch live rates.'
      // Keep previous rates on error
    }
  }
  
  // Fetch OHLC history for a specific pair/period
  // Results are cached with timestamp; consumers can decide if stale
  async function fetchPairHistory(from, to, period = '1d') {
    const key = `${from}/${to}:${period}`
    try {
      const { data } = await forexApi.getPairHistory(from, to, period)
      pairHistory.value[key] = {
        candles: data.candles || [],
        timestamp: Date.now()
      }
      return pairHistory.value[key]
    } catch (e) {
      console.error(`Failed to fetch history for ${key}:`, e)
      // Return cached data if available, otherwise empty
      return pairHistory.value[key] || { candles: [], timestamp: 0 }
    }
  }
  
  // Get cached pair history without fetching
  function getCachedPairHistory(from, to, period = '1d') {
    const key = `${from}/${to}:${period}`
    return pairHistory.value[key] || null
  }
  
  // Get rate for a specific pair (from rates cache)
  function getRate(from, to) {
    const key = `${from}${to}`
    return rates.value[key] || null
  }
  
  // Start the polling pipeline
  function startPipeline() {
    if (refreshTimer) return // Already running
    
    // Initial fetch
    loadCurrencies()
    fetchRates()
    
    // Poll rates at interval
    refreshTimer = setInterval(fetchRates, REFRESH_INTERVAL_MS)
  }
  
  // Stop the polling pipeline
  function stopPipeline() {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }
  
  return {
    // State
    currencies,
    rates,
    pairHistory,
    lastUpdate,
    error,
    
    // Actions
    loadCurrencies,
    fetchRates,
    fetchPairHistory,
    getCachedPairHistory,
    getRate,
    startPipeline,
    stopPipeline,
    
    // Config
    REFRESH_INTERVAL_MS
  }
})
