<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-white">Trade</h1>

    <!-- Tab Switcher -->
    <div class="flex gap-1 p-1 bg-bg-primary rounded-xl w-fit">
      <button
        @click="activeTab = 'exchange'"
        :class="['px-5 py-2 rounded-lg text-sm font-semibold transition-all duration-200',
          activeTab === 'exchange' ? 'bg-primary text-black shadow' : 'text-gray-400 hover:text-white']"
      >
        Currency Exchange
      </button>
      <button
        @click="activeTab = 'send'"
        :class="['px-5 py-2 rounded-lg text-sm font-semibold transition-all duration-200',
          activeTab === 'send' ? 'bg-primary text-black shadow' : 'text-gray-400 hover:text-white']"
      >
        Send to User
      </button>
    </div>

    <!-- ── Currency Exchange Form ── -->
    <div v-if="activeTab === 'exchange'" class="glass p-6 rounded-xl">
      <h2 class="text-lg font-bold text-white mb-5">Exchange Currency</h2>

      <!-- From / Swap / To -->
      <div class="flex items-center gap-3 mb-4">
        <div class="flex-1">
          <label class="text-xs text-gray-400 mb-1 block">From</label>
          <select v-model="fromCurrency" @change="fetchRate"
            class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary">
            <option value="USD">USD — US Dollar</option>
            <option value="AUD">AUD — Australian Dollar</option>
            <option value="CAD">CAD — Canadian Dollar</option>
          </select>
        </div>

        <div class="mt-5 flex-shrink-0">
          <button @click="swapCurrencies"
            class="p-2 rounded-full border border-gray-700 text-gray-400 hover:border-primary hover:text-primary transition">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </button>
        </div>

        <div class="flex-1">
          <label class="text-xs text-gray-400 mb-1 block">To</label>
          <select v-model="toCurrency" @change="fetchRate"
            class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary">
            <option value="USD">USD — US Dollar</option>
            <option value="AUD">AUD — Australian Dollar</option>
            <option value="CAD">CAD — Canadian Dollar</option>
          </select>
        </div>
      </div>

      <!-- Amount -->
      <div class="mb-4">
        <label class="text-xs text-gray-400 mb-1 block">Amount to Send</label>
        <input
          v-model.number="exchangeAmount"
          type="number" min="0.01" step="0.01" placeholder="0.00"
          @input="computeReceive"
          class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
        />
        <p class="text-xs text-gray-500 mt-1">
          Balance: <span class="text-gray-300">{{ exchangeFromBalance.toFixed(2) }} {{ fromCurrency }}</span>
        </p>
      </div>

      <!-- Rate & Preview -->
      <div v-if="currentRate" class="bg-bg-primary rounded-lg px-4 py-3 mb-4 space-y-1 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-400">Rate</span>
          <span class="text-primary font-mono">1 {{ fromCurrency }} = {{ currentRate.toFixed(6) }} {{ toCurrency }}</span>
        </div>
        <div v-if="receiveAmount" class="flex justify-between">
          <span class="text-gray-400">You receive</span>
          <span class="text-green-400 font-mono font-bold">{{ receiveAmount.toFixed(6) }} {{ toCurrency }}</span>
        </div>
        <span v-if="rateLoading" class="text-gray-500 text-xs">Refreshing...</span>
      </div>
      <div v-else-if="rateLoading" class="text-gray-500 text-sm mb-4">Fetching rate...</div>
      <div v-else-if="rateError" class="text-red-400 text-sm mb-4">{{ rateError }}</div>

      <p v-if="tradeError"   class="text-red-400 text-sm mb-3">{{ tradeError }}</p>
      <p v-if="tradeSuccess" class="text-green-400 text-sm mb-3">{{ tradeSuccess }}</p>

      <button
        @click="executeTrade"
        :disabled="tradeLoading || !currentRate || !exchangeAmount"
        class="w-full py-3 bg-primary text-black rounded-full font-bold hover:opacity-80 transition disabled:opacity-50"
      >
        {{ tradeLoading ? 'Processing...' : 'Execute Trade' }}
      </button>
    </div>

    <!-- ── Send to User Form ── -->
    <div v-else class="glass p-6 rounded-xl">
      <h2 class="text-lg font-bold text-white mb-5">Send Funds to Another User</h2>

      <div class="space-y-4">
        <div>
          <label class="text-xs text-gray-400 mb-1 block">Recipient Email</label>
          <input
            v-model="transferEmail"
            type="email" placeholder="recipient@example.com"
            class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
          />
        </div>

        <div>
          <label class="text-xs text-gray-400 mb-1 block">Currency</label>
          <select v-model="transferCurrency"
            class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary">
            <option value="USD">USD — US Dollar</option>
            <option value="AUD">AUD — Australian Dollar</option>
            <option value="CAD">CAD — Canadian Dollar</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">
            Balance: <span class="text-gray-300">{{ transferFromBalance.toFixed(2) }} {{ transferCurrency }}</span>
          </p>
        </div>

        <div>
          <label class="text-xs text-gray-400 mb-1 block">Amount</label>
          <input
            v-model.number="transferAmount"
            type="number" min="0.01" step="0.01" placeholder="0.00"
            class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
          />
        </div>

        <p v-if="transferError"   class="text-red-400 text-sm">{{ transferError }}</p>
        <p v-if="transferSuccess" class="text-green-400 text-sm">{{ transferSuccess }}</p>

        <button
          @click="executeTransfer"
          :disabled="transferLoading || !transferAmount || !transferEmail"
          class="w-full py-3 bg-primary text-black rounded-full font-bold hover:opacity-80 transition disabled:opacity-50"
        >
          {{ transferLoading ? 'Sending...' : 'Send Funds' }}
        </button>
      </div>
    </div>

    <!-- ── Transaction History ── -->
    <div class="glass p-6 rounded-xl">
      <div class="flex items-center justify-between mb-5">
        <h2 class="text-lg font-bold text-white">Transaction History</h2>
        <button @click="loadHistory" class="text-sm text-gray-400 hover:text-white transition">Refresh</button>
      </div>

      <div v-if="historyLoading" class="space-y-3">
        <div class="h-16 bg-bg-primary rounded-lg animate-pulse"></div>
        <div class="h-16 bg-bg-primary rounded-lg animate-pulse"></div>
        <div class="h-16 bg-bg-primary rounded-lg animate-pulse"></div>
      </div>

      <div v-else-if="transactions.length === 0" class="text-gray-500 text-sm py-6 text-center">
        No transactions yet.
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="tx in transactions"
          :key="tx.transaction_id"
          class="bg-bg-primary rounded-xl px-4 py-3 space-y-2"
        >
          <!-- Top row: type badge + currencies + amounts -->
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center gap-3">
              <span :class="['px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wide', typeBadgeClass(tx.type)]">
                {{ tx.type || 'OTHER' }}
              </span>
              <span class="text-white font-mono text-sm">
                {{ tx.sender_currency_ticker_symbol }}
                <span class="text-gray-500 mx-1">→</span>
                {{ tx.receiver_currency_ticker_symbol }}
              </span>
            </div>
            <div class="text-sm font-mono">
              <span class="text-gray-300">{{ formatAmount(tx['sender-amount'] ?? tx.sender_amount) }}</span>
              <span class="text-gray-500 mx-1">→</span>
              <span class="text-primary font-bold">{{ formatAmount(tx['receiver-amount'] ?? tx.receiver_amount) }}</span>
            </div>
          </div>

          <!-- Bottom row: emails + date + tx id -->
          <div class="flex items-center justify-between flex-wrap gap-2 text-xs text-gray-500">
            <span class="min-w-0 truncate">
              <span class="text-gray-400">{{ tx.sender_email }}</span>
              <span class="mx-1 text-gray-600">→</span>
              <span class="text-gray-400">{{ tx.receiver_email }}</span>
            </span>
            <div class="flex items-center gap-3 flex-shrink-0">
              <span>{{ formatDate(tx.timestamp) }}</span>
              <span class="font-mono text-gray-600">TX: {{ tx.transaction_id?.slice(0, 8) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { tradeApi } from '@/services/api'
import { usePortfolioStore } from '@/stores/portfolio'

const portfolioStore = usePortfolioStore()

// ── Tabs ──────────────────────────────────────────────────────────────────
const activeTab = ref('exchange')

// ── Exchange form ─────────────────────────────────────────────────────────
const fromCurrency   = ref('USD')
const toCurrency     = ref('AUD')
const exchangeAmount = ref(null)
const currentRate    = ref(null)
const receiveAmount  = ref(null)
const rateLoading    = ref(false)
const rateError      = ref('')
const tradeLoading   = ref(false)
const tradeError     = ref('')
const tradeSuccess   = ref('')

// ── Send form ─────────────────────────────────────────────────────────────
const transferEmail    = ref('')
const transferCurrency = ref('USD')
const transferAmount   = ref(null)
const transferLoading  = ref(false)
const transferError    = ref('')
const transferSuccess  = ref('')

// ── History ───────────────────────────────────────────────────────────────
const transactions   = ref([])
const historyLoading = ref(false)

// ── Balance helpers ───────────────────────────────────────────────────────
function getBalance(currency) {
  const h = portfolioStore.holdings.find(
    h => (h['currency-ticker-symbol'] || h.currency) === currency
  )
  return h ? Number(h.amount) : 0
}
const exchangeFromBalance = computed(() => getBalance(fromCurrency.value))
const transferFromBalance = computed(() => getBalance(transferCurrency.value))

// ── Exchange logic ────────────────────────────────────────────────────────
async function fetchRate() {
  if (fromCurrency.value === toCurrency.value) {
    currentRate.value   = null
    receiveAmount.value = null
    rateError.value     = 'Cannot exchange a currency for itself.'
    return
  }
  rateError.value   = ''
  rateLoading.value = true
  try {
    const { data } = await tradeApi.getRate(fromCurrency.value, toCurrency.value)
    currentRate.value = data.rate
    computeReceive()
  } catch {
    rateError.value   = 'Could not fetch rate.'
    currentRate.value = null
  } finally {
    rateLoading.value = false
  }
}

function computeReceive() {
  receiveAmount.value = (currentRate.value && exchangeAmount.value > 0)
    ? exchangeAmount.value * currentRate.value
    : null
}

function swapCurrencies() {
  ;[fromCurrency.value, toCurrency.value] = [toCurrency.value, fromCurrency.value]
  fetchRate()
}

async function executeTrade() {
  tradeError.value   = ''
  tradeSuccess.value = ''
  if (!exchangeAmount.value || exchangeAmount.value <= 0) { tradeError.value = 'Enter a positive amount.'; return }
  if (fromCurrency.value === toCurrency.value) { tradeError.value = 'Cannot exchange a currency for itself.'; return }
  tradeLoading.value = true
  try {
    const { data } = await tradeApi.exchange(fromCurrency.value, toCurrency.value, exchangeAmount.value)
    tradeSuccess.value = `Trade complete: sent ${data.sent_amount} ${data.from_currency}, received ${data.received_amount.toFixed(6)} ${data.to_currency} at rate ${data.rate.toFixed(6)}.`
    exchangeAmount.value = null
    receiveAmount.value  = null
    await portfolioStore.fetchHoldings()
    await loadHistory()
  } catch (e) {
    tradeError.value = e.response?.data?.detail || 'Trade failed.'
  } finally {
    tradeLoading.value = false
  }
}

// ── Transfer logic ────────────────────────────────────────────────────────
async function executeTransfer() {
  transferError.value   = ''
  transferSuccess.value = ''
  if (!transferEmail.value) { transferError.value = 'Enter a recipient email.'; return }
  if (!transferAmount.value || transferAmount.value <= 0) { transferError.value = 'Enter a positive amount.'; return }
  transferLoading.value = true
  try {
    const { data } = await tradeApi.transfer(transferEmail.value, transferCurrency.value, transferAmount.value)
    transferSuccess.value = `Sent ${data.amount} ${data.currency} to ${data.to_email}.`
    transferAmount.value  = null
    transferEmail.value   = ''
    await portfolioStore.fetchHoldings()
    await loadHistory()
  } catch (e) {
    transferError.value = e.response?.data?.detail || 'Transfer failed.'
  } finally {
    transferLoading.value = false
  }
}

// ── History logic ─────────────────────────────────────────────────────────
async function loadHistory() {
  historyLoading.value = true
  try {
    const { data } = await tradeApi.getHistory()
    transactions.value = data.transactions || []
  } catch {
    // silently ignore
  } finally {
    historyLoading.value = false
  }
}

// ── Display helpers ───────────────────────────────────────────────────────
function typeBadgeClass(type) {
  switch (type) {
    case 'EXCHANGE': return 'bg-blue-900/60 text-blue-300 border border-blue-700/40'
    case 'DEPOSIT':  return 'bg-green-900/60 text-green-300 border border-green-700/40'
    case 'WITHDRAW': return 'bg-red-900/60 text-red-300 border border-red-700/40'
    default:         return 'bg-gray-800 text-gray-400 border border-gray-700'
  }
}

function formatAmount(val) {
  const n = Number(val)
  if (isNaN(n)) return '—'
  return n.toFixed(6)
}

function formatDate(ts) {
  if (!ts) return '—'
  return new Date(ts).toLocaleString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => {
  fetchRate()
  loadHistory()
  if (portfolioStore.holdings.length === 0) portfolioStore.fetchHoldings()
})
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.glass:hover {
  border-color: rgba(255, 215, 0, 0.1);
}
</style>
