<template>
  <div class="glass glass-hover rounded-2xl p-5 shadow-xl">
    <div class="flex justify-between items-center mb-4">
      <div>
        <h3 class="text-xl font-bold text-white">{{ pair }}</h3>
        <p class="text-sm text-gray-400">{{ description }}</p>
      </div>
      <div class="text-right">
        <div v-if="loading" class="text-sm text-gray-500">Loading…</div>
        <template v-else>
          <div class="text-2xl font-bold" :class="priceChangeClass">
            {{ displayPrice }}
          </div>
          <div class="text-sm" :class="priceChangeClass">
            {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(4) }} ({{ Number(priceChangePercent).toFixed(2) }}%)
          </div>
        </template>
      </div>
    </div>
    <p v-if="error" class="text-red-400 text-sm mb-2">{{ error }}</p>
    <div ref="chartContainer" class="w-full h-64"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { createChart } from 'lightweight-charts'
import { useForexStore } from '@/stores/forex'

const props = defineProps({
  pair: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: 'Currency Pair'
  },
  historyPeriod: {
    type: String,
    default: '3mo'
  }
})

const forexStore = useForexStore()
const chartContainer = ref(null)
const loading = ref(true)
const error = ref('')
const currentPrice = ref(0)
const priceChange = ref(0)
const priceChangePercent = ref(0)

let chart = null
let lineSeries = null

const displayPrice = computed(() =>
  currentPrice.value ? currentPrice.value.toFixed(4) : '—'
)

const priceChangeClass = computed(() => {
  return priceChange.value >= 0 ? 'text-forex-green' : 'text-forex-red'
})

function parsePair(pairStr) {
  const parts = pairStr.split('/')
  if (parts.length !== 2) return null
  return { from: parts[0].trim(), to: parts[1].trim() }
}

async function loadSeries() {
  if (!lineSeries) return
  loading.value = true
  error.value = ''
  try {
    const p = parsePair(props.pair)
    if (!p) {
      error.value = 'Invalid pair.'
      return
    }
    const result = await forexStore.fetchPairHistory(p.from, p.to, props.historyPeriod)
    const candles = result.candles || []
    if (candles.length === 0) {
      lineSeries.setData([])
      error.value = 'No historical data for this pair.'
      currentPrice.value = 0
      priceChange.value = 0
      priceChangePercent.value = 0
      return
    }
    const lineData = candles.map((c) => ({ time: c.time, value: c.close }))
    lineSeries.setData(lineData)
    const first = candles[0].close
    const last = candles[candles.length - 1].close
    currentPrice.value = last
    priceChange.value = last - first
    priceChangePercent.value = first ? ((last - first) / first) * 100 : 0
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load chart.'
    lineSeries.setData([])
    currentPrice.value = 0
    priceChange.value = 0
    priceChangePercent.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  chart = createChart(chartContainer.value, {
    layout: {
      background: { color: '#1a1d23' },
      textColor: '#d1d4dc'
    },
    grid: {
      vertLines: { color: '#2d3139' },
      horzLines: { color: '#2d3139' }
    },
    width: chartContainer.value.clientWidth,
    height: 256,
    timeScale: {
      timeVisible: true,
      secondsVisible: false
    }
  })

  lineSeries = chart.addLineSeries({
    color: '#00c853',
    lineWidth: 2
  })

  loadSeries()
  window.addEventListener('resize', handleResize)
})

watch(
  () => [props.pair, props.historyPeriod],
  () => loadSeries()
)

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.remove()
    chart = null
    lineSeries = null
  }
})

function handleResize() {
  if (chart && chartContainer.value) {
    chart.applyOptions({
      width: chartContainer.value.clientWidth
    })
  }
}
</script>
