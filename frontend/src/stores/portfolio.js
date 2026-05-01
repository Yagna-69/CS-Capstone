import { defineStore } from 'pinia'
import { ref } from 'vue'
import { portfolioApi } from '@/services/api'

export const usePortfolioStore = defineStore('portfolio', () => {
  const holdings = ref([])   // [{ 'currency-ticker-symbol', amount }, ...]
  const loading  = ref(false)
  const error    = ref(null)
  let previousHoldingsHash = null

  // History state
  const historyData    = ref(null)   // { period, interval, data_points, currency, total_deposited, net_gain_loss }
  const historyLoading = ref(false)
  const historyError   = ref(null)
  const selectedPeriod = ref('1mo')
  
  // First transaction date (for limiting chart periods)
  const firstTransactionDate = ref(null)

  // Wishlist state (client-side localStorage)
  const wishlist = ref([])  // [{ pair: 'USD/EUR', addedAt: timestamp }, ...]
  const WISHLIST_STORAGE_KEY = 'fxtrade_wishlist'

  function loadWishlistFromStorage() {
    try {
      const stored = localStorage.getItem(WISHLIST_STORAGE_KEY)
      if (stored) {
        wishlist.value = JSON.parse(stored)
      }
    } catch (e) {
      console.error('Failed to load wishlist from localStorage:', e)
    }
  }

  function saveWishlistToStorage() {
    try {
      localStorage.setItem(WISHLIST_STORAGE_KEY, JSON.stringify(wishlist.value))
    } catch (e) {
      console.error('Failed to save wishlist to localStorage:', e)
    }
  }

  function getHoldingsHash(holdingsArray) {
    if (!holdingsArray || holdingsArray.length === 0) return 'empty'
    return holdingsArray
      .map(h => `${h['currency-ticker-symbol'] || h.currency}:${h.amount}`)
      .sort()
      .join('|')
  }

  async function fetchHoldings() {
    const isInitialLoad = holdings.value.length === 0
    if (isInitialLoad) {
      loading.value = true
    }
    error.value   = null
    try {
      const { data } = await portfolioApi.getHoldings()
      holdings.value = data
      
      // Check if holdings actually changed
      const newHash = getHoldingsHash(data)
      const holdingsChanged = newHash !== previousHoldingsHash
      previousHoldingsHash = newHash
      
      return { holdingsChanged }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to load portfolio.'
      return { holdingsChanged: false }
    } finally {
      if (isInitialLoad) {
        loading.value = false
      }
    }
  }

  async function fetchHistory(period = '1mo', forceRefresh = false) {
    const isInitialLoad = historyData.value === null
    if (isInitialLoad || forceRefresh) {
      historyLoading.value = true
    }
    historyError.value   = null
    selectedPeriod.value = period
    try {
      const { data } = await portfolioApi.getHistory(period)
      historyData.value = data
    } catch (e) {
      historyError.value = e.response?.data?.detail || 'Failed to load history.'
    } finally {
      if (isInitialLoad || forceRefresh) {
        historyLoading.value = false
      }
    }
  }

  async function fetchFirstTransactionDate() {
    try {
      const { data } = await portfolioApi.getFirstTransaction()
      firstTransactionDate.value = data.first_transaction_date
    } catch (e) {
      console.error('Failed to fetch first transaction date:', e)
    }
  }

  /**
   * Immediately apply a known trade result to holdings in memory so the UI
   * reflects the new balances without waiting for the next API poll.
   * The background fetchHoldings() call will reconcile with the server truth.
   */
  function applyTradeOptimistic({ fromCurrency, toCurrency, sentAmount, receivedAmount }) {
    const adjust = (ticker, delta) => {
      const holding = holdings.value.find(
        h => (h['currency-ticker-symbol'] || h.currency) === ticker
      )
      if (holding) {
        holding.amount = Math.max(0, Number(holding.amount) + delta)
      } else if (delta > 0) {
        holdings.value.push({ 'currency-ticker-symbol': ticker, currency: ticker, amount: delta })
      }
    }
    adjust(fromCurrency, -sentAmount)
    adjust(toCurrency,   +receivedAmount)
    // Update hash so the next fetchHoldings diff check still works
    previousHoldingsHash = getHoldingsHash(holdings.value)
  }

  async function deposit(currency, amount) {
    await portfolioApi.deposit(currency, amount)
    await fetchHoldings()
  }

  async function withdraw(currency, amount) {
    await portfolioApi.withdraw(currency, amount)
    await fetchHoldings()
  }

  // Wishlist methods (client-side localStorage)
  function isInWishlist(pair) {
    return wishlist.value.some(item => item.pair === pair)
  }

  function addToWishlist(pair) {
    if (!isInWishlist(pair)) {
      wishlist.value.push({
        pair,
        addedAt: Date.now()
      })
      saveWishlistToStorage()
    }
  }

  function removeFromWishlist(pair) {
    const index = wishlist.value.findIndex(item => item.pair === pair)
    if (index > -1) {
      wishlist.value.splice(index, 1)
      saveWishlistToStorage()
    }
  }

  function toggleWishlist(pair) {
    if (isInWishlist(pair)) {
      removeFromWishlist(pair)
    } else {
      addToWishlist(pair)
    }
  }

  // Load wishlist from localStorage on store initialization
  loadWishlistFromStorage()

  function $reset() {
    holdings.value             = []
    loading.value              = false
    error.value                = null
    previousHoldingsHash       = null
    historyData.value          = null
    historyLoading.value       = false
    historyError.value         = null
    selectedPeriod.value       = '1mo'
    firstTransactionDate.value = null
    wishlist.value             = []
    try { localStorage.removeItem(WISHLIST_STORAGE_KEY) } catch { /* ignore */ }
  }

  return {
    holdings, loading, error,
    historyData, historyLoading, historyError, selectedPeriod,
    firstTransactionDate,
    fetchHoldings, fetchHistory, fetchFirstTransactionDate, applyTradeOptimistic, deposit, withdraw,
    wishlist, isInWishlist, addToWishlist, removeFromWishlist, toggleWishlist,
    $reset,
  }
})
