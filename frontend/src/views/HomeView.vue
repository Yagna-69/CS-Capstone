<template>
  <div class="space-y-6">
    <div v-if="!isAuthed" class="bg-forex-card rounded-lg p-6 border border-forex-border">
      <p class="text-gray-300 text-sm">
        <RouterLink to="/login" class="text-primary font-semibold hover:underline">Sign in</RouterLink>
        to see portfolio values from your account. Below is live market data from the API.
      </p>
    </div>

    <!-- Portfolio Overview (authenticated) -->
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <PortfolioCard
        label="Portfolio Value (USD)"
        :value="portfolioValueDisplay"
        :change="dayChangeUsd"
        :changePercent="dayChangePct"
        period="Today (local)"
        icon="💰"
      />
      <PortfolioCard
        label="Day change"
        :value="dayChangePctDisplay"
        period="vs start of local day"
        icon="📈"
      />
      <PortfolioCard
        label="USD balance"
        :value="usdBalanceDisplay"
        icon="⚡"
      />
    </div>

    <!-- Main Chart -->
    <PriceChart pair="EUR/USD" description="Euro vs US Dollar" history-period="3mo" />

    <!-- Watchlist -->
    <div>
      <h2 class="text-2xl font-bold text-white mb-4">Watchlist</h2>
      <p v-if="watchlistError" class="text-red-400 text-sm mb-3">{{ watchlistError }}</p>
      <div v-if="watchlistLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="n in 4" :key="n" class="h-32 bg-forex-card rounded-2xl animate-pulse border border-forex-border" />
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <CurrencyCard
          v-for="row in watchlistRows"
          :key="row.pair"
          :pair="row.pair"
          :description="row.description"
          :price="row.priceStr"
          :change="row.changeAbs"
          :changePercent="row.changePercent"
          :sparkline-data="row.sparkline"
        />
      </div>
    </div>

    <!-- Backend Connection Status -->
    <div class="bg-forex-card rounded-lg p-6 border border-forex-border">
      <h2 class="text-xl font-bold text-white mb-4">System Status</h2>
      <div class="flex items-center gap-4">
        <button
          @click="checkHealth"
          :disabled="checking"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
        >
          {{ checking ? 'Checking...' : 'Check Backend' }}
        </button>

        <div v-if="healthStatus" class="flex items-center gap-2">
          <span
            class="w-3 h-3 rounded-full"
            :class="healthStatus.status === 'success' ? 'bg-forex-green' : 'bg-forex-red'"
          ></span>
          <span :class="healthStatus.status === 'success' ? 'text-forex-green' : 'text-forex-red'">
            {{ healthStatus.message }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import PriceChart from '@/components/PriceChart.vue'
import CurrencyCard from '@/components/CurrencyCard.vue'
import PortfolioCard from '@/components/PortfolioCard.vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useForexStore } from '@/stores/forex'
import { buildPortfolioSeriesUsd } from '@/utils/portfolioSeries'
import axios from 'axios'

const WATCH_PAIRS = [
  { pair: 'GBP/USD', description: 'British Pound / US Dollar' },
  { pair: 'USD/JPY', description: 'US Dollar / Japanese Yen' },
  { pair: 'AUD/USD', description: 'Australian Dollar / US Dollar' },
  { pair: 'USD/CAD', description: 'US Dollar / Canadian Dollar' }
]

const WATCHLIST_REFRESH_INTERVAL_MS = 4_000  // Reload watchlist prices every 4s (configurable)

const portfolioStore = usePortfolioStore()
const forexStore = useForexStore()
const checking = ref(false)
const healthStatus = ref(null)
const watchlistLoading = ref(true)
const watchlistError = ref('')
const watchlistRows = ref([])
let watchlistRefreshTimer = null

const isAuthed = computed(() => !!localStorage.getItem('access_token'))

const homeHeadline = computed(() => {
  const s = buildPortfolioSeriesUsd(portfolioStore.historyData, '1d')
  if (s.type === 'empty') {
    return { last: 0, first: 0, changePct: 0, changeUsd: 0 }
  }
  const first = s.type === 'xy' ? s.data[0]?.y : s.data[0]
  const last = s.type === 'xy' ? s.data[s.data.length - 1]?.y : s.data[s.data.length - 1]
  if (first == null || last == null) {
    return { last: 0, first: 0, changePct: 0, changeUsd: 0 }
  }
  return {
    last,
    first,
    changePct: first !== 0 ? ((last - first) / first) * 100 : 0,
    changeUsd: last - first
  }
})

const portfolioValueDisplay = computed(() => {
  const v = homeHeadline.value.last
  if (!v) return '—'
  return '$' + v.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

const dayChangeUsd = computed(() => homeHeadline.value.changeUsd)
const dayChangePct = computed(() => homeHeadline.value.changePct)

const dayChangePctDisplay = computed(() => {
  const p = homeHeadline.value.changePct
  return (p >= 0 ? '+' : '') + p.toFixed(2) + '%'
})

const usdBalanceDisplay = computed(() => {
  const h = portfolioStore.holdings.find(
    (x) => (x['currency-ticker-symbol'] || x.currency) === 'USD'
  )
  if (!h) return '$0.00'
  const n = Number(h.amount)
  return '$' + n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

async function loadWatchlist() {
  const isInitialLoad = watchlistRows.value.length === 0
  if (isInitialLoad) {
    watchlistLoading.value = true
  }
  watchlistError.value = ''
  try {
    const rows = await Promise.all(
      WATCH_PAIRS.map(async ({ pair, description }) => {
        const [from, to] = pair.split('/')
        const { data } = await forexApi.getPairHistory(from, to, '1wk')
        const candles = data.candles || []
        if (candles.length === 0) {
          return {
            pair,
            description,
            priceStr: '—',
            changeAbs: 0,
            changePercent: 0,
            sparkline: []
          }
        }
        const first = candles[0].close
        const last = candles[candles.length - 1].close
        const sparkline = candles.map((c) => c.close)
        return {
          pair,
          description,
          priceStr: last.toFixed(pair.includes('JPY') ? 2 : 4),
          changeAbs: last - first,
          changePercent: first ? ((last - first) / first) * 100 : 0,
          sparkline
        }
      })
    )
    watchlistRows.value = rows
  } catch (e) {
    watchlistError.value = e.response?.data?.detail || 'Could not load watchlist.'
    if (isInitialLoad) {
      watchlistRows.value = []
    }
  } finally {
    if (isInitialLoad) {
      watchlistLoading.value = false
    }
  }
}

async function checkHealth() {
  checking.value = true
  healthStatus.value = null
  try {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await axios.get(base.replace(/\/$/, '') + '/health')
    healthStatus.value = {
      status: 'success',
      message: `Backend is ${response.data.status}!`
    }
  } catch {
    healthStatus.value = {
      status: 'error',
      message: 'Backend is not responding. Check VITE_API_URL and that the server is running.'
    }
  } finally {
    checking.value = false
  }
}

onMounted(async () => {
  loadWatchlist()
  if (isAuthed.value) {
    await portfolioStore.fetchHoldings()
    await portfolioStore.fetchHistory('1d')
  }
  watchlistRefreshTimer = setInterval(() => loadWatchlist(), WATCHLIST_REFRESH_INTERVAL_MS)
})

onUnmounted(() => {
  if (watchlistRefreshTimer) clearInterval(watchlistRefreshTimer)
})
</script>
