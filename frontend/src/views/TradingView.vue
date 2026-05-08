<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-white">Trade</h1>

    <!-- Main Trading Layout: Chart + Sidebar -->
    <div class="trading-layout">
      <!-- Left: TradingView Chart -->
      <div class="chart-section glass p-6 rounded-xl">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <h2 class="text-xl font-bold text-white">{{ chartPair }}</h2>
            <!-- Wishlist Heart Icon -->
            <button
              @click="toggleWishlist"
              class="p-1.5 rounded-lg transition-all hover:bg-primary/10"
              :title="isWishlisted ? 'Remove from wishlist' : 'Add to wishlist'"
            >
              <svg 
                v-if="isWishlisted" 
                class="w-6 h-6 text-primary fill-current" 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <svg 
                v-else 
                class="w-6 h-6 text-primary" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </button>
          </div>
          
          <!-- Center: Chart Type Icons (No Labels) -->
          <div class="flex gap-2 flex-shrink-0">
            <button
              v-for="type in chartTypes"
              :key="type.id"
              @click="selectChartType(type.id)"
              :class="[
                'p-2 rounded-lg border-2 transition-all',
                chartType === type.id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white'
              ]"
              :title="type.label"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" :d="type.icon" />
              </svg>
            </button>
          </div>
          
          <div class="flex items-center gap-4">
            <span v-if="chartLoading" class="text-sm text-gray-500">Loading chart…</span>
            <template v-else>
              <span class="text-2xl font-mono text-white">{{ currentPrice.toFixed(4) }}</span>
              <span :class="['text-sm font-bold', priceChange >= 0 ? 'text-green-400' : 'text-red-400']">
                {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
              </span>
            </template>
            <!-- Fullscreen Toggle Button -->
            <button
              @click="toggleFullscreen"
              class="p-2 rounded-lg border-2 border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white transition-all"
              :title="isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'"
            >
              <svg v-if="!isFullscreen" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
              </svg>
            </button>
          </div>
        </div>
        <p v-if="chartError" class="text-xs text-red-400 mb-2">{{ chartError }}</p>
        <div ref="chartContainer" class="chart-container"></div>
        
        <!-- RSI Chart (shown when RSI indicator is active) -->
        <div v-if="activeIndicators.includes('rsi')" class="mt-2">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-bold text-gray-400">RSI (14)</span>
          </div>
          <div ref="rsiChartContainer" class="rsi-chart-container"></div>
        </div>
        
        <!-- Chart Controls Row -->
        <div class="flex items-center justify-between mt-3 gap-6">
          <!-- Left: Timeline Slider -->
          <div class="w-60 pl-0 pr-4 mb-4">
            <div class="relative">
              <!-- Timeline Track -->
              <div class="absolute top-1/2 -translate-y-1/2 w-full h-0.5 bg-gray-700"></div>
              
              <!-- Timeline Stops -->
              <div class="relative flex justify-between items-center">
                <button
                  v-for="(period, index) in timelinePeriods"
                  :key="period.value"
                  @click="selectPeriod(period.value)"
                  class="relative flex flex-col items-center group"
                  :title="`${period.label} - ${getPeriodDateLabel(period.value)}`"
                >
                  <!-- Stop Circle -->
                  <div :class="[
                    'w-3 h-3 rounded-full border-2 transition-all cursor-pointer z-10',
                    chartHistoryPeriod === period.value
                      ? 'bg-primary border-primary scale-125 shadow-lg shadow-primary/50'
                      : 'bg-bg-primary border-gray-600 group-hover:border-primary group-hover:scale-110'
                  ]"></div>
                  
                  <!-- Label Below -->
                  <span :class="[
                    'absolute top-5 text-xs font-semibold whitespace-nowrap transition-all',
                    chartHistoryPeriod === period.value
                      ? 'text-primary'
                      : 'text-gray-500 group-hover:text-gray-300'
                  ]">
                    {{ period.label }}
                  </span>
                </button>
              </div>
            </div>
          </div>

          <!-- Right: Technical Indicators -->
          <div class="flex gap-2 flex-shrink-0">
            <button
              v-for="indicator in technicalIndicators"
              :key="indicator.id"
              @click="toggleIndicator(indicator.id)"
              :class="[
                'px-1.5 py-2 rounded-lg text-xs font-bold transition-all border-2',
                activeIndicators.includes(indicator.id)
                  ? 'bg-green-600 border-green-600 text-white'
                  : 'bg-bg-primary text-gray-400 border-gray-700 hover:text-white hover:border-gray-600'
              ]"
              :title="indicator.name"
            >
              {{ indicator.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Trading Widgets Sidebar -->
      <div class="widgets-sidebar">
        <!-- Exchange Widget -->
        <div class="glass p-4 rounded-xl flex flex-col h-full">
          <h3 class="text-sm font-bold text-white mb-3">Exchange Currency</h3>

          <!-- Order Type Row -->
          <div class="mb-4">
            <label class="text-xs text-gray-400 mb-1.5 block font-medium">Order Type</label>
            <div class="flex gap-2">
              <button @click="orderType = 'Market'" type="button" title="Market Order"
                :class="['flex-1 flex items-center justify-center p-3 rounded-lg border-2 transition-all', orderType === 'Market' ? 'border-primary bg-primary/10 text-primary' : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white']">
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </button>
              <button @click="orderType = 'Limit'" type="button" title="Limit Order"
                :class="['flex-1 flex items-center justify-center p-3 rounded-lg border-2 transition-all', orderType === 'Limit' ? 'border-primary bg-primary/10 text-primary' : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white']">
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 17l4-4 4 4 4-4 4 4M3 12h18"/>
                </svg>
              </button>
              <button @click="orderType = 'Stop'" type="button" title="Stop Order"
                :class="['flex-1 flex items-center justify-center p-3 rounded-lg border-2 transition-all', orderType === 'Stop' ? 'border-primary bg-primary/10 text-primary' : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white']">
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 17l4-8 4 4 4-8 4 8M3 21h18"/>
                </svg>
              </button>
              <button @click="orderType = 'Stop-Limit'" type="button" title="Stop-Limit Order"
                :class="['flex-1 flex items-center justify-center p-3 rounded-lg border-2 transition-all', orderType === 'Stop-Limit' ? 'border-primary bg-primary/10 text-primary' : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white']">
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 17l4-8 4 4 4-8 4 8M3 12h18M3 21h18"/>
                </svg>
              </button>
            </div>
            <p class="text-xs mt-2 font-semibold text-white">
              {{ orderType === 'Market' ? 'Market Order' : orderType === 'Limit' ? 'Limit Order' : orderType === 'Stop' ? 'Stop Order' : 'Stop-Limit Order' }}
              <span class="font-normal text-gray-500 ml-1">—
                {{ orderType === 'Market' ? 'fills immediately at current price' :
                   orderType === 'Limit'  ? 'fills when rate reaches your target' :
                   orderType === 'Stop'   ? 'triggers when rate hits your stop' :
                                            'stop triggers, fills up to limit price' }}
              </span>
            </p>
          </div>

          <!-- Target / Limit price inputs (non-market only) -->
          <div v-if="orderType !== 'Market'" class="mb-4 space-y-3">
            <!-- Target / Stop price -->
            <div>
              <label class="text-xs text-gray-400 mb-1.5 block font-medium">
                {{ orderType === 'Stop-Limit' ? 'Stop Price' : orderType === 'Limit' ? 'Target Price (fill at or below)' : 'Stop Price (fill at or above)' }}
              </label>
              <div class="relative">
                <input
                  v-model.number="targetPrice"
                  type="number" min="0.000001" step="0.0001" placeholder="0.000000"
                  class="w-full px-3 py-2.5 bg-bg-primary border-2 border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary transition-all font-mono"
                />
                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-semibold">{{ toCurrency }}</span>
              </div>
              <p v-if="currentRate" class="text-xs text-gray-600 mt-1 font-mono">
                Live rate: <span class="text-gray-400">{{ currentRate.toFixed(6) }}</span>
                <span v-if="targetPrice && orderType === 'Limit'" :class="targetPrice < currentRate ? 'text-green-500' : 'text-yellow-500'" class="ml-2">
                  {{ targetPrice < currentRate ? '↓ below market' : '↑ above market — will fill immediately' }}
                </span>
                <span v-if="targetPrice && orderType === 'Stop'" :class="targetPrice > currentRate ? 'text-green-500' : 'text-yellow-500'" class="ml-2">
                  {{ targetPrice > currentRate ? '↑ above market' : '↓ below market — will fill immediately' }}
                </span>
              </p>
            </div>

            <!-- Limit price (Stop-Limit only) -->
            <div v-if="orderType === 'Stop-Limit'">
              <label class="text-xs text-gray-400 mb-1.5 block font-medium">
                Limit Price <span class="text-gray-600">(max rate to accept)</span>
              </label>
              <div class="relative">
                <input
                  v-model.number="limitPrice"
                  type="number" min="0.000001" step="0.0001" placeholder="0.000000"
                  class="w-full px-3 py-2.5 bg-bg-primary border-2 border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary transition-all font-mono"
                />
                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-semibold">{{ toCurrency }}</span>
              </div>
              <p class="text-xs text-gray-600 mt-1">Must be ≥ stop price</p>
            </div>

            <!-- Plain-English order preview -->
            <div v-if="exchangeAmount && targetPrice" class="rounded-lg bg-bg-secondary border border-gray-700 px-3 py-2 text-xs text-gray-400 leading-relaxed">
              <template v-if="orderType === 'Limit'">
                Buy <span class="text-white font-semibold">{{ exchangeAmount }} {{ fromCurrency }}</span> worth of <span class="text-white font-semibold">{{ toCurrency }}</span> once the rate drops to <span class="text-blue-300 font-mono">{{ targetPrice }}</span> or lower.
              </template>
              <template v-else-if="orderType === 'Stop'">
                Sell <span class="text-white font-semibold">{{ exchangeAmount }} {{ fromCurrency }}</span> into <span class="text-white font-semibold">{{ toCurrency }}</span> once the rate rises to <span class="text-orange-300 font-mono">{{ targetPrice }}</span> or higher.
              </template>
              <template v-else-if="orderType === 'Stop-Limit' && limitPrice">
                Triggered at <span class="text-purple-300 font-mono">{{ targetPrice }}</span> — fills <span class="text-white font-semibold">{{ exchangeAmount }} {{ fromCurrency }}</span> only if rate ≤ <span class="text-purple-200 font-mono">{{ limitPrice }}</span>.
              </template>
            </div>
          </div>

          <!-- Currency Pair (Locked to Chart) -->
          <div class="mb-4">
            <label class="text-xs text-gray-400 mb-1.5 block font-medium">Currency Pair (locked to chart)</label>
            <div class="flex items-center gap-2">
              <!-- From Currency (Display Only) -->
              <div class="flex-1 px-3 py-2.5 bg-gradient-to-br from-bg-primary to-bg-secondary border-2 border-gray-700 rounded-lg">
                <span class="text-white text-sm font-bold">{{ fromCurrency }}</span>
              </div>
              
              <!-- Swap Direction Button -->
              <button
                @click="swapPairDirection"
                class="p-2 rounded-lg border-2 border-gray-700 bg-bg-primary hover:border-primary hover:bg-primary/10 transition-all group"
                title="Swap to inverse pair"
              >
                <svg class="w-4 h-4 text-gray-400 group-hover:text-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
              </button>
              
              <!-- To Currency (Display Only) -->
              <div class="flex-1 px-3 py-2.5 bg-gradient-to-br from-bg-primary to-bg-secondary border-2 border-gray-700 rounded-lg">
                <span class="text-white text-sm font-bold">{{ toCurrency }}</span>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1.5">
              Balance: <span class="text-gray-300 font-semibold">{{ exchangeFromBalance.toFixed(2) }} {{ fromCurrency }}</span>
            </p>
          </div>

          <!-- Amount -->
          <div class="mb-4">
            <label class="text-xs text-gray-400 mb-1.5 block font-medium">Amount</label>
            <div class="relative">
              <input
                v-model.number="exchangeAmount"
                type="number" min="0.01" step="0.01" placeholder="0.00"
                @input="computeReceive"
                class="w-full px-3 py-2.5 bg-bg-primary border-2 border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary transition-all font-mono"
              />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-semibold">{{ fromCurrency }}</span>
            </div>
          </div>

          <!-- Rate & Preview + Execute — wrapped relative so feedback overlays it -->
          <div class="relative rounded-xl">
            <div v-if="currentRate" class="relative z-0 bg-bg-primary rounded-lg px-3 py-2 mb-3 space-y-1 text-xs">
              <div class="flex justify-between">
                <span class="text-gray-400">Rate</span>
                <span class="text-primary font-mono">1 {{ fromCurrency }} = {{ currentRate.toFixed(6) }} {{ toCurrency }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Spread</span>
                <span class="text-gray-300 font-mono">0.0002</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Fee</span>
                <span class="text-green-400 font-semibold">0%</span>
              </div>
              <div v-if="receiveAmount" class="flex justify-between pt-1 border-t border-gray-800">
                <span class="text-gray-400">You receive</span>
                <span class="text-green-400 font-mono font-bold">{{ receiveAmount.toFixed(6) }} {{ toCurrency }}</span>
              </div>
            </div>
            <div v-else-if="rateLoading" class="text-gray-500 text-xs mb-3">Fetching rate...</div>
            <div v-else-if="rateError" class="text-red-400 text-xs mb-3">{{ rateError }}</div>

            <TradeFeedbackAction
              v-model:feedback="tradeFeedback"
              :disabled="orderType === 'Market' ? (tradeLoading || !currentRate || !exchangeAmount) : (orderLoading || !exchangeAmount || !targetPrice)"
              :loading="orderType === 'Market' ? tradeLoading : orderLoading"
              :loading-label="orderType === 'Market' ? 'Processing...' : 'Placing...'"
              :button-label="orderType === 'Market' ? 'Execute Trade' : 'Place Order'"
              button-class="w-full py-2 bg-primary text-black rounded-full text-sm font-bold hover:opacity-80 transition disabled:opacity-50"
              @execute="orderType === 'Market' ? executeTrade() : placeOrder()"
            />
          </div>
        </div>
      </div>
    </div>


    <!-- Pending Orders -->
    <div class="glass p-6 rounded-xl">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-bold text-white">Orders</h2>
          <p class="text-xs text-gray-500 mt-0.5">Limit, Stop, and Stop-Limit orders waiting to fill</p>
        </div>
        <button @click="loadOrders" class="text-sm text-primary hover:text-primary/80 font-semibold transition">Refresh</button>
      </div>

      <div v-if="ordersLoading" class="space-y-3">
        <div class="h-24 bg-bg-primary rounded-xl animate-pulse"></div>
        <div class="h-24 bg-bg-primary rounded-xl animate-pulse"></div>
      </div>

      <div v-else-if="pendingOrders.length === 0" class="py-10 text-center">
        <svg class="w-12 h-12 text-gray-700 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="text-gray-500 text-sm">No orders yet</p>
        <p class="text-gray-600 text-xs mt-1">Place a Limit, Stop, or Stop-Limit order to see it here</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="order in pendingOrders"
          :key="order.order_id"
          class="bg-bg-primary rounded-lg px-4 py-3 border hover:border-gray-700 transition"
          :class="order.status === 'PENDING'
            ? 'border-gray-800'
            : order.status === 'FILLED'
              ? 'border-primary/20'
              : 'border-gray-800 opacity-50'"
        >
          <!-- Top row: order type badge + pair + amount → condition + cancel -->
          <div class="flex items-center justify-between flex-wrap gap-3 mb-2">
            <div class="flex items-center gap-3">
              <!-- type badge -->
              <span
                class="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border"
                :class="order.order_type === 'Limit'
                  ? 'text-blue-300 border-blue-500/40 bg-blue-500/10'
                  : order.order_type === 'Stop'
                    ? 'text-orange-300 border-orange-500/40 bg-orange-500/10'
                    : 'text-purple-300 border-purple-500/40 bg-purple-500/10'"
              >{{ order.order_type }}</span>
              <!-- pair -->
              <div class="flex items-center gap-2 text-sm">
                <span class="text-white font-semibold">{{ order.from_currency }}</span>
                <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <span class="text-white font-semibold">{{ order.to_currency }}</span>
              </div>
            </div>

            <!-- amount → trigger condition -->
            <div class="flex items-center gap-2 text-sm font-mono">
              <span class="text-gray-400">{{ Number(order.amount).toFixed(4) }} {{ order.from_currency }}</span>
              <span class="text-gray-600">@</span>
              <template v-if="order.order_type === 'Limit'">
                <span class="text-blue-300 font-bold">≤ {{ Number(order.target_price).toFixed(6) }}</span>
              </template>
              <template v-else-if="order.order_type === 'Stop'">
                <span class="text-orange-300 font-bold">≥ {{ Number(order.target_price).toFixed(6) }}</span>
              </template>
              <template v-else>
                <span class="text-purple-300 font-bold">≥ {{ Number(order.target_price).toFixed(6) }}</span>
                <span class="text-gray-600">/</span>
                <span class="text-purple-200 font-bold">≤ {{ Number(order.limit_price).toFixed(6) }}</span>
              </template>
            </div>
          </div>

          <!-- Bottom row: status + placed date + id + cancel -->
          <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
            <div class="flex items-center gap-3 text-gray-500">
              <span
                class="font-semibold uppercase tracking-wider"
                :class="order.status === 'PENDING' ? 'text-yellow-500'
                  : order.status === 'FILLED' ? 'text-primary'
                  : 'text-gray-500'"
              >{{ order.status }}</span>
              <span>{{ formatDate(order.created_at) }}</span>
              <span v-if="order.status === 'FILLED' && order.filled_at" class="text-primary">
                Filled {{ formatDate(order.filled_at) }}
              </span>
              <span class="font-mono text-gray-600">{{ order.order_id?.slice(0, 8) }}</span>
            </div>
            <button
              v-if="order.status === 'PENDING'"
              class="text-xs text-gray-500 hover:text-red-400 border border-gray-700 hover:border-red-500/40 rounded px-2 py-0.5 transition font-semibold"
              @click="cancelOrder(order.order_id)"
            >Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction History -->
    <div class="glass p-6 rounded-xl">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-white">Transaction History</h2>
        <button @click="loadHistory" class="text-sm text-primary hover:text-primary/80 font-semibold transition">
          Refresh
        </button>
      </div>

      <div v-if="historyLoading" class="space-y-3">
        <div class="h-20 bg-bg-primary rounded-lg animate-pulse"></div>
        <div class="h-20 bg-bg-primary rounded-lg animate-pulse"></div>
        <div class="h-20 bg-bg-primary rounded-lg animate-pulse"></div>
      </div>

      <div v-else-if="transactions.length === 0" class="flex flex-col items-center justify-center py-12">
        <svg class="w-16 h-16 text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-gray-500 text-sm">No transactions yet</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="tx in transactions"
          :key="tx.transaction_id"
          class="bg-bg-primary rounded-lg px-4 py-3 border border-gray-800 hover:border-gray-700 transition"
        >
          <!-- Top row: type + currencies + amounts -->
          <div class="flex items-center justify-between flex-wrap gap-3 mb-2">
            <div class="flex items-center gap-3">
              <span class="text-xs font-bold uppercase tracking-wider text-gray-400">
                {{ tx.type || 'OTHER' }}
              </span>
              <div class="flex items-center gap-2 text-sm">
                <span class="text-white font-semibold">{{ tx.sender_currency_ticker_symbol }}</span>
                <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <span class="text-white font-semibold">{{ tx.receiver_currency_ticker_symbol }}</span>
              </div>
            </div>
            <div class="text-sm font-mono flex items-center gap-2">
              <span class="text-gray-400">{{ formatAmount(tx['sender-amount'] ?? tx.sender_amount) }}</span>
              <span class="text-gray-600">→</span>
              <span class="text-primary font-bold">{{ formatAmount(tx['receiver-amount'] ?? tx.receiver_amount) }}</span>
            </div>
          </div>

          <!-- Bottom row: emails + date + tx id -->
          <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
            <div class="flex items-center gap-2 text-gray-500 min-w-0">
              <span class="text-gray-400 truncate">{{ tx.sender_email }}</span>
              <span class="text-gray-600">→</span>
              <span class="text-gray-400 truncate">{{ tx.receiver_email }}</span>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 text-gray-500">
              <span>{{ formatDate(tx.timestamp) }}</span>
              <span class="font-mono text-gray-600">{{ tx.transaction_id?.slice(0, 8) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Fullscreen Mode Overlay with Split Layout -->
  <Teleport to="body">
    <div v-if="isFullscreen" class="fixed inset-0 z-50 bg-bg-primary flex">
      <!-- Main Chart Section (80%) -->
      <div class="flex flex-col" style="width: 80%;">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div class="flex items-center gap-4">
            <span class="text-2xl font-bold text-white">{{ chartPair }}</span>
            <span class="text-2xl font-mono text-white">{{ currentPrice.toFixed(4) }}</span>
            <span :class="['text-lg font-bold', priceChange >= 0 ? 'text-green-400' : 'text-red-400']">
              {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
            </span>
          </div>
          
          <!-- Chart Type Icons -->
          <div class="flex gap-2">
            <button
              v-for="type in chartTypes"
              :key="type.id"
              @click="selectChartType(type.id)"
              :class="[
                'p-2 rounded-lg border-2 transition-all',
                chartType === type.id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white'
              ]"
              :title="type.label"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" :d="type.icon" />
              </svg>
            </button>
          </div>
          
          <button
            @click="toggleFullscreen"
            class="p-2 rounded-lg border-2 border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white transition-all"
            title="Exit Fullscreen"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Chart Area -->
        <div class="flex-1 flex flex-col px-6 py-4 min-h-0">
          <div class="flex-1 relative min-h-0">
            <div ref="chartContainerFullscreen" class="w-full h-full"></div>
          </div>
          
          <!-- RSI Chart (if active) -->
          <div v-if="activeIndicators.includes('rsi')" class="mt-2" style="height: 120px;">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-bold text-gray-400">RSI (14)</span>
            </div>
            <div ref="rsiChartContainerFullscreen" class="w-full h-full"></div>
          </div>
        </div>
        
        <!-- Controls -->
        <div class="flex items-center justify-between px-6 py-4 gap-6 border-t border-gray-800">
          <!-- Left: Timeline Slider -->
          <div class="w-80 pl-0 pr-4">
            <div class="relative">
              <div class="absolute top-1/2 -translate-y-1/2 w-full h-0.5 bg-gray-700"></div>
              <div class="relative flex justify-between items-center">
                <button
                  v-for="period in timelinePeriods"
                  :key="period.value"
                  @click="selectPeriod(period.value)"
                  class="relative flex flex-col items-center group"
                  :title="`${period.label} - ${getPeriodDateLabel(period.value)}`"
                >
                  <div :class="[
                    'w-3 h-3 rounded-full border-2 transition-all cursor-pointer z-10',
                    chartHistoryPeriod === period.value
                      ? 'bg-primary border-primary scale-125 shadow-lg shadow-primary/50'
                      : 'bg-bg-primary border-gray-600 group-hover:border-primary group-hover:scale-110'
                  ]"></div>
                  <span :class="[
                    'absolute top-5 text-xs font-semibold whitespace-nowrap transition-all',
                    chartHistoryPeriod === period.value
                      ? 'text-primary'
                      : 'text-gray-500 group-hover:text-gray-300'
                  ]">
                    {{ period.label }}
                  </span>
                </button>
              </div>
            </div>
          </div>

          <!-- Right: Technical Indicators -->
          <div class="flex gap-2 flex-shrink-0">
            <button
              v-for="indicator in technicalIndicators"
              :key="indicator.id"
              @click="toggleIndicator(indicator.id)"
              :class="[
                'px-1.5 py-2 rounded-lg text-xs font-bold transition-all border-2',
                activeIndicators.includes(indicator.id)
                  ? 'bg-green-600 border-green-600 text-white'
                  : 'bg-bg-primary text-gray-400 border-gray-700 hover:text-white hover:border-gray-600'
              ]"
              :title="indicator.name"
            >
              {{ indicator.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Exchange Widget Sidebar (20%) -->
      <div class="border-l border-gray-800 bg-bg-secondary flex flex-col" style="width: 20%; min-width: 320px;">
        <!-- Tabs -->
        <div class="flex border-b border-gray-700">
          <button
            v-for="tab in ['exchange']"
            :key="tab"
            @click="activeTab = tab"
            :class="[
              'flex-1 py-3 px-4 text-sm font-bold capitalize transition-all',
              activeTab === tab
                ? 'text-primary border-b-2 border-primary bg-primary/5'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            ]"
          >
            {{ tab }}
          </button>
        </div>

        <!-- Tab Content (scrollable) -->
        <div class="flex-1 overflow-y-auto p-4">
          <!-- Exchange Tab -->
          <div v-if="activeTab === 'exchange'" class="space-y-4">
            <!-- Order Type Row (Fullscreen) -->
            <div>
              <label class="text-xs text-gray-400 mb-1.5 block font-medium">Order Type</label>
              <div class="flex gap-2">
                <button @click="orderType = 'Market'" type="button" title="Market Order"
                  :class="['flex-1 flex items-center justify-center p-3 rounded-lg border-2 transition-all', orderType === 'Market' ? 'border-primary bg-primary/10 text-primary' : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white']">
                  <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                </button>
                <button @click="orderType = 'Limit'" type="button" title="Limit Order"
                  :class="['flex-1 flex items-center justify-center p-3 rounded-lg border-2 transition-all', orderType === 'Limit' ? 'border-primary bg-primary/10 text-primary' : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white']">
                  <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 17l4-4 4 4 4-4 4 4M3 12h18"/>
                  </svg>
                </button>
                <button @click="orderType = 'Stop'" type="button" title="Stop Order"
                  :class="['flex-1 flex items-center justify-center p-3 rounded-lg border-2 transition-all', orderType === 'Stop' ? 'border-primary bg-primary/10 text-primary' : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white']">
                  <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 17l4-8 4 4 4-8 4 8M3 21h18"/>
                  </svg>
                </button>
                <button @click="orderType = 'Stop-Limit'" type="button" title="Stop-Limit Order"
                  :class="['flex-1 flex items-center justify-center p-3 rounded-lg border-2 transition-all', orderType === 'Stop-Limit' ? 'border-primary bg-primary/10 text-primary' : 'border-gray-700 bg-bg-primary text-gray-400 hover:border-gray-600 hover:text-white']">
                  <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 17l4-8 4 4 4-8 4 8M3 12h18M3 21h18"/>
                  </svg>
                </button>
              </div>
              <p class="text-xs mt-2 font-semibold text-white">
                {{ orderType === 'Market' ? 'Market Order' : orderType === 'Limit' ? 'Limit Order' : orderType === 'Stop' ? 'Stop Order' : 'Stop-Limit Order' }}
                <span class="font-normal text-gray-500 ml-1">—
                  {{ orderType === 'Market' ? 'fills immediately at current price' :
                     orderType === 'Limit'  ? 'fills when rate reaches your target' :
                     orderType === 'Stop'   ? 'triggers when rate hits your stop' :
                                              'stop triggers, fills up to limit price' }}
                </span>
              </p>
            </div>

            <!-- Target / Limit price inputs (fullscreen, non-market) -->
            <div v-if="orderType !== 'Market'" class="space-y-3">
              <div>
                <label class="text-xs text-gray-400 mb-1.5 block font-medium">
                  {{ orderType === 'Stop-Limit' ? 'Stop Price' : orderType === 'Limit' ? 'Target Price (fill at or below)' : 'Stop Price (fill at or above)' }}
                </label>
                <div class="relative">
                  <input
                    v-model.number="targetPrice"
                    type="number" min="0.000001" step="0.0001" placeholder="0.000000"
                    class="w-full px-3 py-2.5 bg-bg-primary border-2 border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary transition-all font-mono"
                  />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-semibold">{{ toCurrency }}</span>
                </div>
                <p v-if="currentRate" class="text-xs text-gray-600 mt-1 font-mono">
                  Live: <span class="text-gray-400">{{ currentRate.toFixed(6) }}</span>
                  <span v-if="targetPrice && orderType === 'Limit'" :class="targetPrice < currentRate ? 'text-green-500' : 'text-yellow-500'" class="ml-2">
                    {{ targetPrice < currentRate ? '↓ below market' : '↑ will fill immediately' }}
                  </span>
                  <span v-if="targetPrice && orderType === 'Stop'" :class="targetPrice > currentRate ? 'text-green-500' : 'text-yellow-500'" class="ml-2">
                    {{ targetPrice > currentRate ? '↑ above market' : '↓ will fill immediately' }}
                  </span>
                </p>
              </div>
              <div v-if="orderType === 'Stop-Limit'">
                <label class="text-xs text-gray-400 mb-1.5 block font-medium">Limit Price <span class="text-gray-600">(max rate)</span></label>
                <div class="relative">
                  <input
                    v-model.number="limitPrice"
                    type="number" min="0.000001" step="0.0001" placeholder="0.000000"
                    class="w-full px-3 py-2.5 bg-bg-primary border-2 border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary transition-all font-mono"
                  />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-semibold">{{ toCurrency }}</span>
                </div>
                <p class="text-xs text-gray-600 mt-1">Must be ≥ stop price</p>
              </div>
              <!-- Plain-English preview -->
              <div v-if="exchangeAmount && targetPrice" class="rounded-lg bg-bg-primary border border-gray-800 px-3 py-2 text-xs text-gray-400 leading-relaxed">
                <template v-if="orderType === 'Limit'">
                  Buy <span class="text-white font-semibold">{{ exchangeAmount }} {{ fromCurrency }}</span> worth of <span class="text-white font-semibold">{{ toCurrency }}</span> when rate ≤ <span class="text-blue-300 font-mono">{{ targetPrice }}</span>.
                </template>
                <template v-else-if="orderType === 'Stop'">
                  Sell <span class="text-white font-semibold">{{ exchangeAmount }} {{ fromCurrency }}</span> into <span class="text-white font-semibold">{{ toCurrency }}</span> when rate ≥ <span class="text-orange-300 font-mono">{{ targetPrice }}</span>.
                </template>
                <template v-else-if="orderType === 'Stop-Limit' && limitPrice">
                  Triggered at <span class="text-purple-300 font-mono">{{ targetPrice }}</span>, fills only if rate ≤ <span class="text-purple-200 font-mono">{{ limitPrice }}</span>.
                </template>
              </div>
            </div>

            <!-- Currency Pair (Locked to Chart) -->
            <div>
              <label class="text-xs text-gray-400 mb-1.5 block font-medium">Currency Pair</label>
              <div class="flex items-center gap-2">
                <div class="flex-1 px-3 py-2.5 bg-gradient-to-br from-bg-primary to-bg-secondary border-2 border-gray-700 rounded-lg">
                  <span class="text-white text-sm font-bold">{{ fromCurrency }}</span>
                </div>
                <button
                  @click="swapPairDirection"
                  class="p-2 rounded-lg border-2 border-gray-700 bg-bg-primary hover:border-primary hover:bg-primary/10 transition-all group"
                  title="Swap to inverse pair"
                >
                  <svg class="w-4 h-4 text-gray-400 group-hover:text-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                  </svg>
                </button>
                <div class="flex-1 px-3 py-2.5 bg-gradient-to-br from-bg-primary to-bg-secondary border-2 border-gray-700 rounded-lg">
                  <span class="text-white text-sm font-bold">{{ toCurrency }}</span>
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-1.5">
                Balance: <span class="text-gray-300 font-semibold">{{ exchangeFromBalance.toFixed(2) }} {{ fromCurrency }}</span>
              </p>
            </div>

            <!-- Amount Input -->
            <div>
              <label class="text-xs text-gray-400 mb-1.5 block font-medium">Amount</label>
              <div class="relative">
                <input
                  v-model.number="exchangeAmount"
                  type="number" min="0.01" step="0.01" placeholder="0.00"
                  @input="computeReceive"
                  class="w-full px-3 py-2.5 bg-bg-primary border-2 border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary transition-all font-mono"
                />
                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-semibold">{{ fromCurrency }}</span>
              </div>
            </div>

            <!-- Rate & Preview + Execute — wrapped relative so feedback overlays it -->
            <div class="relative rounded-xl">
              <div v-if="currentRate" class="relative z-0 bg-bg-primary rounded-lg px-3 py-2 mb-3 space-y-1 text-xs">
                <div class="flex justify-between">
                  <span class="text-gray-400">Rate</span>
                  <span class="text-primary font-mono">1 {{ fromCurrency }} = {{ currentRate.toFixed(6) }} {{ toCurrency }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400">Spread</span>
                  <span class="text-gray-300 font-mono">0.0002</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400">Fee</span>
                  <span class="text-green-400 font-semibold">0%</span>
                </div>
                <div v-if="receiveAmount" class="flex justify-between pt-1 border-t border-gray-800">
                  <span class="text-gray-400">You receive</span>
                  <span class="text-green-400 font-mono font-bold">{{ receiveAmount.toFixed(6) }} {{ toCurrency }}</span>
                </div>
              </div>
              <div v-else-if="rateLoading" class="text-gray-500 text-xs mb-3">Fetching rate...</div>
              <div v-else-if="rateError" class="text-red-400 text-xs mb-3">{{ rateError }}</div>

              <TradeFeedbackAction
                v-model:feedback="tradeFeedback"
                :disabled="orderType === 'Market' ? (tradeLoading || !currentRate || !exchangeAmount) : (orderLoading || !exchangeAmount || !targetPrice)"
                :loading="orderType === 'Market' ? tradeLoading : orderLoading"
                :loading-label="orderType === 'Market' ? 'Processing...' : 'Placing...'"
                :button-label="orderType === 'Market' ? 'Execute Trade' : 'Place Order'"
                button-class="w-full py-3 rounded-lg bg-primary text-black font-bold transition-all shadow-lg hover:opacity-80 disabled:opacity-50 disabled:cursor-not-allowed"
                @execute="orderType === 'Market' ? executeTrade() : placeOrder()"
              />
            </div>
          </div>

        </div>
      </div>
    </div>
  </Teleport>

</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { tradeApi, ordersApi } from '@/services/api'
import { usePortfolioStore } from '@/stores/portfolio'
import { useForexStore } from '@/stores/forex'
import { useAuthStore } from '@/stores/auth'
import TradeFeedbackAction from '@/components/TradeFeedbackAction.vue'
import { createChart } from 'lightweight-charts'

const route = useRoute()
const router = useRouter()
const portfolioStore = usePortfolioStore()
const forexStore = useForexStore()
const authStore = useAuthStore()

// Respect the "Trade Confirmations" notification preference
function tradeConfirmationsEnabled() {
  try {
    const key = `fxtrade_notif_local_${authStore.userId || 'anon'}`
    const local = JSON.parse(localStorage.getItem(key) || '{}')
    // Default true if not yet saved
    return local.tradeConfirmations !== false
  } catch { return true }
}

// Wishlist functionality
const isWishlisted = computed(() => portfolioStore.isInWishlist(chartPair.value))

function toggleWishlist() {
  portfolioStore.toggleWishlist(chartPair.value)
}

// ── Currencies ───────────────────────────────────────────────────────────
const currencies = computed(() => forexStore.currencies)

async function fetchCurrencies() {
  // No-op: currencies come from forex store pipeline
}

// Generate all valid trading pairs from the currencies list
const tradingPairs = computed(() => {
  const pairs = []
  const codes = currencies.value.map(c => c.code)
  // Standard convention: major base currencies paired against quote currencies
  const majorBases = ['EUR', 'GBP', 'AUD', 'NZD', 'USD']
  for (const base of codes) {
    for (const quote of codes) {
      if (base === quote) continue
      // Avoid duplicates — use market convention ordering
      const baseIdx = majorBases.indexOf(base)
      const quoteIdx = majorBases.indexOf(quote)
      if (baseIdx >= 0 && quoteIdx >= 0 && baseIdx > quoteIdx) continue
      pairs.push(`${base}/${quote}`)
    }
  }
  return pairs
})

// ── Chart ─────────────────────────────────────────────────────────────────
const chartContainer = ref(null)
const chartContainerFullscreen = ref(null)
const rsiChartContainer = ref(null)
const rsiChartContainerFullscreen = ref(null)
const chartPair = ref('EUR/USD')
const chartHistoryPeriod = ref('3mo')
const chartType = ref('candlestick')
const activeIndicators = ref([])  // Array of active indicator IDs
const _openPrice = ref(0)  // First candle close for % change denominator

// currentPrice updates live from forexStore every 4s without reloading the chart
const currentPrice = computed(() => {
  const [from, to] = chartPair.value.split('/')
  return forexStore.getRate(from, to) || _openPrice.value || 0
})
const priceChange = computed(() => {
  if (!_openPrice.value || !currentPrice.value) return 0
  return ((currentPrice.value - _openPrice.value) / _openPrice.value) * 100
})
const chartLoading = ref(false)
const chartError = ref('')
const isFullscreen = ref(false)
let chart = null
let rsiChart = null
let candlestickSeries = null
let lineSeries = null
let areaSeries = null
let baselineSeries = null

// Indicator line series (will be created on demand)
let ma20Series = null
let ma50Series = null
let ema12Series = null
let ema26Series = null
let rsiSeries = null

const timelinePeriods = [
  { label: '1D', value: '1d' },
  { label: '1W', value: '1wk' },
  { label: '1M', value: '1mo' },
  { label: '3M', value: '3mo' },
  { label: 'YTD', value: 'ytd' },
  { label: '1Y', value: '1y' },
  { label: '5Y', value: '5y' }
]

const technicalIndicators = [
  { id: 'ma20', label: 'MA20', name: 'Moving Average 20' },
  { id: 'ma50', label: 'MA50', name: 'Moving Average 50' },
  { id: 'ema12', label: 'EMA12', name: 'Exponential MA 12' },
  { id: 'ema26', label: 'EMA26', name: 'Exponential MA 26' },
  { id: 'rsi', label: 'RSI', name: 'Relative Strength Index' }
]

const chartTypes = [
  {
    id: 'candlestick',
    label: 'Candles',
    icon: 'M3 10h18M3 14h18M8 3v18M16 3v18'
  },
  {
    id: 'line',
    label: 'Line',
    icon: 'M3 17l6-6 4 4 8-8'
  },
  {
    id: 'area',
    label: 'Area',
    icon: 'M3 17l6-6 4 4 8-8M3 21h18'
  },
  {
    id: 'baseline',
    label: 'Baseline',
    icon: 'M3 12h18M3 17l6-6 4 4 8-8'
  }
]

async function initChart() {
  const container = isFullscreen.value ? chartContainerFullscreen.value : chartContainer.value
  if (!container) return
  
  // Wait for next tick to ensure DOM is fully rendered
  await nextTick()
  
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight || (isFullscreen.value ? 600 : 400)
  
  chart = createChart(container, {
    width: containerWidth || 800,
    height: containerHeight,
    layout: {
      background: { color: '#0a0a0a' },
      textColor: '#9ca3af',
    },
    grid: {
      vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
      horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
    },
    crosshair: {
      mode: 1,
    },
    rightPriceScale: {
      borderColor: 'rgba(255, 255, 255, 0.1)',
    },
    timeScale: {
      borderColor: 'rgba(255, 255, 255, 0.1)',
      timeVisible: true,
      secondsVisible: false,
      fixLeftEdge: true,
      fixRightEdge: true,
      lockVisibleTimeRangeOnResize: true,
    },
    handleScroll: isFullscreen.value ? { vertTouchDrag: false } : false,
    handleScale: isFullscreen.value ? { 
      axisPressedMouseMove: { time: true, price: true },
      mouseWheel: true,
      pinch: true
    } : false,
  })

  // Initialize all series types (only one will be visible at a time)
  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#10b981',
    downColor: '#ef4444',
    borderUpColor: '#10b981',
    borderDownColor: '#ef4444',
    wickUpColor: '#10b981',
    wickDownColor: '#ef4444',
    visible: chartType.value === 'candlestick'
  })

  lineSeries = chart.addLineSeries({
    color: '#fbbf24',
    lineWidth: 2,
    visible: chartType.value === 'line'
  })

  areaSeries = chart.addAreaSeries({
    topColor: 'rgba(251, 191, 36, 0.4)',
    bottomColor: 'rgba(251, 191, 36, 0.0)',
    lineColor: '#fbbf24',
    lineWidth: 2,
    visible: chartType.value === 'area'
  })

  baselineSeries = chart.addBaselineSeries({
    topLineColor: '#10b981',
    topFillColor1: 'rgba(16, 185, 129, 0.28)',
    topFillColor2: 'rgba(16, 185, 129, 0.05)',
    bottomLineColor: '#ef4444',
    bottomFillColor1: 'rgba(239, 68, 68, 0.05)',
    bottomFillColor2: 'rgba(239, 68, 68, 0.28)',
    lineWidth: 2,
    visible: chartType.value === 'baseline'
  })

  // Create indicator series (initially hidden)
  ma20Series = chart.addLineSeries({
    color: '#3b82f6',
    lineWidth: 1.5,
    visible: false,
    priceLineVisible: false
  })

  ma50Series = chart.addLineSeries({
    color: '#8b5cf6',
    lineWidth: 1.5,
    visible: false,
    priceLineVisible: false
  })

  ema12Series = chart.addLineSeries({
    color: '#06b6d4',
    lineWidth: 1.5,
    visible: false,
    priceLineVisible: false
  })

  ema26Series = chart.addLineSeries({
    color: '#ec4899',
    lineWidth: 1.5,
    visible: false,
    priceLineVisible: false
  })

  await loadChartData()
  
  // Handle resize
  window.addEventListener('resize', handleResize)
  
  // Force a resize after a short delay to ensure proper sizing
  setTimeout(() => {
    handleResize()
  }, 100)
}

async function initRsiChart() {
  const container = isFullscreen.value ? rsiChartContainerFullscreen.value : rsiChartContainer.value
  if (!container) return
  
  await nextTick()
  
  const containerWidth = container.clientWidth
  
  rsiChart = createChart(container, {
    width: containerWidth || 800,
    height: 120,
    layout: {
      background: { color: '#0a0a0a' },
      textColor: '#9ca3af',
    },
    grid: {
      vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
      horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
    },
    rightPriceScale: {
      borderColor: 'rgba(255, 255, 255, 0.1)',
    },
    timeScale: {
      borderColor: 'rgba(255, 255, 255, 0.1)',
      timeVisible: true,
      secondsVisible: false,
      fixLeftEdge: true,
      fixRightEdge: true,
      lockVisibleTimeRangeOnResize: true,
      visible: false,
    },
    handleScroll: false,
    handleScale: false,
  })

  rsiSeries = rsiChart.addLineSeries({
    color: '#f59e0b',
    lineWidth: 2,
    priceLineVisible: false
  })
  
  // Add reference lines at 30 and 70
  rsiChart.addLineSeries({
    color: 'rgba(239, 68, 68, 0.3)',
    lineWidth: 1,
    lineStyle: 2,
    priceLineVisible: false
  }).setData([{ time: 0, value: 70 }])
  
  rsiChart.addLineSeries({
    color: 'rgba(16, 185, 129, 0.3)',
    lineWidth: 1,
    lineStyle: 2,
    priceLineVisible: false
  }).setData([{ time: 0, value: 30 }])
}

function handleResize() {
  const container = isFullscreen.value ? chartContainerFullscreen.value : chartContainer.value
  if (chart && container) {
    const width = container.clientWidth
    const height = container.clientHeight || (isFullscreen.value ? 600 : 400)
    if (width > 0) {
      chart.applyOptions({ width, height })
    }
  }
  
  const rsiContainer = isFullscreen.value ? rsiChartContainerFullscreen.value : rsiChartContainer.value
  if (rsiChart && rsiContainer && activeIndicators.value.includes('rsi')) {
    const width = rsiContainer.clientWidth
    if (width > 0) {
      rsiChart.applyOptions({ width })
    }
  }
}

async function loadChartData(isInitialLoad = false) {
  if (!chart) return
  
  // Only show loading state on initial load, not on refresh
  if (isInitialLoad) {
    chartLoading.value = true
  }
  chartError.value = ''
  
  try {
    const parts = chartPair.value.split('/')
    if (parts.length !== 2) {
      chartError.value = 'Invalid pair.'
      return
    }
    const [from, to] = parts
    const result = await forexStore.fetchPairHistory(from, to, chartHistoryPeriod.value)
    const candles = result.candles || []
    if (candles.length === 0) {
      if (isInitialLoad) {
        chartError.value = 'No chart data for this pair.'
        currentPrice.value = 0
        priceChange.value = 0
      }
      return
    }
    
    // Update data for all series types
    if (candlestickSeries) candlestickSeries.setData(candles)
    
    // For line/area/baseline, convert to line data
    const lineData = candles.map((c) => ({ time: c.time, value: c.close }))
    if (lineSeries) lineSeries.setData(lineData)
    if (areaSeries) areaSeries.setData(lineData)
    if (baselineSeries) {
      const baseValue = candles[0]?.close || 0
      baselineSeries.setData(lineData)
      baselineSeries.applyOptions({ baseValue: { type: 'price', price: baseValue } })
    }
    
    // Update technical indicators
    updateIndicators(candles)
    
    // Fix the visible time range to match the data range exactly (disable zoom/scroll)
    if (chart && candles.length > 0) {
      const timeScale = chart.timeScale()
      const from = candles[0].time
      const to = candles[candles.length - 1].time
      timeScale.setVisibleRange({ from, to })
    }

    // Store the period-open price so priceChange% is meaningful
    _openPrice.value = candles[0]?.close || 0

    // Push the live rate as the latest tick on the current candle so the
    // chart reflects the real-time price without a full reload
    _pushLiveTick(candles)
  } catch (e) {
    if (isInitialLoad) {
      chartError.value = e.response?.data?.detail || 'Could not load chart data.'
      _openPrice.value = 0
    }
  } finally {
    if (isInitialLoad) {
      chartLoading.value = false
    }
  }
}

function updateChartPair() {
  loadChartData(true) // Initial load when pair changes
}

/**
 * Push the current live rate as an update to the latest candle.
 * lightweight-charts `update()` is O(1) — no full re-render.
 * We use floor(now / interval_seconds) as the candle bucket so the
 * tick lands on the correct bar.
 */
function _pushLiveTick(candles) {
  const liveRate = currentPrice.value
  if (!liveRate || !candles || candles.length === 0) return

  const latest = candles[candles.length - 1]
  const tick = {
    time:  latest.time,
    open:  latest.open,
    high:  Math.max(latest.high, liveRate),
    low:   Math.min(latest.low,  liveRate),
    close: liveRate,
  }

  try {
    if (candlestickSeries) candlestickSeries.update(tick)
    const lineTick = { time: latest.time, value: liveRate }
    if (lineSeries)     lineSeries.update(lineTick)
    if (areaSeries)     areaSeries.update(lineTick)
    if (baselineSeries) baselineSeries.update(lineTick)
  } catch {
    // Silently ignore if chart was destroyed mid-update
  }
}

function selectChartType(type) {
  chartType.value = type
  
  // Toggle visibility of all series
  if (candlestickSeries) candlestickSeries.applyOptions({ visible: type === 'candlestick' })
  if (lineSeries) lineSeries.applyOptions({ visible: type === 'line' })
  if (areaSeries) areaSeries.applyOptions({ visible: type === 'area' })
  if (baselineSeries) baselineSeries.applyOptions({ visible: type === 'baseline' })
}

function selectPeriod(period) {
  chartHistoryPeriod.value = period
  loadChartData(true) // Reload with new period
}

function getPeriodDateLabel(period) {
  const now = new Date()
  let targetDate = new Date()
  
  switch(period) {
    case '1d':
      return 'Today'
    case '1wk':
      targetDate.setDate(now.getDate() - 7)
      return targetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    case '1mo':
      targetDate.setMonth(now.getMonth() - 1)
      return targetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    case '3mo':
      targetDate.setMonth(now.getMonth() - 3)
      return targetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    case '6mo':
      targetDate.setMonth(now.getMonth() - 6)
      return targetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    case 'ytd':
      return 'Jan 1, ' + now.getFullYear()
    case '1y':
      targetDate.setFullYear(now.getFullYear() - 1)
      return targetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    case '3y':
      targetDate.setFullYear(now.getFullYear() - 3)
      return targetDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    case '5y':
      targetDate.setFullYear(now.getFullYear() - 5)
      return targetDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    default:
      return ''
  }
}

// Calculate Simple Moving Average
function calculateSMA(data, period) {
  const result = []
  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1)
    const avg = slice.reduce((sum, candle) => sum + candle.close, 0) / period
    result.push({ time: data[i].time, value: avg })
  }
  return result
}

