<template>
  <div class="llm-layout">
    <!-- Left Sidebar: Context Widgets (30%) -->
    <div class="left-sidebar flex flex-col overflow-hidden">
      <!-- Top: Portfolio Chart Widget (Collapsible) -->
      <div 
        :class="['portfolio-widget glass-inner rounded-lg m-4 p-4 flex-shrink-0', { expanded: showPortfolioChart }]"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-bold text-white">Portfolio Performance</h3>
          <!-- Toggle Switch -->
          <button
            @click="showPortfolioChart = !showPortfolioChart"
            :class="[
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none',
              showPortfolioChart ? 'bg-primary' : 'bg-gray-700'
            ]"
          >
            <span
              :class="[
                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                showPortfolioChart ? 'translate-x-6' : 'translate-x-1'
              ]"
            />
          </button>
        </div>
        <div v-if="showPortfolioChart" class="h-48 flex items-center justify-center">
          <Line
            v-if="portfolioChartData"
            :data="portfolioChartData"
            :options="portfolioChartOptions"
          />
          <p v-else class="text-gray-500 text-sm">No portfolio data</p>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-t border-gray-700 mx-4"></div>

      <!-- Search Bar for Currency Pair Selection -->
      <div class="px-4 py-3">
        <div class="relative" ref="searchBarRef">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search currency pairs..."
            autocomplete="off"
            @focus="handleSearchFocus"
            @blur="handleSearchBlur"
            class="w-full px-4 py-2 pl-10 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary transition text-sm"
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          
          <!-- Search Dropdown -->
          <div 
            v-if="showSearchDropdown" 
            class="absolute top-full left-0 right-0 mt-2 bg-black border border-gray-800 rounded-lg shadow-2xl overflow-hidden z-50 max-h-64"
          >
            <div class="overflow-y-auto max-h-48">
              <div v-if="searchResults.length > 0" class="py-1">
                <button
                  v-for="item in searchResults"
                  :key="item.pair"
                  @click="selectCurrencyPair(item.pair)"
                  class="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-900 transition text-left"
                >
                  <div class="flex-1">
                    <p class="font-bold text-xs text-white">{{ item.pair }}</p>
                    <p class="text-xs text-gray-500">{{ item.pair.split('/')[0] }} to {{ item.pair.split('/')[1] }}</p>
                  </div>
                  <div class="text-right">
                    <p class="font-mono text-xs text-white">{{ item.price }}</p>
                  </div>
                </button>
              </div>
              <div v-else class="px-4 py-4 text-center text-gray-500 text-xs">
                No pairs found
              </div>
            </div>
            
            <!-- Toggle: Only show tradeable pairs -->
            <div class="border-t border-gray-800 px-3 py-2 bg-bg-secondary">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="showOnlyTradeable"
                  type="checkbox"
                  class="w-4 h-4 rounded bg-bg-primary border-gray-700 text-primary focus:ring-primary focus:ring-offset-0"
                />
                <span class="text-xs text-gray-400">Only show tradeable pairs</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Selected Currency Pair Widgets -->
      <div class="flex-1 overflow-y-auto px-4 pb-4 space-y-2 context-widgets-scroll">
        <div
          v-for="widget in contextWidgets"
          :key="widget.pair"
          @click="selectWidget(widget.pair)"
          :class="[
            'glass-inner rounded-lg p-3 cursor-pointer transition-all border-2',
            selectedWidget === widget.pair
              ? 'border-primary bg-primary/5'
              : 'border-transparent hover:border-gray-700'
          ]"
        >
          <div class="flex items-center justify-between mb-2">
            <p 
              class="font-bold text-sm"
              :class="widget.change >= 0 ? 'text-green-400' : 'text-red-400'"
            >
              {{ widget.pair }}
            </p>
            <button
              @click.stop="removeWidget(widget.pair)"
              class="p-1 hover:bg-red-500/20 rounded transition"
              title="Remove"
            >
              <svg class="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <svg width="120" height="40" class="mini-chart">
                <path
                  v-if="widget.miniPath"
                  :d="widget.miniPath"
                  fill="none"
                  :stroke="widget.change >= 0 ? '#10b981' : '#ef4444'"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <div class="text-right">
              <p class="font-mono text-sm text-white">{{ widget.price }}</p>
              <p class="text-xs font-semibold" :class="widget.change >= 0 ? 'text-green-400' : 'text-red-400'">
                {{ widget.change >= 0 ? '+' : '' }}{{ widget.change.toFixed(2) }}%
              </p>
            </div>
          </div>
        </div>
        
        <div v-if="contextWidgets.length === 0" class="flex items-center justify-center py-8 text-gray-500 text-xs text-center">
          Search and select currency pairs above to add context for the AI
        </div>
      </div>
    </div>

    <!-- Vertical Divider -->
    <div class="divider"></div>

    <!-- Right: Chat Interface (70%) -->
    <div class="chat-section flex flex-col">
      <!-- Chat Header -->
      <div class="flex items-center justify-between p-4 flex-shrink-0">
        <div>
          <h1 class="text-xl font-bold text-white font-goldman">ExLLM Assistant</h1>
          <p class="text-xs text-gray-500">AI-powered forex trading assistant</p>
        </div>
        <div class="flex items-center gap-3">
          <button
            v-if="isAdmin"
            @click="showKeyPanel = !showKeyPanel"
            class="text-xs text-gray-400 hover:text-primary transition"
          >
            {{ showKeyPanel ? 'Hide Keys' : 'Manage Keys' }}
          </button>
          <button
            v-if="store.messages.length"
            @click="store.clearChat"
            class="text-xs text-gray-400 hover:text-primary transition"
          >
            Clear Chat
          </button>
        </div>
      </div>

      <!-- Admin Key Management Panel -->
      <div v-if="showKeyPanel" class="glass-inner m-4 rounded-xl p-4 flex-shrink-0">
        <h3 class="text-sm font-bold text-white mb-3">API Keys</h3>

        <!-- Existing keys -->
        <div v-if="apiKeys.length" class="space-y-2 mb-3">
          <div
            v-for="key in apiKeys"
            :key="key.id"
            class="flex items-center justify-between px-3 py-2 rounded-lg"
            :class="key.is_active ? 'bg-primary/10 border border-primary/30' : 'bg-bg-secondary border border-transparent'"
          >
            <div class="flex items-center gap-2">
              <span class="text-xs font-mono px-2 py-0.5 rounded bg-bg-primary text-gray-400">{{ key.provider }}</span>
              <span class="text-sm text-white">{{ key.label || 'Unnamed' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-if="!key.is_active"
                @click="activateKey(key.id)"
                class="text-xs text-primary hover:text-primary/80 transition"
              >
                Activate
              </button>
              <span v-else class="text-xs text-primary font-bold">Active</span>
              <button
                @click="deleteKey(key.id)"
                class="text-xs text-red-400 hover:text-red-300 transition ml-2"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        <p v-else class="text-gray-500 text-sm mb-3">No API keys configured.</p>

        <!-- Add new key -->
        <div class="flex gap-2">
          <select v-model="newKey.provider" class="px-3 py-2 bg-bg-primary border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary">
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
          </select>
          <input
            v-model="newKey.label"
            placeholder="Label"
            class="px-3 py-2 bg-bg-primary border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary w-28"
          />
          <input
            v-model="newKey.api_key"
            placeholder="API Key"
            type="password"
            class="flex-1 px-3 py-2 bg-bg-primary border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary"
          />
          <button
            @click="addKey"
            :disabled="!newKey.api_key"
            class="px-4 py-2 bg-primary text-black rounded-lg text-sm font-bold hover:bg-primary-dark transition disabled:opacity-50"
          >
            Add
          </button>
        </div>
      </div>

      <!-- Messages Area -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto px-4 py-4 space-y-4 min-h-0 chat-scroll">
        <!-- Empty state -->
        <div v-if="!store.messages.length" class="flex flex-col items-center justify-center h-full">
          <div class="glass-inner rounded-2xl p-8 text-center max-w-md">
            <div class="text-4xl mb-4">💱</div>
            <h2 class="text-xl font-bold text-white mb-2 font-goldman">ExLLM</h2>
            <p class="text-gray-400 text-sm mb-6">Your AI-powered forex trading assistant. Ask about market trends, trading strategies, or currency pairs.</p>
            <div class="flex flex-wrap gap-2 justify-center">
              <button
                v-for="s in suggestions"
                :key="s"
                @click="send(s)"
                class="glass-inner hover:border-primary border border-transparent px-4 py-2 rounded-full text-sm text-gray-300 hover:text-primary transition"
              >
                {{ s }}
              </button>
            </div>
          </div>
        </div>

        <!-- Message bubbles -->
        <transition-group name="message">
          <div
            v-for="(msg, i) in store.messages"
            :key="i"
            :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
          >
            <!-- AI message -->
            <div v-if="msg.role === 'assistant'" class="max-w-[85%]">
              <div class="glass-inner rounded-2xl rounded-tl-md px-4 py-3 text-gray-200 prose prose-invert prose-sm" v-html="renderAssistantMarkdown(msg.content)"></div>
            </div>

            <!-- User bubble (strip context prefix) -->
            <div v-else class="max-w-[85%]">
              <div class="bg-primary text-black rounded-2xl rounded-br-md px-4 py-3 whitespace-pre-wrap">{{ stripContextPrefix(msg.content) }}</div>
            </div>
          </div>
        </transition-group>

        <!-- Typing indicator -->
        <div v-if="store.loading" class="flex justify-start">
          <div class="glass-inner rounded-2xl rounded-tl-md px-4 py-3">
            <div class="typing-indicator flex gap-1">
              <span class="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Error -->
      <p v-if="store.error" class="text-red-400 text-sm mx-4 mb-2 flex-shrink-0">{{ store.error }}</p>

      <!-- Input Bar -->
      <div class="p-4 flex-shrink-0">
        <!-- Active Context Tags -->
        <div v-if="contextWidgets.length > 0" class="mb-3 flex flex-wrap gap-2">
          <span class="text-xs text-gray-400">Context:</span>
          <span
            v-for="widget in contextWidgets"
            :key="widget.pair"
            class="inline-flex items-center gap-1 px-2 py-1 bg-primary/10 border border-primary/30 rounded-full text-xs text-primary"
          >
            {{ widget.pair }}
          </span>
        </div>
        
        <div class="flex gap-3">
          <input
            v-model="input"
            @keyup.enter="send()"
            :disabled="store.loading"
            placeholder="Type a message..."
            class="flex-1 px-5 py-3 bg-bg-primary border border-gray-700 rounded-full text-white placeholder-gray-500 focus:outline-none focus:border-primary transition disabled:opacity-50"
          />
          <button
            @click="send()"
            :disabled="!input.trim() || store.loading"
            class="px-6 py-3 bg-primary text-black rounded-full font-bold hover:bg-primary-dark transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import MarkdownIt from 'markdown-it'
import { useLlmStore } from '@/stores/llm'
import { usePortfolioStore } from '@/stores/portfolio'
import { useForexStore } from '@/stores/forex'
import { preferencesApi, llmApi } from '@/services/api'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

const store = useLlmStore()
const portfolioStore = usePortfolioStore()
const forexStore = useForexStore()
const input = ref('')
const messagesContainer = ref(null)

// Admin state
const isAdmin = ref(false)
const showKeyPanel = ref(false)
const apiKeys = ref([])
const newKey = ref({ provider: 'openai', label: '', api_key: '' })

const suggestions = [
  'What affects EUR/USD?',
  'Explain pip values',
  'Current market outlook',
  'Best pairs for beginners',
]

// Context widgets state
const searchQuery = ref('')
const showSearchDropdown = ref(false)
const searchBarRef = ref(null)
const showOnlyTradeable = ref(false)
const selectedWidget = ref(null)
const contextWidgets = ref([])  // [{ pair, price, change, miniPath }]
const selectedPortfolioPeriod = ref('1M')
const showPortfolioChart = ref(false)  // Collapsed by default to save space

// Search results for currency pairs
const searchResults = computed(() => {
  const rates = forexStore.rates
  const keys = Object.keys(rates)
  
  let results = keys.map((key) => {
    const pair = `${key.slice(0, 3)}/${key.slice(3)}`
    const price = rates[key].toFixed(4)
    return { pair, price }
  })
  
  // Filter by holdings if toggle is on
  if (showOnlyTradeable.value && portfolioStore.holdings.length > 0) {
    const heldCurrencies = portfolioStore.holdings.map(h => 
      h['currency-ticker-symbol'] || h.currency
    )
    
    const allCurrencies = forexStore.currencies.map(c => c.code)
    const syntheticPairs = []
    heldCurrencies.forEach(base => {
      allCurrencies.forEach(quote => {
        if (base !== quote) {
          const pairStr = `${base}/${quote}`
          const exists = results.some(item => item.pair === pairStr)
          if (!exists) {
            syntheticPairs.push({ pair: pairStr, price: '—' })
          }
        }
      })
    })
    
    const allPairs = [...results, ...syntheticPairs]
    results = allPairs.filter(item => {
      const [base] = item.pair.split('/')
      return heldCurrencies.includes(base)
    })
  }
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    results = results.filter(r => r.pair.toLowerCase().includes(q))
  }
  
  return results.slice(0, 20)
})

function handleSearchFocus() {
  showSearchDropdown.value = true
}

function handleSearchBlur() {
  setTimeout(() => {
    showSearchDropdown.value = false
  }, 200)
}

function handleClickOutside(event) {
  if (searchBarRef.value && !searchBarRef.value.contains(event.target)) {
    showSearchDropdown.value = false
  }
}

async function selectCurrencyPair(pair) {
  searchQuery.value = ''
  showSearchDropdown.value = false
  
  // Check if already in widgets
  if (contextWidgets.value.some(w => w.pair === pair)) {
    selectedWidget.value = pair
    return
  }
  
  // Load chart data for this pair
  const [from, to] = pair.split('/')
  const result = await forexStore.fetchPairHistory(from, to, '1d')
  const candles = result.candles || []
  
  const closes = candles.map(c => c.close).filter(n => n > 0 && Number.isFinite(n))
  const change = candles.length >= 2
    ? ((candles[candles.length - 1].close - candles[0].close) / candles[0].close) * 100
    : 0
  
  const rate = forexStore.getRate(from, to)
  
  contextWidgets.value.push({
    pair,
    price: rate ? rate.toFixed(4) : '—',
    change,
    miniPath: getMiniChartPath(closes),
    addedAt: Date.now()
  })
  
  selectedWidget.value = pair
}

function getMiniChartPath(data) {
  if (!data || data.length < 2) return ''
  const width = 120
  const height = 40
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  return (
    'M ' +
    data
      .map((value, index) => {
        const x = (index / (data.length - 1)) * width
        const y = height - ((value - min) / range) * height
        return `${x},${y}`
      })
      .join(' L ')
  )
}

function selectWidget(pair) {
  selectedWidget.value = pair
}

function removeWidget(pair) {
  contextWidgets.value = contextWidgets.value.filter(w => w.pair !== pair)
  if (selectedWidget.value === pair) {
    selectedWidget.value = null
  }
}

// Portfolio chart data
const portfolioChartData = computed(() => {
  const history = portfolioStore.historyData
  if (!history?.data_points?.length) return null
  
  const labels = history.data_points.map(pt => {
    const date = new Date(pt.date)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })
  
  const values = history.data_points.map(pt => pt.value)
  
  return {
    labels,
    datasets: [{
      data: values,
      borderColor: '#fbbf24',
      backgroundColor: 'rgba(251, 191, 36, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 4,
      pointHoverBackgroundColor: '#fbbf24',
    }]
  }
})

const portfolioChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fbbf24',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      padding: 8,
      displayColors: false,
      callbacks: {
        label: (context) => `$${context.parsed.y.toFixed(2)}`
      }
    }
  },
  scales: {
    x: {
      display: false
    },
    y: {
      display: false
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  
  try {
    const { data } = await preferencesApi.get()
    isAdmin.value = !!data.is_admin
    if (isAdmin.value) await loadKeys()
  } catch {
    // not admin or preferences unavailable
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

async function loadKeys() {
  try {
    const { data } = await llmApi.getKeys()
    apiKeys.value = data
  } catch {
    // 403 or other error
  }
}

async function addKey() {
  if (!newKey.value.api_key) return
  await llmApi.createKey(newKey.value)
  newKey.value = { provider: 'openai', label: '', api_key: '' }
  await loadKeys()
}

async function activateKey(keyId) {
  await llmApi.activateKey(keyId)
  await loadKeys()
}

async function deleteKey(keyId) {
  await llmApi.deleteKey(keyId)
  await loadKeys()
}

function renderAssistantMarkdown(text) {
  return md.render(text || '')
}

// Strip [Context: ...] prefix from user messages for display
function stripContextPrefix(content) {
  return content.replace(/^\[Context:[^\]]+\]\s*/, '')
}

function send(text) {
  const msg = text || input.value.trim()
  if (!msg || store.loading) return
  input.value = ''
  
  // Build context from selected currency widgets (as tags)
  let contextPrefix = ''
  if (contextWidgets.value.length > 0) {
    const pairs = contextWidgets.value.map(w => w.pair).join(', ')
    contextPrefix = `[Context: ${pairs}] `
  }
  
  // Prepend context to message for better LLM understanding
  const messageWithContext = contextPrefix + msg
  store.sendMessage(messageWithContext)
}

// Auto-scroll on new messages or when loading changes
watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }
)

