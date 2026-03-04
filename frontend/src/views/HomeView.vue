<template>
  <div class="space-y-6">
    <!-- Portfolio Overview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <PortfolioCard
        label="Portfolio Value"
        value="$10,234.56"
        :change="234.56"
        :changePercent="2.35"
        period="Today"
        icon="💰"
      />
      <PortfolioCard
        label="Day's Profit/Loss"
        value="$+156.23"
        :change="156.23"
        :changePercent="1.55"
        period="Today"
        icon="📈"
      />
      <PortfolioCard
        label="Buying Power"
        value="$5,432.10"
        icon="⚡"
      />
    </div>

    <!-- Main Chart -->
    <PriceChart
      pair="EUR/USD"
      description="Euro vs US Dollar"
    />

    <!-- Watchlist -->
    <div>
      <h2 class="text-2xl font-bold text-white mb-4">Watchlist</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <CurrencyCard
          pair="GBP/USD"
          description="British Pound vs US Dollar"
          price="1.2643"
          :change="0.0012"
          :changePercent="0.095"
        />
        <CurrencyCard
          pair="USD/JPY"
          description="US Dollar vs Japanese Yen"
          price="149.82"
          :change="-0.23"
          :changePercent="-0.15"
        />
        <CurrencyCard
          pair="AUD/USD"
          description="Australian Dollar vs US Dollar"
          price="0.6523"
          :change="0.0008"
          :changePercent="0.12"
        />
        <CurrencyCard
          pair="USD/CAD"
          description="US Dollar vs Canadian Dollar"
          price="1.3542"
          :change="-0.0015"
          :changePercent="-0.11"
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
import { ref } from 'vue'
import PriceChart from '@/components/PriceChart.vue'
import CurrencyCard from '@/components/CurrencyCard.vue'
import PortfolioCard from '@/components/PortfolioCard.vue'
import { api } from '@/services/api'

const checking = ref(false)
const healthStatus = ref(null)

async function checkHealth() {
  checking.value = true
  healthStatus.value = null
  try {
    const response = await api.healthCheck()
    healthStatus.value = {
      status: 'success',
      message: `Backend is ${response.status}!`
    }
  } catch (error) {
    healthStatus.value = {
      status: 'error',
      message: 'Backend is not responding. Make sure it\'s running on port 8000.'
    }
  } finally {
    checking.value = false
  }
}
</script>