// Calculate Exponential Moving Average
function calculateEMA(data, period) {
  if (data.length === 0) return []
  const result = []
  const multiplier = 2 / (period + 1)
  
  // Start with SMA for first value
  let ema = data.slice(0, period).reduce((sum, c) => sum + c.close, 0) / period
  result.push({ time: data[period - 1].time, value: ema })
  
  // Calculate EMA for remaining values
  for (let i = period; i < data.length; i++) {
    ema = (data[i].close - ema) * multiplier + ema
    result.push({ time: data[i].time, value: ema })
  }
  return result
}

// Calculate RSI (Relative Strength Index)
function calculateRSI(data, period = 14) {
  if (data.length < period + 1) return []
  
  const changes = []
  for (let i = 1; i < data.length; i++) {
    changes.push(data[i].close - data[i - 1].close)
  }
  
  const result = []
  let avgGain = 0
  let avgLoss = 0
  
  // Calculate initial average gain/loss
  for (let i = 0; i < period; i++) {
    if (changes[i] > 0) {
      avgGain += changes[i]
    } else {
      avgLoss += Math.abs(changes[i])
    }
  }
  avgGain /= period
  avgLoss /= period
  
  // Calculate RSI for each point
  for (let i = period; i < changes.length; i++) {
    const change = changes[i]
    const gain = change > 0 ? change : 0
    const loss = change < 0 ? Math.abs(change) : 0
    
    avgGain = (avgGain * (period - 1) + gain) / period
    avgLoss = (avgLoss * (period - 1) + loss) / period
    
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss
    const rsi = 100 - (100 / (1 + rs))
    
    // Scale RSI (0-100) to overlay on price chart by mapping to price range
    // Or store raw RSI value - for now we'll store raw for proper indicator display
    result.push({ time: data[i + 1].time, value: rsi })
  }
  
  return result
}

