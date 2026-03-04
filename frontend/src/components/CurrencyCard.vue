<template>
  <div class="glass glass-hover rounded-2xl p-4 cursor-pointer">
    <div class="flex justify-between items-start">
      <div>
        <h4 class="text-lg font-bold text-white">{{ pair }}</h4>
        <p class="text-sm text-gray-400">{{ description }}</p>
      </div>
      <div class="text-right">
        <div class="text-xl font-bold text-white">{{ price }}</div>
        <div class="flex items-center gap-1 text-sm" :class="changeClass">
          <span>{{ change >= 0 ? '↑' : '↓' }}</span>
          <span>{{ Math.abs(changePercent) }}%</span>
        </div>
      </div>
    </div>
    
    <div class="mt-3 h-12">
      <svg class="w-full h-full" viewBox="0 0 100 30" preserveAspectRatio="none">
        <polyline
          :points="sparklinePoints"
          fill="none"
          :stroke="change >= 0 ? '#FFD700' : '#ff4444'"
          stroke-width="2"
        />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  pair: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  price: {
    type: String,
    required: true
  },
  change: {
    type: Number,
    required: true
  },
  changePercent: {
    type: Number,
    required: true
  },
  sparklineData: {
    type: Array,
    default: () => []
  }
})

const changeClass = computed(() => {
  return props.change >= 0 ? 'text-forex-green' : 'text-forex-red'
})

const sparklinePoints = computed(() => {
  if (props.sparklineData.length === 0) {
    // Generate mock sparkline
    const points = []
    for (let i = 0; i < 20; i++) {
      const x = (i / 19) * 100
      const y = 15 + Math.sin(i * 0.5) * 10 + (Math.random() - 0.5) * 5
      points.push(`${x},${y}`)
    }
    return points.join(' ')
  }
  
  const max = Math.max(...props.sparklineData)
  const min = Math.min(...props.sparklineData)
  const range = max - min
  
  return props.sparklineData
    .map((value, i) => {
      const x = (i / (props.sparklineData.length - 1)) * 100
      const y = 30 - ((value - min) / range) * 30
      return `${x},${y}`
    })
    .join(' ')
})
</script>
