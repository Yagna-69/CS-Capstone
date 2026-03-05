<script setup>
import { ref, computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isLoginPage = computed(() => route.path === '/login')
const searchQuery = ref('')
const searchFocused = ref(false)

// Toggle to show/hide the ticker jumbotron
const showTicker = ref(true)

// Track user authentication status
const isSignedIn = ref(false)

// Base list of currencies - can be updated dynamically
const baseCurrencies = ref([
  { pair: 'EUR/USD', price: '1.0823', trend: 'up' },
  { pair: 'GBP/USD', price: '1.2645', trend: 'down' },
  { pair: 'USD/JPY', price: '150.12', trend: 'up' },
  { pair: 'AUD/USD', price: '0.6543', trend: 'up' },
  { pair: 'USD/CAD', price: '1.3456', trend: 'down' },
  { pair: 'USD/CHF', price: '0.8876', trend: 'up' },
  { pair: 'NZD/USD', price: '0.6123', trend: 'down' },
  { pair: 'EUR/GBP', price: '0.8554', trend: 'up' },
  { pair: 'EUR/JPY', price: '162.45', trend: 'up' },
  { pair: 'GBP/JPY', price: '189.76', trend: 'down' }
])

// Duplicated for infinite scroll
const tickerItems = computed(() => {
  return [...baseCurrencies.value, ...baseCurrencies.value, ...baseCurrencies.value]
})

// Function to update ticker data - can be called from API/WebSocket later
const updateTickerData = (newData) => {
  baseCurrencies.value = newData
}

// Handle Trade button click
const handleTradeClick = () => {
  if (isSignedIn.value) {
    router.push('/')
  } else {
    router.push('/login')
  }
}

// Expose updateTickerData for future use
defineExpose({ updateTickerData })
</script>

<template>
  <div v-if="!isLoginPage" id="app" class="min-h-screen bg-bg-primary flex flex-col">
    <header class="bg-bg-secondary border-b border-border sticky top-0 z-50 backdrop-blur-sm bg-opacity-90">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16 gap-6">
          
          <!-- Left: Logo + Search Bar -->
          <div class="flex items-center gap-6 flex-shrink-0">
            <RouterLink to="/" class="text-3xl font-bold font-goldman text-primary hover:opacity-80 transition">FXTrade</RouterLink>
            
            <div class="relative hidden sm:block">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search currencies"
                @focus="searchFocused = true"
                @blur="searchFocused = false"
                class="search-input w-48 focus:w-64 px-4 py-2 pl-10 bg-bg-primary border border-gray-700 rounded-full text-white placeholder-gray-500 focus:outline-none focus:border-primary transition-all duration-300 text-sm"
              />
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 transition-colors" :class="{ 'text-primary': searchFocused }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
          </div>

          <!-- Center: Currency Ticker with 3D Curved Perspective -->
          <div v-if="showTicker" class="flex-1 overflow-hidden mx-4 perspective-container">
            <div class="ticker-scroll-container">
              <div class="ticker-scroll">
                <span 
                  v-for="(item, index) in tickerItems" 
                  :key="index"
                  class="ticker-item"
                >
                  <span class="font-bold text-gray-400">{{ item.pair }}</span>
                  <span class="text-primary">{{ item.price }}</span>
                  <span :class="item.trend === 'up' ? 'text-green-500' : 'text-red-500'">
                    {{ item.trend === 'up' ? '▲' : '▼' }}
                  </span>
                </span>
              </div>
            </div>
          </div>

          <!-- Right: Nav Links + Trade -->
          <div class="flex items-center gap-4 flex-shrink-0">
            <div class="hidden md:flex gap-2">
              <RouterLink to="/" class="nav-link">Dashboard</RouterLink>
              <RouterLink to="/news" class="nav-link">News</RouterLink>
              <RouterLink to="/ai" class="nav-link">Insight</RouterLink>
            </div>
            
            <button @click="handleTradeClick" class="px-6 py-2 bg-primary text-black rounded-full font-bold hover:bg-primary-dark transition-all text-sm">
              Trade
            </button>
          </div>

        </div>
      </nav>
    </header>
    
    <main class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full">
      <RouterView />
    </main>
  </div>
  
  <RouterView v-else />
</template>

<style scoped>
.nav-link {
  @apply text-gray-400 hover:text-white px-4 py-2 rounded-full text-sm font-semibold transition-all;
}

.nav-link.router-link-active {
  @apply text-white bg-bg-card;
}

.search-input {
  transition: all 0.3s ease;
}

.search-input:focus {
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1);
}

/* 3D Perspective Container */
.perspective-container {
  perspective: 1000px;
  perspective-origin: center;
  display: flex;
  align-items: center;
  height: 100%;
}

/* Ticker Scroll Container with Curve Effect */
.ticker-scroll-container {
  position: relative;
  width: 100%;
  height: 40px;
  overflow: hidden;
  display: flex;
  align-items: center;
  mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 10%,
    black 90%,
    transparent 100%
  );
  -webkit-mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 10%,
    black 90%,
    transparent 100%
  );
}

/* Scrolling Ticker with 3D Transform */
.ticker-scroll {
  display: flex;
  gap: 2rem;
  animation: scroll-curve 40s linear infinite;
  transform-style: preserve-3d;
  will-change: transform;
}

/* Individual Ticker Items */
.ticker-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  font-family: monospace;
  font-size: 0.875rem;
  flex-shrink: 0;
  transform-style: preserve-3d;
  animation: curve-perspective 40s linear infinite;
}

/* 3D Curve Animation */
@keyframes scroll-curve {
  0% {
    transform: translateX(0) translateZ(0) rotateY(0deg);
  }
  100% {
    transform: translateX(-33.33%) translateZ(0) rotateY(0deg);
  }
}

@keyframes curve-perspective {
  0%, 100% {
    transform: translateZ(15px) rotateY(-12deg) scale(0.95);
  }
  50% {
    transform: translateZ(0px) rotateY(0deg) scale(1);
  }
}

/* Pause on hover */
.ticker-scroll-container:hover .ticker-scroll {
  animation-play-state: paused;
}

.ticker-scroll-container:hover .ticker-item {
  animation-play-state: paused;
}
</style>