function updateIndicators(candles) {
  if (!chart) return
  
  // Calculate and update each active indicator on main chart
  if (activeIndicators.value.includes('ma20')) {
    const ma20Data = calculateSMA(candles, 20)
    if (ma20Series) ma20Series.setData(ma20Data)
  }
  
  if (activeIndicators.value.includes('ma50')) {
    const ma50Data = calculateSMA(candles, 50)
    if (ma50Series) ma50Series.setData(ma50Data)
  }
  
  if (activeIndicators.value.includes('ema12')) {
    const ema12Data = calculateEMA(candles, 12)
    if (ema12Series) ema12Series.setData(ema12Data)
  }
  
  if (activeIndicators.value.includes('ema26')) {
    const ema26Data = calculateEMA(candles, 26)
    if (ema26Series) ema26Series.setData(ema26Data)
  }
  
  // RSI is in separate chart
  if (activeIndicators.value.includes('rsi')) {
    const rsiData = calculateRSI(candles, 14)
    if (rsiChart && rsiSeries) {
      rsiSeries.setData(rsiData)
      // Sync time range with main chart
      if (candles.length > 0) {
        const timeScale = rsiChart.timeScale()
        const from = candles[0].time
        const to = candles[candles.length - 1].time
        timeScale.setVisibleRange({ from, to })
      }
    }
  }
}

