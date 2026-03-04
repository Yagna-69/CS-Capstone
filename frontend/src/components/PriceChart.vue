<template>
  <div class="glass glass-hover rounded-2xl p-5 shadow-xl">
    <div class="flex justify-between items-center mb-4">
      <div>
        <h3 class="text-xl font-bold text-white">{{ pair }}</h3>
        <p class="text-sm text-gray-400">{{ description }}</p>
      </div>
      <div class="text-right">
        <div class="text-2xl font-bold" :class="priceChangeClass">
          {{ currentPrice }}
        </div>
        <div class="text-sm" :class="priceChangeClass">
          {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(4) }} ({{ priceChangePercent }}%)
        </div>
      </div>
    </div>
    <div ref="chartContainer" class="w-full h-64"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { createChart } from 'lightweight-charts'

const props = defineProps({
  pair: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: 'Currency Pair'
  }
})

const chartContainer = ref(null)
const currentPrice = ref(1.0856)
const priceChange = ref(0.0024)
const priceChangePercent = ref(0.22)

let chart = null
let lineSeries = null
let interval = null

const priceChangeClass = computed(() => {
  return priceChange.value >= 0 ? 'text-forex-green' : 'text-forex-red'
})

onMounted(() => {
  chart = createChart(chartContainer.value, {
    layout: {
      background: { color: '#1a1d23' },
      textColor: '#d1d4dc',
    },
    grid: {
      vertLines: { color: '#2d3139' },
      horzLines: { color: '#2d3139' },
    },
    width: chartContainer.value.clientWidth,
    height: 256,
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
  })

  lineSeries = chart.addLineSeries({
    color: '#00c853',
    lineWidth: 2,
  })

  // Generate initial mock data
  const initialData = generateMockData(100)
  lineSeries.setData(initialData)

  // Simulate real-time updates
  interval = setInterval(() => {
    const lastPrice = initialData[initialData.length - 1].value
    const change = (Math.random() - 0.5) * 0.0010
    const newPrice = lastPrice + change
    
    currentPrice.value = newPrice.toFixed(4)
    priceChange.value = newPrice - initialData[0].value
    priceChangePercent.value = ((priceChange.value / initialData[0].value) * 100).toFixed(2)
    
    lineSeries.update({
      time: Math.floor(Date.now() / 1000),
      value: newPrice
    })
    
    initialData.push({
      time: Math.floor(Date.now() / 1000),
      value: newPrice
    })
    
    if (initialData.length > 100) {
      initialData.shift()
    }
  }, 2000)

  // Handle window resize
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
  if (chart) chart.remove()
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  if (chart && chartContainer.value) {
    chart.applyOptions({
      width: chartContainer.value.clientWidth
    })
  }
}

function generateMockData(count) {
  const data = []
  let basePrice = 1.0832
  const now = Math.floor(Date.now() / 1000)
  
  for (let i = 0; i < count; i++) {
    const change = (Math.random() - 0.5) * 0.0010
    basePrice += change
    data.push({
      time: now - (count - i) * 120, // 2 min intervals
      value: basePrice
    })
  }
  
  return data
}
</script>
