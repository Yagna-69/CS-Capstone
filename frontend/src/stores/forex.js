import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { forexApi } from '@/services/api'

/**
 * Centralized forex data pipeline store.
 * Components subscribe to specific pairs via subscribePair/unsubscribePair.
 * The poller only fetches the pairs that have active subscribers, so the
 * request payload stays small regardless of how many currencies exist.
 */
export const useForexStore = defineStore('forex', () => {
  const REFRESH_INTERVAL_MS = 4_000

  const currencies  = ref([])
  const rates       = ref({})
  const pairHistory = ref({})
  const lastUpdate  = ref(null)
  const error       = ref(null)

  // { 'EURUSD': subscriptionCount }
  const _subscriptions = ref({})

  let refreshTimer = null

  // Pairs that have at least one subscriber
  const activePairs = computed(() =>
    Object.keys(_subscriptions.value).filter(k => _subscriptions.value[k] > 0)
  )

  function subscribePair(from, to) {
    const key = `${from.toUpperCase()}${to.toUpperCase()}`
    _subscriptions.value[key] = (_subscriptions.value[key] || 0) + 1
  }

  function unsubscribePair(from, to) {
    const key = `${from.toUpperCase()}${to.toUpperCase()}`
    if (_subscriptions.value[key] > 0) _subscriptions.value[key]--
  }

  async function loadCurrencies() {
    try {
      const { data } = await forexApi.getCurrencies()
      currencies.value = data.currencies || []
    } catch (e) {
      console.error('Failed to load currencies:', e)
    }
  }

  async function fetchRates() {
    const pairs = activePairs.value
    if (pairs.length === 0) return

    try {
      const { data } = await forexApi.getRates(pairs.join(','))
      // Merge so previously fetched pairs aren't wiped
      rates.value = { ...rates.value, ...(data.rates || {}) }
      lastUpdate.value = Date.now()
      error.value = null
    } catch (e) {
      console.error('Failed to fetch rates:', e)
      error.value = 'Could not fetch live rates.'
    }
  }

  async function fetchPairHistory(from, to, period = '1d') {
    const key = `${from}/${to}:${period}`
    try {
      const { data } = await forexApi.getPairHistory(from, to, period)
      pairHistory.value[key] = { candles: data.candles || [], timestamp: Date.now() }
      return pairHistory.value[key]
    } catch (e) {
      console.error(`Failed to fetch history for ${key}:`, e)
      return pairHistory.value[key] || { candles: [], timestamp: 0 }
    }
  }

  function getCachedPairHistory(from, to, period = '1d') {
    return pairHistory.value[`${from}/${to}:${period}`] || null
  }

  function getRate(from, to) {
    if (!from || !to) return null
    return rates.value[`${from.toUpperCase()}${to.toUpperCase()}`] || null
  }

  function startPipeline() {
    if (refreshTimer) return
    loadCurrencies()
    fetchRates()
    refreshTimer = setInterval(fetchRates, REFRESH_INTERVAL_MS)
  }

  function stopPipeline() {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  return {
    currencies,
    rates,
    pairHistory,
    lastUpdate,
    error,
    activePairs,
    subscribePair,
    unsubscribePair,
    loadCurrencies,
    fetchRates,
    fetchPairHistory,
    getCachedPairHistory,
    getRate,
    startPipeline,
    stopPipeline,
    REFRESH_INTERVAL_MS,
  }
})