async function toggleIndicator(indicatorId) {
  const index = activeIndicators.value.indexOf(indicatorId)
  if (index === -1) {
    // Add indicator
    activeIndicators.value.push(indicatorId)
    // Initialize RSI chart if needed
    if (indicatorId === 'rsi' && !rsiChart) {
      await nextTick()
      await initRsiChart()
      // Load current data into RSI chart
      const parts = chartPair.value.split('/')
      if (parts.length === 2) {
        const [from, to] = parts
        const result = await forexStore.fetchPairHistory(from, to, chartHistoryPeriod.value)
        const candles = result.candles || []
        if (candles.length > 0) {
          const rsiData = calculateRSI(candles, 14)
          if (rsiSeries) rsiSeries.setData(rsiData)
          if (rsiChart && candles.length > 0) {
            const timeScale = rsiChart.timeScale()
            timeScale.setVisibleRange({ from: candles[0].time, to: candles[candles.length - 1].time })
          }
        }
      }
    }
  } else {
    // Remove indicator
    activeIndicators.value.splice(index, 1)
  }
  
  // Update visibility for non-RSI indicators
  const seriesMap = {
    'ma20': ma20Series,
    'ma50': ma50Series,
    'ema12': ema12Series,
    'ema26': ema26Series
  }
  
  const series = seriesMap[indicatorId]
  if (series) {
    series.applyOptions({ visible: activeIndicators.value.includes(indicatorId) })
  }
}