watch(
  () => store.loading,
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }
)
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.glass-inner {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.llm-layout {
  display: grid;
  grid-template-columns: 30% 1px 1fr;
  gap: 0;
  min-height: calc(100vh - 8rem);
  height: calc(100vh - 8rem);
}

.left-sidebar {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.divider {
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.05),
    rgba(255, 255, 255, 0.1),
    rgba(255, 255, 255, 0.05)
  );
  width: 1px;
}

.chat-section {
  background: rgba(255, 255, 255, 0.01);
  overflow: hidden;
}

.portfolio-widget {
  min-height: 80px;
  transition: min-height 0.3s ease;
}

.portfolio-widget.expanded {
  min-height: 280px;
}

.typing-indicator span {
  animation-duration: 1s;
  animation-iteration-count: infinite;
}

.context-widgets-scroll {
  overflow-y: auto;
}

.context-widgets-scroll::-webkit-scrollbar {
  width: 6px;
}

.context-widgets-scroll::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.context-widgets-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.context-widgets-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chat-scroll {
  overflow-y: auto;
}

.chat-scroll::-webkit-scrollbar {
  width: 6px;
}

.chat-scroll::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.chat-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.chat-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.mini-chart {
  display: block;
}

/* Prose styling for markdown */
.prose {
  max-width: none;
  font-size: 0.875rem;
  line-height: 1.5;
}

.prose p {
  margin-bottom: 0.75rem;
}

.prose ul, .prose ol {
  margin-bottom: 0.75rem;
  padding-left: 1.5rem;
}

.prose code {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
}

.prose pre {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.75rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin-bottom: 0.75rem;
}

.prose pre code {
  background: none;
  padding: 0;
}

/* Message slide-in fade transitions */
.message-move,
.message-enter-active {
  transition: all 0.4s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.message-leave-active {
  transition: all 0.3s ease;
}

.message-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
