<template>
  <div class="container mx-auto px-0 py-0">
    <!-- <h1 class="text-6xl font-bold font-goldman text-primary mb-8">Dashboard</h1>
    
    <!-- Adaptive Bento Box Layout -->
    <div class="dashboard-grid">
      <!-- Portfolio Widget - Always the largest -->
      <div 
        class="portfolio-area glass p-6 rounded-xl hover:shadow-xl widget-card"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <div
              draggable="true"
              @dragstart="handleDragStart($event, 'portfolio')"
              @dragend="handleDragEnd"
              class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
            >
              <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-white">Portfolio</h2>
          </div>
          <div class="flex gap-2">
            <button
              @click="showDepositModal = true"
              class="px-4 py-1.5 bg-primary text-black rounded-full text-sm font-bold hover:opacity-80 transition"
            >
              + Deposit
            </button>
            <button
              @click="showWithdrawModal = true"
              class="px-4 py-1.5 border border-gray-600 text-gray-300 rounded-full text-sm font-bold hover:border-gray-400 hover:text-white transition"
            >
              − Withdraw
            </button>
          </div>
        </div>

        <!-- Deposit Modal -->
        <Teleport to="body">
          <div v-if="showDepositModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="closeDeposit">
            <div class="bg-bg-secondary border border-gray-700 rounded-2xl p-6 w-full max-w-sm mx-4">
              <h3 class="text-xl font-bold text-white mb-4">Deposit Funds</h3>
              <div class="space-y-4">
                <div>
                  <label class="text-sm text-gray-400 mb-1 block">Currency</label>
                  <select v-model="depositCurrency" class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary">
                    <option value="USD">USD — US Dollar</option>
                    <option value="AUD">AUD — Australian Dollar</option>
                    <option value="CAD">CAD — Canadian Dollar</option>
                  </select>
                </div>
                <div>
                  <label class="text-sm text-gray-400 mb-1 block">Amount</label>
                  <input
                    v-model.number="depositAmount"
                    type="number"
                    min="0.01"
                    step="0.01"
                    placeholder="0.00"
                    class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                  />
                </div>
                <p v-if="depositError" class="text-red-400 text-sm">{{ depositError }}</p>
                <div class="flex gap-3 pt-2">
                  <button @click="closeDeposit" class="flex-1 py-3 border border-gray-600 text-gray-400 rounded-full font-bold hover:border-gray-400 transition">
                    Cancel
                  </button>
                  <button @click="handleDeposit" :disabled="depositLoading" class="flex-1 py-3 bg-primary text-black rounded-full font-bold hover:opacity-80 transition disabled:opacity-50">
                    {{ depositLoading ? 'Depositing...' : 'Confirm' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Teleport>

        <!-- Withdraw Modal -->
        <Teleport to="body">
          <div v-if="showWithdrawModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="closeWithdraw">
            <div class="bg-bg-secondary border border-gray-700 rounded-2xl p-6 w-full max-w-sm mx-4">
              <h3 class="text-xl font-bold text-white mb-4">Withdraw Funds</h3>
              <div class="space-y-4">
                <div>
                  <label class="text-sm text-gray-400 mb-1 block">Currency</label>
                  <select v-model="withdrawCurrency" class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary">
                    <option value="USD">USD — US Dollar</option>
                    <option value="AUD">AUD — Australian Dollar</option>
                    <option value="CAD">CAD — Canadian Dollar</option>
                  </select>
                </div>
                <div>
                  <label class="text-sm text-gray-400 mb-1 block">Amount</label>
                  <input
                    v-model.number="withdrawAmount"
                    type="number"
                    min="0.01"
                    step="0.01"
                    placeholder="0.00"
                    class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                  />
                </div>
                <p v-if="withdrawError" class="text-red-400 text-sm">{{ withdrawError }}</p>
                <div class="flex gap-3 pt-2">
                  <button @click="closeWithdraw" class="flex-1 py-3 border border-gray-600 text-gray-400 rounded-full font-bold hover:border-gray-400 transition">
                    Cancel
                  </button>
                  <button @click="handleWithdraw" :disabled="withdrawLoading" class="flex-1 py-3 bg-red-600 text-white rounded-full font-bold hover:opacity-80 transition disabled:opacity-50">
                    {{ withdrawLoading ? 'Withdrawing...' : 'Confirm' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Teleport>

        <div class="bg-bg-primary rounded-lg p-4 min-h-64">
          <div v-if="portfolioStore.loading" class="space-y-2">
            <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
            <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
            <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
          </div>
          <div v-else-if="portfolioStore.error" class="flex items-center justify-center h-48 text-red-400 text-sm">
            {{ portfolioStore.error }}
          </div>
          <div v-else-if="portfolioStore.holdings.length === 0" class="flex items-center justify-center h-48 text-gray-500 text-sm">
            No holdings yet. Deposit funds to get started.
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="holding in portfolioStore.holdings"
              :key="holding['currency-ticker-symbol'] || holding.currency"
              class="flex justify-between items-center px-4 py-3 bg-bg-secondary rounded-lg"
            >
              <span class="font-bold text-white text-lg">{{ holding['currency-ticker-symbol'] || holding.currency }}</span>
              <span class="text-primary font-mono text-lg">{{ Number(holding.amount).toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Adaptive Widgets Container -->
      <div class="adaptive-widgets">
        <template v-for="widgetId in sideWidgets" :key="widgetId">
          <!-- Wishlist Widget -->
          <div 
            v-if="widgetId === 'wishlist'"
            @dragover.prevent="handleDragOver($event, 'wishlist')"
            @drop="handleDrop($event, 'wishlist')"
            :class="`glass p-6 rounded-xl hover:shadow-xl widget-card ${
              draggedWidget === 'wishlist' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'wishlist')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Wishlist</h2>
              </div>
            </div>
            <div class="space-y-2">
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
            </div>
          </div>

          <!-- Feed Widget -->
          <div 
            v-else-if="widgetId === 'feed'"
            @dragover.prevent="handleDragOver($event, 'feed')"
            @drop="handleDrop($event, 'feed')"
            :class="`glass p-6 rounded-xl hover:shadow-xl widget-card ${
              draggedWidget === 'feed' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'feed')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Feed</h2>
              </div>
            </div>
            <div class="space-y-2">
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'

const portfolioStore = usePortfolioStore()

onMounted(() => {
  portfolioStore.fetchHoldings()
})

// Deposit modal state
const showDepositModal = ref(false)
const depositCurrency  = ref('USD')
const depositAmount    = ref(null)
const depositLoading   = ref(false)
const depositError     = ref('')

function closeDeposit() {
  showDepositModal.value = false
  depositAmount.value    = null
  depositError.value     = ''
}

async function handleDeposit() {
  depositError.value = ''
  if (!depositAmount.value || depositAmount.value <= 0) {
    depositError.value = 'Enter a positive amount.'
    return
  }
  depositLoading.value = true
  try {
    await portfolioStore.deposit(depositCurrency.value, depositAmount.value)
    closeDeposit()
  } catch (e) {
    depositError.value = e.response?.data?.detail || 'Deposit failed.'
  } finally {
    depositLoading.value = false
  }
}

// Withdraw modal state
const showWithdrawModal = ref(false)
const withdrawCurrency  = ref('USD')
const withdrawAmount    = ref(null)
const withdrawLoading   = ref(false)
const withdrawError     = ref('')

function closeWithdraw() {
  showWithdrawModal.value = false
  withdrawAmount.value    = null
  withdrawError.value     = ''
}

async function handleWithdraw() {
  withdrawError.value = ''
  if (!withdrawAmount.value || withdrawAmount.value <= 0) {
    withdrawError.value = 'Enter a positive amount.'
    return
  }
  withdrawLoading.value = true
  try {
    await portfolioStore.withdraw(withdrawCurrency.value, withdrawAmount.value)
    closeWithdraw()
  } catch (e) {
    withdrawError.value = e.response?.data?.detail || 'Withdrawal failed.'
  } finally {
    withdrawLoading.value = false
  }
}

// Portfolio is always main, only side widgets can be reordered
const sideWidgets = ref(['wishlist', 'feed'])
const draggedWidget = ref(null)

const handleDragStart = (event, widgetId) => {
  // Only allow dragging side widgets
  if (widgetId === 'portfolio') return
  
  draggedWidget.value = widgetId
  event.dataTransfer.effectAllowed = 'move'
}

const handleDragOver = (event, widgetId) => {
  event.preventDefault()
  
  if (!draggedWidget.value || draggedWidget.value === widgetId || draggedWidget.value === 'portfolio') {
    return
  }
  
  // Live reorder side widgets
  const newOrder = [...sideWidgets.value]
  const dragIndex = newOrder.indexOf(draggedWidget.value)
  const dropIndex = newOrder.indexOf(widgetId)
  
  // Remove from current position
  newOrder.splice(dragIndex, 1)
  
  // Insert at new position
  newOrder.splice(dropIndex, 0, draggedWidget.value)
  
  sideWidgets.value = newOrder
}

const handleDrop = (event, widgetId) => {
  event.preventDefault()
  
  // Save to localStorage
  localStorage.setItem('sideWidgetOrder', JSON.stringify(sideWidgets.value))
  
  draggedWidget.value = null
}

const handleDragEnd = () => {
  draggedWidget.value = null
}

// Load saved state
const savedOrder = localStorage.getItem('sideWidgetOrder')
if (savedOrder) {
  try {
    sideWidgets.value = JSON.parse(savedOrder)
  } catch (e) {
    console.error('Failed to load widget order', e)
  }
}
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.glass:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 215, 0, 0.2);
}

/* Adaptive Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 2fr 1fr;
    grid-template-rows: auto;
    gap: 1rem;
  }
  
  .portfolio-area {
    grid-row: span 2;
    min-height: 500px;
  }
  
  .adaptive-widgets {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .adaptive-widgets > div {
    flex: 1;
    min-height: 240px;
  }
}

/* Smooth transitions */
.widget-card {
  transition: all 0.3s ease;
}

/* Placeholder for dragged widget */
.dragging-placeholder {
  opacity: 0.3;
  border: 2px dashed rgba(255, 215, 0, 0.5);
}

/* Drag handle */
.drag-handle {
  transition: all 0.2s ease;
}

.drag-handle:hover {
  transform: scale(1.1);
}
</style>