async function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
  
  // Destroy existing charts
  if (chart) {
    chart.remove()
    chart = null
  }
  if (rsiChart) {
    rsiChart.remove()
    rsiChart = null
  }
  
  // Wait for DOM update
  await nextTick()
  
  // Reinitialize charts in new containers
  await initChart()
  
  // Reinitialize RSI chart if active
  if (activeIndicators.value.includes('rsi')) {
    await initRsiChart()
  }
  
  // Reload data into charts
  await loadChartData(false)
}


// ── Tabs ──────────────────────────────────────────────────────────────────
const activeTab = ref('exchange')

// ── Exchange form ─────────────────────────────────────────────────────────
const orderType   = ref('Market')
const targetPrice = ref(null)
const limitPrice  = ref(null)
const fromCurrency   = ref('USD')
const toCurrency     = ref('AUD')
const exchangeAmount = ref(null)
// currentRate is driven reactively by forexStore — no separate polling needed
const currentRate = computed(() => {
  if (fromCurrency.value === toCurrency.value) return null
  return forexStore.getRate(fromCurrency.value, toCurrency.value) ?? null
})
const receiveAmount  = ref(null)
const rateLoading    = computed(() => !currentRate.value && fromCurrency.value !== toCurrency.value && !forexStore.error)
const rateError      = ref('')
const tradeLoading   = ref(false)

