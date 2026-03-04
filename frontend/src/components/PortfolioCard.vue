<template>
  <div class="glass glass-hover rounded-2xl p-5 shadow-xl">
    <div class="flex justify-between items-start mb-4">
      <div>
        <p class="text-sm text-gray-400">{{ label }}</p>
        <h3 class="text-3xl font-bold text-white mt-1">{{ value }}</h3>
      </div>
      <div v-if="icon" class="text-3xl">{{ icon }}</div>
    </div>
    
    <div v-if="change !== undefined" class="flex items-center gap-2">
      <span class="text-sm" :class="changeClass">
        {{ change >= 0 ? '+' : '' }}{{ change }} ({{ changePercent >= 0 ? '+' : '' }}{{ changePercent }}%)
      </span>
      <span class="text-xs text-gray-500">{{ period }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: String,
    required: true
  },
  change: {
    type: Number,
    default: undefined
  },
  changePercent: {
    type: Number,
    default: undefined
  },
  period: {
    type: String,
    default: 'Today'
  },
  icon: {
    type: String,
    default: ''
  }
})

const changeClass = computed(() => {
  if (props.change === undefined) return ''
  return props.change >= 0 ? 'text-forex-green' : 'text-forex-red'
})
</script>