/** Inline trade result: replaces Execute Trade until OK ({ message, variant }) */
const tradeFeedback = ref(null)

function showTradeFeedback(message, variant = 'success') {
  // Skip success card if the user turned off trade confirmations
  if (variant === 'success' && !tradeConfirmationsEnabled()) return
  tradeFeedback.value = { message, variant }
}

function formatApiDetail(detail, fallback) {
  if (detail == null || detail === '') return fallback
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((x) => (x && typeof x === 'object' && x.msg ? x.msg : String(x)))
      .join(' ')
  }
  return fallback
}

// ── Pending orders ────────────────────────────────────────────────────────
const pendingOrders  = ref([])
const ordersLoading  = ref(false)
const orderLoading   = ref(false)

async function loadOrders() {
  ordersLoading.value = true
  try {
    const { data } = await ordersApi.list()
    pendingOrders.value = data.orders || []
  } catch {
    // silently ignore
  } finally {
    ordersLoading.value = false
  }
}

async function placeOrder() {
  if (!exchangeAmount.value || exchangeAmount.value <= 0) {
    showTradeFeedback('Enter a positive amount.', 'error')
    return
  }
  if (!targetPrice.value || targetPrice.value <= 0) {
    showTradeFeedback('Enter a valid target price.', 'error')
    return
  }
  if (orderType.value === 'Stop-Limit') {
    if (!limitPrice.value || limitPrice.value <= 0) {
      showTradeFeedback('Enter a valid limit price.', 'error')
      return
    }
    if (limitPrice.value < targetPrice.value) {
      showTradeFeedback('Limit price must be ≥ stop price.', 'error')
      return
    }
  }
  orderLoading.value = true
  try {
    await ordersApi.place({
      from_currency: fromCurrency.value,
      to_currency:   toCurrency.value,
      amount:        exchangeAmount.value,
      order_type:    orderType.value,
      target_price:  targetPrice.value,
      limit_price:   orderType.value === 'Stop-Limit' ? limitPrice.value : null,
    })
    showTradeFeedback(
      `${orderType.value} order placed: ${exchangeAmount.value} ${fromCurrency.value} at target ${targetPrice.value} ${toCurrency.value}. It will fill automatically when the rate is hit.`,
      'success'
    )
    exchangeAmount.value = null
    targetPrice.value    = null
    limitPrice.value     = null
    await loadOrders()
  } catch (e) {
    showTradeFeedback(formatApiDetail(e.response?.data?.detail, 'Could not place order.'), 'error')
  } finally {
    orderLoading.value = false
  }
}

async function cancelOrder(orderId) {
  try {
    await ordersApi.cancel(orderId)
    await loadOrders()
  } catch {
    // silently ignore
  }
}

// ── Send form ─────────────────────────────────────────────────────────────
const transferEmail    = ref('')
const transferCurrency = ref('USD')
const transferAmount   = ref(null)
const transferLoading  = ref(false)

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
// currentRate is a computed from forexStore — no direct API call needed.
// This stub exists so callers (syncCurrenciesFromChart etc.) don't need refactoring.
function fetchRate() {
  if (fromCurrency.value === toCurrency.value) {
    rateError.value     = 'Cannot exchange a currency for itself.'
    receiveAmount.value = null
    return
  }
  rateError.value = ''
  computeReceive()
}

// Sync currencies from chart pair
function syncCurrenciesFromChart() {
  const [from, to] = chartPair.value.split('/')
  fromCurrency.value = from
  toCurrency.value = to
  fetchRate()
}

const CHART_REFRESH_INTERVAL_MS = 60_000  // Reload chart OHLC every 60s (candles don't change faster)

let chartRefreshTimer = null

// Initialize chart and watches on mount
onMounted(async () => {
  await fetchCurrencies()
  if (tradingPairs.value.length > 0 && !tradingPairs.value.includes(chartPair.value)) {
    chartPair.value = tradingPairs.value[0]
  }
  await initChart()
  await portfolioStore.fetchHoldings()
  loadHistory()
  loadOrders()
  fetchRate()

  // Initial chart data load
  await loadChartData(true)

  chartRefreshTimer = setInterval(() => loadChartData(false), CHART_REFRESH_INTERVAL_MS)
  
  // Watch for query parameter changes from wishlist navigation
  watch(() => route.query.pair, (newPair) => {
    if (newPair && newPair !== chartPair.value) {
      chartPair.value = newPair
      updateChartPair()
      syncCurrenciesFromChart()
    }
  }, { immediate: true })
  
  // Watch for chart pair changes — sync form + reload OHLC from API
  watch(chartPair, () => {
    syncCurrenciesFromChart()
    loadChartData(true) // Show loading when user changes pair
  })

  // Reset target/limit price when switching back to Market
  watch(orderType, (val) => {
    if (val === 'Market') {
      targetPrice.value = null
      limitPrice.value  = null
    }
  })

  // Subscribe to the active trading pair (trade form) so the rate poller covers it.
  watch(
    [fromCurrency, toCurrency],
    ([newFrom, newTo], [oldFrom, oldTo]) => {
      if (oldFrom && oldTo) forexStore.unsubscribePair(oldFrom, oldTo)
      if (newFrom && newTo && newFrom !== newTo) forexStore.subscribePair(newFrom, newTo)
    },
    { immediate: true }
  )

  // Also subscribe the chart pair so the live tick watcher gets updates even
  // when the chart pair differs from the trade form pair.
  watch(
    chartPair,
    (newPair, oldPair) => {
      if (oldPair) {
        const [f, t] = oldPair.split('/')
        if (f && t) forexStore.unsubscribePair(f, t)
      }
      if (newPair) {
        const [f, t] = newPair.split('/')
        if (f && t && f !== t) forexStore.subscribePair(f, t)
      }
    },
    { immediate: true }
  )
})

function computeReceive() {
  receiveAmount.value = (currentRate.value && exchangeAmount.value > 0)
    ? exchangeAmount.value * currentRate.value
    : null
}

// Keep receiveAmount in sync whenever rate or amount changes
watch([currentRate, exchangeAmount], computeReceive)

// Push a live tick to the chart every time forexStore delivers a fresh rate
watch(currentPrice, (liveRate) => {
  if (!liveRate) return
  const [from, to] = chartPair.value.split('/')
  const cached = forexStore.getCachedPairHistory(from, to, chartHistoryPeriod.value)
  if (cached?.candles?.length) _pushLiveTick(cached.candles)
})

// Swap pair direction and navigate to inverse pair
function swapPairDirection() {
  router.push(`/trading?pair=${toCurrency.value}/${fromCurrency.value}`)
}

async function executeTrade() {
  if (!exchangeAmount.value || exchangeAmount.value <= 0) {
    showTradeFeedback('Enter a positive amount.', 'error')
    return
  }
  if (fromCurrency.value === toCurrency.value) {
    showTradeFeedback('Cannot exchange a currency for itself.', 'error')
    return
  }
  tradeLoading.value = true
  try {
    const { data } = await tradeApi.exchange(fromCurrency.value, toCurrency.value, exchangeAmount.value)
    // Immediately reflect new balances — don't wait for the background poll
    portfolioStore.applyTradeOptimistic({
      fromCurrency:   data.from_currency,
      toCurrency:     data.to_currency,
      sentAmount:     data.sent_amount,
      receivedAmount: data.received_amount,
    })
    showTradeFeedback(
      `Sent ${data.sent_amount} ${data.from_currency}, received ${data.received_amount.toFixed(6)} ${data.to_currency} at rate ${data.rate.toFixed(6)}.`,
      'success'
    )
    exchangeAmount.value = null
    receiveAmount.value  = null
    // Reconcile with server in background — fire-and-forget
    portfolioStore.fetchHoldings()
    loadHistory()
  } catch (e) {
    showTradeFeedback(formatApiDetail(e.response?.data?.detail, 'Trade failed.'), 'error')
  } finally {
    tradeLoading.value = false
  }
}

// ── Transfer logic ────────────────────────────────────────────────────────
async function executeTransfer() {
  if (!transferEmail.value) {
    showTradeFeedback('Enter a recipient email.', 'error')
    return
  }
  if (!transferAmount.value || transferAmount.value <= 0) {
    showTradeFeedback('Enter a positive amount.', 'error')
    return
  }
  transferLoading.value = true
  try {
    const { data } = await tradeApi.transfer(transferEmail.value, transferCurrency.value, transferAmount.value)
    // Immediately debit the sent amount so the balance updates without waiting
    portfolioStore.applyTradeOptimistic({
      fromCurrency:   data.currency,
      toCurrency:     data.currency, // same currency — credit side is receiver's account
      sentAmount:     data.amount,
      receivedAmount: 0,
    })
    showTradeFeedback(`Sent ${data.amount} ${data.currency} to ${data.to_email}.`, 'success')
    transferAmount.value = null
    transferEmail.value = ''
    portfolioStore.fetchHoldings()
    loadHistory()
  } catch (e) {
    showTradeFeedback(formatApiDetail(e.response?.data?.detail, 'Transfer failed.'), 'error')
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
    case 'EXCHANGE': return 'bg-primary/20 text-primary border border-primary/40'
    case 'DEPOSIT':  return 'bg-green-500/20 text-green-400 border border-green-500/40'
    case 'WITHDRAW': return 'bg-red-500/20 text-red-400 border border-red-500/40'
    default:         return 'bg-gray-700/50 text-gray-400 border border-gray-600'
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

onUnmounted(() => {
  if (chartRefreshTimer) clearInterval(chartRefreshTimer)
  forexStore.unsubscribePair(fromCurrency.value, toCurrency.value)
  const [cpFrom, cpTo] = chartPair.value.split('/')
  if (cpFrom && cpTo) forexStore.unsubscribePair(cpFrom, cpTo)
  window.removeEventListener('resize', handleResize)
  document.body.style.overflow = ''
  
  if (chart) {
    chart.remove()
    chart = null
    candlestickSeries = null
    lineSeries = null
    areaSeries = null
    baselineSeries = null
    ma20Series = null
    ma50Series = null
    ema12Series = null
    ema26Series = null
  }
  if (rsiChart) {
    rsiChart.remove()
    rsiChart = null
    rsiSeries = null
  }
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

/* Trading Layout */
.trading-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 1024px) {
  .trading-layout {
    grid-template-columns: 1fr 350px;
  }
}

.chart-section {
  min-height: 500px;
}

.widgets-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

.widgets-sidebar > .glass {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.chart-container {
  width: 100%;
  height: 400px;
  position: relative;
  overflow: hidden;
}

.rsi-chart-container {
  width: 100%;
  height: 120px;
  position: relative;
  overflow: hidden;
}

/* Ensure chart canvas takes full width */
.chart-container > * {
  max-width: 100%;
}
</style>
