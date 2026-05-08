<template>
  <div class="container mx-auto px-0 py-0">
    <!-- <h1 class="text-6xl font-bold font-goldman text-primary mb-8">Dashboard</h1>
    
    <!-- Adaptive Bento Box Layout -->
    <div class="dashboard-grid">
      <!-- Left Column: Adaptive Widgets (Holdings/Wishlist/Feed) -->
      <div class="adaptive-widgets">
        <template v-for="widgetId in sideWidgets" :key="widgetId">
          <!-- Holdings Widget -->
          <div 
            v-if="widgetId === 'holdings'"
            @dragover.prevent="handleDragOver($event, 'holdings', 'side')"
            @drop="handleDrop($event, 'holdings', 'side')"
            :class="`glass rounded-xl hover:shadow-xl widget-card flex flex-col ${
              draggedWidget === 'holdings' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between p-6 pb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'holdings', 'side')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Holdings</h2>
              </div>
            </div>
            <div class="bg-bg-primary rounded-lg mx-6 p-3 flex-1 flex gap-0 overflow-hidden">
              <!-- Left: Donut Chart (30%) -->
              <div v-if="holdingsDonutData && portfolioStore.holdings.length > 0" class="flex-shrink-0 flex items-center justify-start pl-1 pr-2 border-r border-gray-700" style="width: 30%; min-width: 110px;">
                <div style="width: 100%; height: 140px;">
                  <Doughnut :data="holdingsDonutData" :options="holdingsDonutOptions" />
                </div>
              </div>
              
              <!-- Right: Holdings List (70%) - scrollable after 3 items -->
              <div class="flex-1 overflow-auto holdings-list-scroll pl-3">
                <div v-if="portfolioStore.loading && portfolioStore.holdings.length === 0" class="space-y-1.5">
                  <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
                  <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
                  <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
                </div>
                <div v-else-if="portfolioStore.error" class="flex items-center justify-center h-full text-red-400 text-sm">
                  {{ portfolioStore.error }}
                </div>
                <div v-else-if="portfolioStore.holdings.length === 0" class="flex items-center justify-center h-full text-gray-500 text-sm">
                  No holdings yet
                </div>
                <div v-else class="space-y-1.5">
                  <div
                    v-for="holding in portfolioStore.holdings"
                    :key="holding['currency-ticker-symbol'] || holding.currency"
                    class="flex justify-between items-center px-3 py-2.5 bg-bg-secondary rounded-lg hover:border-primary border border-transparent transition-all cursor-pointer group"
                  >
                    <div>
                      <p class="font-bold text-white text-sm group-hover:text-primary transition">{{ holding['currency-ticker-symbol'] || holding.currency }}</p>
                      <p class="text-xs text-gray-500 mt-0.5">{{ holding.currency || 'Currency' }}</p>
                    </div>
                    <div class="text-right">
                      <p class="font-mono text-white text-sm">{{ Number(holding.amount).toFixed(2) }}</p>
                      <p class="text-xs text-gray-500 mt-0.5">units</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Holdings Footer -->
            <div class="widget-footer">
              <p class="text-xs text-gray-400">{{ portfolioStore.holdings?.length || 0 }} currencies held</p>
            </div>
          </div>

          <!-- Wishlist Widget -->
          <div
            v-if="widgetId === 'wishlist'"
            @dragover.prevent="handleDragOver($event, 'wishlist', 'side')"
            @drop="handleDrop($event, 'wishlist', 'side')"
            :class="`glass rounded-xl hover:shadow-xl widget-card flex flex-col ${
              draggedWidget === 'wishlist' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between p-6 pb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'wishlist', 'side')"
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
            <div class="bg-bg-primary rounded-lg mx-6 p-3 flex-1 overflow-auto wishlist-scroll">
              <div v-if="portfolioStore.wishlist.length === 0" class="flex items-center justify-center py-8 text-gray-500 text-sm text-center px-2">
                No watchlist items yet. Add pairs from trading to track them here.
              </div>
              <div v-else class="space-y-1.5">
                <div
                  v-for="item in portfolioStore.wishlist"
                  :key="item.pair"
                  @click="goToTrading(item.pair)"
                  class="flex items-center justify-between px-3 py-2.5 bg-bg-secondary rounded-lg hover:border-primary border border-transparent transition-all cursor-pointer group"
                >
                  <div class="flex-1">
                    <p 
                      class="font-bold text-sm transition group-hover:text-primary"
                      :class="getWishlistChange(item.pair) >= 0 ? 'text-green-400' : 'text-red-400'"
                    >
                      {{ item.pair }}
                    </p>
                    <p class="text-xs text-gray-500 mt-0.5">{{ item.pair.split('/')[0] }} to {{ item.pair.split('/')[1] }}</p>
                  </div>
                  
                  <div class="mx-3 flex-shrink-0">
                    <svg width="60" height="20" class="mini-chart">
                      <path
                        v-if="getWishlistMiniPath(item.pair)"
                        :d="getWishlistMiniPath(item.pair)"
                        fill="none"
                        :stroke="getWishlistChange(item.pair) >= 0 ? '#10b981' : '#ef4444'"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </div>

                  <div class="text-right">
                    <p class="font-mono text-sm text-white">{{ getWishlistPrice(item.pair) }}</p>
                    <p class="text-xs font-semibold" :class="getWishlistChange(item.pair) >= 0 ? 'text-green-400' : 'text-red-400'">
                      {{ getWishlistChange(item.pair) >= 0 ? '+' : '' }}{{ getWishlistChange(item.pair).toFixed(2) }}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Wishlist Footer -->
            <div class="widget-footer">
              <p class="text-xs text-gray-400">{{ portfolioStore.wishlist.length }} pairs tracked</p>
            </div>
          </div>

          <!-- Feed Widget (r/economics) -->
          <div
            v-else-if="widgetId === 'feed'"
            @dragover.prevent="handleDragOver($event, 'feed', 'side')"
            @drop="handleDrop($event, 'feed', 'side')"
            :class="`glass rounded-xl hover:shadow-xl widget-card flex flex-col ${
              draggedWidget === 'feed' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between p-6 pb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'feed', 'side')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Economic News</h2>
              </div>
            </div>
            <div class="bg-bg-primary rounded-lg mx-6 p-3 flex-1 overflow-auto">
              <div v-if="feedItems.length === 0" class="flex items-center justify-center py-8 text-gray-500 text-sm text-center px-2">
                Loading news from r/economics...
              </div>
              <div v-else class="space-y-1.5">
                <a
                  v-for="item in feedItems"
                  :key="item.id"
                  :href="item.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="block px-3 py-2.5 bg-bg-secondary rounded-lg hover:border-primary border border-transparent transition-all cursor-pointer group"
                >
                  <p class="text-sm text-white font-medium group-hover:text-primary transition line-clamp-2">{{ item.title }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ item.time }}</p>
                </a>
              </div>
            </div>
            
            <!-- Feed Footer -->
            <div class="widget-footer">
              <p class="text-xs text-gray-400">r/economics</p>
            </div>
          </div>

        </template>
      </div>

      <!-- Right Column: Portfolio + Buying Power + Holdings -->
      <div class="left-column">
        <template v-for="widgetId in mainWidgets" :key="widgetId">
          <!-- Portfolio Widget -->
          <div 
            v-if="widgetId === 'portfolio'"
            @dragover.prevent="handleDragOver($event, 'portfolio', 'main')"
            @drop="handleDrop($event, 'portfolio', 'main')"
            :class="`portfolio-widget glass p-6 rounded-xl hover:shadow-xl widget-card ${
              draggedWidget === 'portfolio' ? 'dragging-placeholder' : ''
            }`"
          >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div
                draggable="true"
                @dragstart="handleDragStart($event, 'portfolio', 'main')"
                @dragend="handleDragEnd"
                class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
              >
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </div>
              <div>
                <h2 class="text-xl font-bold text-white">Portfolio Value</h2>
                <p class="text-2xl font-bold mt-0.5 text-white">
                  {{ totalPortfolioValue.toFixed(2) }} {{ defaultCurrency }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div class="flex flex-col gap-1">
                <p class="text-xs text-gray-500 italic">
                  Total value (all currencies converted to {{ defaultCurrency }})
                </p>
                <div v-if="portfolioStore.historyData?.total_deposited != null" class="flex items-center gap-3 text-xs">
                  <span class="text-gray-400">
                    Principal: <span class="font-mono text-gray-300">{{ usdToDisplay(portfolioStore.historyData.total_deposited).toFixed(2) }} {{ defaultCurrency }}</span>
                  </span>
                  <span class="text-gray-400">•</span>
                  <span :class="[
                    'font-semibold',
                    (portfolioStore.historyData.net_gain_loss || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                  ]">
                    Net: {{ (portfolioStore.historyData.net_gain_loss || 0) >= 0 ? '+' : '' }}{{ usdToDisplay(Math.abs(portfolioStore.historyData.net_gain_loss || 0)).toFixed(2) }} {{ defaultCurrency }}
                  </span>
                </div>
              </div>
              <div class="text-right">
                <p class="text-xs text-gray-500 mb-1">{{ selectedPeriodDisplayLabel }} change</p>
                <p class="text-lg font-bold" :class="portfolioChange >= 0 ? 'text-green-400' : 'text-red-400'">
                  {{ portfolioChange >= 0 ? '+' : '' }}{{ portfolioChange.toFixed(2) }}%
                </p>
              </div>
            </div>
          </div>

          <!-- Deposit Modal -->
          <Teleport to="body">
            <div v-if="showDepositModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="closeDeposit">
              <div class="bg-bg-secondary border border-gray-700 rounded-2xl p-6 w-full max-w-sm mx-4">
                <h3 class="text-xl font-bold text-white mb-1">Deposit Funds</h3>
                <p class="text-xs text-gray-500 mb-4">Deposits are added in your default currency (<span class="text-primary font-semibold">{{ defaultCurrency }}</span>). Change it in Settings → Preferences.</p>
                <div class="space-y-4">
                  <div>
                    <label class="text-sm text-gray-400 mb-1 block">Amount ({{ defaultCurrency }})</label>
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


          <div class="bg-bg-primary rounded-lg p-4 flex-1 flex flex-col overflow-hidden" style="min-height: 350px; max-height: 350px;">
            <!-- Chart Area -->
            <div v-if="portfolioStore.loading && !portfolioStore.historyData" class="flex items-center justify-center h-full">
              <div class="h-48 w-full bg-bg-secondary rounded-lg animate-pulse"></div>
            </div>
            <div v-else-if="portfolioStore.error" class="flex items-center justify-center h-full text-red-400 text-sm">
              {{ portfolioStore.error }}
            </div>
            <div v-else-if="portfolioStore.holdings.length === 0" class="flex items-center justify-center h-full text-gray-500 text-sm">
              No holdings yet. Deposit funds to get started.
            </div>
            <div v-else class="relative flex flex-col justify-center items-center h-full w-full" style="padding-right: 1rem;">
              <!-- Loading overlay (only shown during refresh, not initial load) -->
              <div v-if="portfolioStore.historyLoading && portfolioStore.historyData" class="absolute inset-0 flex items-center justify-center bg-bg-primary/60 z-10 rounded-lg">
                <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
              </div>
              <!-- History error -->
              <div v-if="portfolioStore.historyError" class="absolute top-0 left-0 right-0 text-center text-red-400 text-xs py-1">
                {{ portfolioStore.historyError }}
              </div>
              <!-- Portfolio Line Chart -->
              <div class="w-full h-full flex items-center justify-center">
                <Line
                  :data="portfolioLineChartData"
                  :options="portfolioLineChartOptions"
                />
              </div>
            </div>
            
            <!-- Controls: Timeline Slider (left) + Total/Relative Toggle (right) -->
            <div class="flex items-center justify-between px-4 py-2 flex-shrink-0">
              <!-- Left: Timeline Slider -->
              <div class="w-80 pl-0 pr-4">
                <div class="relative">
                  <div class="absolute top-1/2 -translate-y-1/2 w-full h-0.5 bg-gray-700"></div>
                  <div class="relative flex justify-between items-center">
                    <button
                      v-for="period in periods"
                      :key="period.value"
                      @click="selectPeriod(period.value)"
                      :disabled="isPeriodDisabled(period.value)"
                      class="relative flex flex-col items-center group"
                      :title="isPeriodDisabled(period.value) ? 'Not enough transaction history' : `${period.label} - ${getPeriodDateLabel(period.value)}`"
                    >
                      <div :class="[
                        'w-3 h-3 rounded-full border-2 transition-all z-10',
                        isPeriodDisabled(period.value)
                          ? 'bg-gray-800 border-gray-700 cursor-not-allowed opacity-40'
                          : portfolioStore.selectedPeriod === period.value
                            ? 'bg-primary border-primary scale-125 shadow-lg shadow-primary/50 cursor-pointer'
                            : 'bg-bg-primary border-gray-600 group-hover:border-primary group-hover:scale-110 cursor-pointer'
                      ]"></div>
                      <span :class="[
                        'absolute top-5 text-xs font-semibold whitespace-nowrap transition-all',
                        isPeriodDisabled(period.value)
                          ? 'text-gray-700'
                          : portfolioStore.selectedPeriod === period.value
                            ? 'text-primary'
                            : 'text-gray-500 group-hover:text-gray-300'
                      ]">
                        {{ period.label }}
                      </span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Right: Total/Relative Toggle -->
              <div class="flex gap-2 flex-shrink-0">
                <button
                  @click="portfolioChartMode = 'total'"
                  :class="[
                    'px-2 py-1.5 rounded-lg text-xs font-bold transition-all border-2',
                    portfolioChartMode === 'total'
                      ? 'bg-green-600 border-green-600 text-white'
                      : 'bg-bg-primary text-gray-400 border-gray-700 hover:text-white hover:border-gray-600'
                  ]"
                  title="Total Portfolio Value"
                >
                  TOTAL
                </button>
                <button
                  @click="portfolioChartMode = 'relative'"
                  :class="[
                    'px-2 py-1.5 rounded-lg text-xs font-bold transition-all border-2',
                    portfolioChartMode === 'relative'
                      ? 'bg-green-600 border-green-600 text-white'
                      : 'bg-bg-primary text-gray-400 border-gray-700 hover:text-white hover:border-gray-600'
                  ]"
                  title="Relative Percentage Change"
                >
                  RELATIVE
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Buying Power Widget -->
        <div 
          v-if="widgetId === 'buyingPower'"
          @dragover.prevent="handleDragOver($event, 'buyingPower', 'main')"
          @drop="handleDrop($event, 'buyingPower', 'main')"
          :class="`glass p-4 rounded-xl hover:shadow-xl widget-card ${
            draggedWidget === 'buyingPower' ? 'dragging-placeholder' : ''
          }`"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div
                draggable="true"
                @dragstart="handleDragStart($event, 'buyingPower', 'main')"
                @dragend="handleDragEnd"
                class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
              >
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </div>
              <div>
                <p class="text-xs text-gray-400 mb-1">Buying Power <span class="text-gray-600">({{ defaultCurrency }})</span></p>
                <p class="text-xl font-bold text-white">{{ buyingPower.toFixed(2) }} {{ defaultCurrency }}</p>
              </div>
            </div>
            <div class="flex gap-2">
              <button 
                @click="showDepositModal = true"
                class="px-4 py-2 bg-gradient-to-r from-primary to-primary/80 text-black font-bold rounded-lg hover:shadow-lg hover:shadow-primary/30 transition-all text-sm"
              >
                Deposit
              </button>
            </div>
          </div>
        </div>

        <!-- Holdings Widget (Main Column) -->
        <div 
          v-if="widgetId === 'holdingsMain'"
          @dragover.prevent="handleDragOver($event, 'holdingsMain', 'main')"
          @drop="handleDrop($event, 'holdingsMain', 'main')"
          :class="`glass p-6 rounded-xl hover:shadow-xl widget-card flex flex-col ${
            draggedWidget === 'holdingsMain' ? 'dragging-placeholder' : ''
          }`"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <div
                draggable="true"
                @dragstart="handleDragStart($event, 'holdingsMain', 'main')"
                @dragend="handleDragEnd"
                class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
              >
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </div>
              <h2 class="text-xl font-bold text-white">Holdings</h2>
            </div>
          </div>
          
          <div class="bg-bg-primary rounded-lg p-4 flex-1 flex gap-0 overflow-hidden">
            <!-- Left: Donut Chart (30%) -->
            <div v-if="holdingsDonutData && portfolioStore.holdings.length > 0" class="flex-shrink-0 flex items-center justify-start pl-1 pr-2 border-r border-gray-700" style="width: 30%; min-width: 110px;">
              <div style="width: 100%; height: 140px;">
                <Doughnut :data="holdingsDonutData" :options="holdingsDonutOptions" />
              </div>
            </div>
            
            <!-- Right: Holdings List (70%) - scrollable after 3 items -->
            <div class="flex-1 overflow-auto holdings-list-scroll pl-3">
              <div v-if="portfolioStore.loading && portfolioStore.holdings.length === 0" class="space-y-1.5">
                <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
                <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
                <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
              </div>
              <div v-else-if="portfolioStore.error" class="flex items-center justify-center h-full text-red-400 text-sm">
                {{ portfolioStore.error }}
              </div>
              <div v-else-if="portfolioStore.holdings.length === 0" class="flex items-center justify-center h-full text-gray-500 text-sm">
                No holdings yet
              </div>
              <div v-else class="space-y-1.5">
                <div
                  v-for="holding in portfolioStore.holdings"
                  :key="holding['currency-ticker-symbol'] || holding.currency"
                  class="flex justify-between items-center px-3 py-2.5 bg-bg-secondary rounded-lg hover:border-primary border border-transparent transition-all cursor-pointer group"
                >
                  <div>
                    <p class="font-bold text-white text-sm group-hover:text-primary transition">{{ holding['currency-ticker-symbol'] || holding.currency }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">{{ holding.currency || 'Currency' }}</p>
                  </div>
                  <div class="text-right">
                    <p class="font-mono text-white text-sm">{{ Number(holding.amount).toFixed(2) }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">units</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Holdings Footer -->
          <div class="widget-footer">
            <p class="text-xs text-gray-400">{{ portfolioStore.holdings?.length || 0 }} currencies held</p>
          </div>
        </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usePortfolioStore } from '@/stores/portfolio'
import { useForexStore } from '@/stores/forex'
import { usePrefsStore } from '@/stores/prefs'
import { useAuthStore } from '@/stores/auth'
import { fetchEconomicsPosts } from '@/composables/useReddit'
import {
  startOfLocalDayMs,
  endOfLocalDayMs,
  buildPortfolioSeriesUsd,
  portfolioHistoryBaselineUsd
} from '@/utils/portfolioSeries'
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
)

const router = useRouter()
const portfolioStore = usePortfolioStore()
const forexStore = useForexStore()
const prefsStore = usePrefsStore()
const authStore = useAuthStore()

// ── Currencies ───────────────────────────────────────────────────────────
// Use forex store currencies instead of fetching directly
const currencies = computed(() => forexStore.currencies)

async function fetchCurrencies() {
  // No-op: currencies come from forex store pipeline
}

// Date range periods for the chart selector
const periods = [
  { label: '1D', value: '1d' },
  { label: '1W', value: '1wk' },
  { label: '1M', value: '1mo' },
  { label: '3M', value: '3mo' },
  { label: 'YTD', value: 'ytd' },
  { label: '1Y', value: '1y' },
  { label: '5Y', value: '5y' },
]

// Calculate if a period should be disabled based on first transaction date
const isPeriodDisabled = computed(() => {
  return (periodValue) => {
    if (!portfolioStore.firstTransactionDate) return false
    
    const firstTxDate = new Date(portfolioStore.firstTransactionDate)
    const now = new Date()
    const daysSinceFirstTx = Math.floor((now - firstTxDate) / (1000 * 60 * 60 * 24))
    
    switch (periodValue) {
      case '1d':
        return daysSinceFirstTx < 1
      case '1wk':
        return daysSinceFirstTx < 7
      case '1mo':
        return daysSinceFirstTx < 30
      case '3mo':
        return daysSinceFirstTx < 90
      case 'ytd':
        return firstTxDate.getFullYear() > now.getFullYear()
      case '1y':
        return daysSinceFirstTx < 365
      case '5y':
        return daysSinceFirstTx < 365 * 5
      default:
        return false
    }
  }
})

function selectPeriod(period) {
  if (!isPeriodDisabled.value(period)) {
    portfolioStore.fetchHistory(period, true)
  }
}

// Get date label for timeline periods
function getPeriodDateLabel(periodValue) {
  const now = new Date()
  const targetDate = new Date()
  
  switch (periodValue) {
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
    case 'ytd':
      return 'Jan 1, ' + now.getFullYear()
    case '1y':
      targetDate.setFullYear(now.getFullYear() - 1)
      return targetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    case '5y':
      targetDate.setFullYear(now.getFullYear() - 5)
      return targetDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    default:
      return ''
  }
}

const selectedPeriodDisplayLabel = computed(() => {
  const p = periods.find((x) => x.value === portfolioStore.selectedPeriod)
  return p?.label ?? 'Period'
})

/** Total = USD value; Relative = % change from first point in range (today’s first bar for 1D). */
const portfolioChartMode = ref('total')

// Reactive display currency driven by user preferences (Settings → Preferences)
const defaultCurrency = computed(() => prefsStore.displayCurrency)

// Holdings donut chart data
const holdingsDonutData = computed(() => {
  const holdings = portfolioStore.holdings
  if (!holdings || holdings.length === 0) return null
  
  // Calculate USD value for each holding
  const holdingsWithValue = holdings.map(h => {
    const ticker = h['currency-ticker-symbol'] || h.currency
    const amount = Number(h.amount)
    const rate = forexStore.getRate(ticker, defaultCurrency.value)
    const value = amount * (rate || 1)
    return { ticker, amount, value }
  })
  
  const total = holdingsWithValue.reduce((sum, h) => sum + h.value, 0)
  
  // Generate colors matching currency theme (gold, silver, bronze, jewel tones)
  const colors = [
    '#fbbf24', // gold
    '#9ca3af', // silver
    '#cd7f32', // bronze/copper
    '#10b981', // emerald
    '#3b82f6', // sapphire blue
    '#a855f7', // amethyst purple
    '#06b6d4', // aquamarine
    '#ef4444', // ruby red
  ]
  
  return {
    labels: holdingsWithValue.map(h => h.ticker),
    datasets: [{
      data: holdingsWithValue.map(h => ((h.value / total) * 100).toFixed(1)),
      backgroundColor: colors.slice(0, holdingsWithValue.length),
      borderColor: '#0a0a14',
      borderWidth: 2
    }]
  }
})

const holdingsDonutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          return `${context.label}: ${context.parsed}%`
        }
      }
    }
  },
  cutout: '65%'
}

const PORTFOLIO_REFRESH_INTERVAL_MS = 15_000  // Holdings rarely change mid-session
let portfolioRefreshTimer = null

// Track which pairs we've subscribed so we can unsubscribe on unmount
let _subscribedPairs = []

function _syncForexSubscriptions() {
  // Unsubscribe stale pairs
  _subscribedPairs.forEach(([f, t]) => forexStore.unsubscribePair(f, t))
  _subscribedPairs = []

  const display = defaultCurrency.value || 'USD'

  // Always subscribe USD→displayCurrency for portfolio value conversion
  if (display !== 'USD') {
    forexStore.subscribePair('USD', display)
    _subscribedPairs.push(['USD', display])
  }

  // Subscribe each held currency → displayCurrency for per-holding values
  portfolioStore.holdings.forEach(h => {
    const ticker = h['currency-ticker-symbol'] || h.currency
    if (ticker && ticker !== display) {
      forexStore.subscribePair(ticker, display)
      _subscribedPairs.push([ticker, display])
    }
  })

  // Subscribe each wishlist pair so getWishlistPrice() gets live rates
  portfolioStore.wishlist.forEach(({ pair }) => {
    const [f, t] = pair.split('/')
    if (f && t && f !== t) {
      forexStore.subscribePair(f, t)
      _subscribedPairs.push([f, t])
    }
  })
}

onMounted(async () => {
  prefsStore.load(authStore.userId)

  await portfolioStore.fetchHoldings()
  _syncForexSubscriptions()

  portfolioStore.fetchHistory('1mo')
  portfolioStore.fetchFirstTransactionDate()
  loadWishlistSparklines()
  loadFeedNews()

  portfolioRefreshTimer = setInterval(async () => {
    const result = await portfolioStore.fetchHoldings()
    if (result?.holdingsChanged) {
      _syncForexSubscriptions()
      portfolioStore.fetchHistory(portfolioStore.selectedPeriod, true)
      // News is cached for 30 min — do NOT re-fetch on every holdings refresh
    }
  }, PORTFOLIO_REFRESH_INTERVAL_MS)
})

onUnmounted(() => {
  if (portfolioRefreshTimer) clearInterval(portfolioRefreshTimer)
  _subscribedPairs.forEach(([f, t]) => forexStore.unsubscribePair(f, t))
  _subscribedPairs = []
})

// Watch wishlist changes to reload sparklines
watch(
  () => portfolioStore.wishlist.map((w) => w.pair).join('|'),
  () => {
    loadWishlistSparklines()
    _syncForexSubscriptions()
  }
)

// Navigation function
const goToTrading = (symbol) => {
  router.push({ path: '/trading', query: { pair: symbol } })
}

function datasetStyleForMode(mode) {
  return {
    label: mode === 'relative' ? 'Change from start of range (%)' : 'Portfolio Value (USD)',
    borderColor: 'rgba(255, 215, 0, 1)',
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    borderWidth: 2,
    tension: 0.4,
    fill: true,
    pointRadius: 0,
    pointHoverRadius: 6,
    pointBackgroundColor: 'rgba(255, 215, 0, 1)',
    pointBorderColor: '#1a1a1a',
    pointBorderWidth: 2
  }
}

/** % change from baseline; baseline is first sample in the visible series. */
function toRelativePercentPoints(points, baselineUsd) {
  if (baselineUsd == null || baselineUsd === 0) return points
  return points.map((p) => ({
    ...p,
    y: ((p.y / baselineUsd) - 1) * 100
  }))
}

// Portfolio Line Chart Data — same USD series as headline (buildPortfolioSeriesUsd)
const portfolioLineChartData = computed(() => {
  const history = portfolioStore.historyData
  const period = portfolioStore.selectedPeriod
  const mode = portfolioChartMode.value
  const ds = datasetStyleForMode(mode)

  const series = buildPortfolioSeriesUsd(history, period)

  if (series.type === 'empty') {
    return {
      labels: [],
      datasets: [{
        ...ds,
        borderColor: 'rgba(255, 215, 0, 0.3)',
        backgroundColor: 'rgba(255, 215, 0, 0.05)',
        data: []
      }]
    }
  }

  if (series.type === 'xy') {
    let data = [...series.data]
    const baseline = portfolioHistoryBaselineUsd(history, period)
    if (mode === 'relative' && baseline != null && baseline !== 0) {
      data = toRelativePercentPoints(data, baseline)
    }
    return {
      datasets: [{ ...ds, data }]
    }
  }

  let data = [...series.data]
  const baseline = portfolioHistoryBaselineUsd(history, period)
  if (mode === 'relative' && baseline != null && baseline !== 0) {
    data = data.map((v) => ((v / baseline) - 1) * 100)
  }

  return {
    labels: series.labels,
    datasets: [{ ...ds, data }]
  }
})

const portfolioLineChartOptions = computed(() => {
  const period = portfolioStore.selectedPeriod
  const mode = portfolioChartMode.value
  const history = portfolioStore.historyData
  const baseline = portfolioHistoryBaselineUsd(history, period)
  const relative =
    mode === 'relative' && baseline != null && baseline !== 0
  const dayStart = startOfLocalDayMs()
  const dayEnd = endOfLocalDayMs()

  const yTickUsd = function (value) {
    return '$' + (value / 1000).toFixed(1) + 'k'
  }
  const yTickPct = function (value) {
    const v = Number(value)
    const s = (v >= 0 ? '+' : '') + v.toFixed(2) + '%'
    return s
  }

  const yScaleBase = {
    grid: {
      color: 'rgba(255, 255, 255, 0.05)',
      drawBorder: false
    },
    ticks: {
      color: relative ? '#9ca3af' : '#6b7280',
      font: {
        size: 11
      },
      callback: relative ? yTickPct : yTickUsd
    }
  }

  const base = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 215, 0, 0.5)',
        borderWidth: 1,
        displayColors: false,
        callbacks: {
          title: (items) => {
            if (!items.length) return ''
            const ctx = items[0]
            if (period === '1d' && ctx.parsed.x != null) {
              return new Date(ctx.parsed.x).toLocaleString('en-US', {
                weekday: 'short',
                hour: 'numeric',
                minute: '2-digit'
              })
            }
            return ctx.label || ''
          },
          label: (context) => {
            const y = context.parsed.y
            if (y == null || Number.isNaN(Number(y))) return ''

            const b = baseline
            let usd
            let pct = null

            if (relative) {
              pct = Number(y)
              usd =
                b != null && b !== 0 && Number.isFinite(pct)
                  ? b * (1 + pct / 100)
                  : null
            } else {
              usd = Number(y)
              pct =
                b != null && b !== 0 && usd != null && Number.isFinite(usd)
                  ? (usd / b - 1) * 100
                  : null
            }

            const usdStr =
              usd != null && Number.isFinite(usd)
                ? '$' +
                  usd.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })
                : null

            const lines = []
            if (usdStr) lines.push(usdStr)
            if (pct != null && Number.isFinite(pct)) {
              lines.push((pct >= 0 ? '+' : '') + pct.toFixed(2) + '%')
            }

            if (lines.length === 0) return ''
            return lines.length === 1 ? lines[0] : lines
          }
        }
      }
    },
    scales: {
      y: yScaleBase
    },
    interaction: {
      intersect: false,
      mode: period === '1d' ? 'nearest' : 'index'
    }
  }

  if (period === '1d') {
    return {
      ...base,
      scales: {
        ...base.scales,
        x: {
          type: 'linear',
          min: dayStart,
          max: dayEnd,
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            color: '#6b7280',
            font: { size: 10 },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 7,
            callback: (value) =>
              typeof value === 'number'
                ? new Date(value).toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit'
                  })
                : value
          }
        },
        y: yScaleBase
      }
    }
  }

  return {
    ...base,
    scales: {
      ...base.scales,
      x: {
        grid: {
          display: false,
          drawBorder: false
        },
        ticks: {
          color: '#6b7280',
          font: {
            size: 10
          },
          maxRotation: 0,
          autoSkipPadding: 20
        }
      },
      y: yScaleBase
    }
  }
})

/** Convert a USD amount to the user's chosen display currency. */
function usdToDisplay(usdAmount) {
  const cur = defaultCurrency.value
  if (!cur || cur === 'USD') return usdAmount
  // The rate key is e.g. "USDEUR" meaning 1 USD = X EUR
  const rate = forexStore.getRate('USD', cur)
  return rate ? usdAmount * rate : usdAmount
}

function sumHoldingsAmountFallback() {
  if (!portfolioStore.holdings?.length) return 0
  // Sum each holding converted to defaultCurrency
  return portfolioStore.holdings.reduce((sum, h) => {
    const ticker = h['currency-ticker-symbol'] || h.currency
    const amount = Number(h.amount)
    const rate = forexStore.getRate(ticker, defaultCurrency.value)
    return sum + amount * (rate || 1)
  }, 0)
}

/** Same series as chart: last USD point = headline value; % vs first point in range. */
const portfolioHeadlineMetrics = computed(() => {
  const history = portfolioStore.historyData
  const period = portfolioStore.selectedPeriod
  const s = buildPortfolioSeriesUsd(history, period)
  if (s.type === 'empty') {
    return { value: sumHoldingsAmountFallback(), changePct: 0 }
  }
  const first = s.type === 'xy' ? s.data[0]?.y : s.data[0]
  const last =
    s.type === 'xy' ? s.data[s.data.length - 1]?.y : s.data[s.data.length - 1]
  if (first == null || last == null) {
    return { value: sumHoldingsAmountFallback(), changePct: 0 }
  }
  return {
    value: usdToDisplay(last),
    changePct: first !== 0 ? ((last - first) / first) * 100 : 0
  }
})

const totalPortfolioValue = computed(() => portfolioHeadlineMetrics.value.value)

const portfolioChange = computed(() => portfolioHeadlineMetrics.value.changePct)

/** Amount of the defaultCurrency the user currently holds — this is their cash buying power. */
const buyingPower = computed(() => {
  const cur = defaultCurrency.value
  if (!cur || !portfolioStore.holdings?.length) return 0
  const holding = portfolioStore.holdings.find(
    h => (h['currency-ticker-symbol'] || h.currency) === cur
  )
  return holding ? Number(holding.amount) : 0
})

// Populated when watchlist / activity APIs exist; empty = no mock data
const wishlistItems = ref([])
const feedItems = ref([])

// Wishlist sparklines (mini charts)
const wishlistSparklines = ref({})  // { 'USD/EUR': { closes: [...], change1d: 0.5 } }

function getCloses1d(candles) {
  if (!candles?.length) return []
  return candles.map((c) => c.close).filter((n) => n > 0 && Number.isFinite(n))
}

function getChange1d(candles) {
  if (!candles?.length || candles.length < 2) return 0
  const first = candles[0].close
  const last = candles[candles.length - 1].close
  if (!first || first === 0) return 0
  return ((last - first) / first) * 100
}

function getMiniChartPath(data) {
  if (!data || data.length < 2) return ''
  const width = 60
  const height = 20
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

async function loadWishlistSparklines() {
  if (portfolioStore.wishlist.length === 0) return
  const pairs = portfolioStore.wishlist.map((w) => w.pair)
  const next = { ...wishlistSparklines.value }
  await Promise.all(
    pairs.map(async (pair) => {
      const parts = pair.split('/')
      if (parts.length !== 2) return
      const [f, t] = parts
      const cached = forexStore.getCachedPairHistory(f, t, '1d')
      const candles = cached?.candles || []
      if (candles.length > 0) {
        next[pair] = {
          closes: getCloses1d(candles),
          change1d: getChange1d(candles)
        }
      } else {
        const result = await forexStore.fetchPairHistory(f, t, '1d')
        const newCandles = result.candles || []
        next[pair] = {
          closes: getCloses1d(newCandles),
          change1d: getChange1d(newCandles)
        }
      }
    })
  )
  wishlistSparklines.value = next
}

function getWishlistMiniPath(pair) {
  const data = wishlistSparklines.value[pair]
  return getMiniChartPath(data?.closes || [])
}

function getWishlistChange(pair) {
  const data = wishlistSparklines.value[pair]
  return data?.change1d || 0
}

function getWishlistPrice(pair) {
  const [from, to] = pair.split('/')
  const rate = forexStore.getRate(from, to)
  return rate ? rate.toFixed(4) : '—'
}

// Load economic news feed from r/economics
async function loadFeedNews() {
  try {
    const posts = await fetchEconomicsPosts(5)
    feedItems.value = posts.slice(0, 5).map(post => ({
      id: post.id,
      title: post.title,
      time: post.time,
      url: post.url
    }))
  } catch (err) {
    console.error('Failed to load economics feed:', err)
    feedItems.value = []
  }
}

// Deposit modal state
const showDepositModal = ref(false)
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
    await portfolioStore.deposit(defaultCurrency.value, depositAmount.value)
    closeDeposit()
  } catch (e) {
    depositError.value = e.response?.data?.detail || 'Deposit failed.'
  } finally {
    depositLoading.value = false
  }
}

// Main column and side widgets can be reordered independently
const mainWidgets = ref(['portfolio', 'buyingPower', 'holdingsMain'])
const sideWidgets = ref(['holdings', 'wishlist', 'feed'])
const draggedWidget = ref(null)
const draggedColumn = ref(null)

const handleDragStart = (event, widgetId, column) => {
  draggedWidget.value = widgetId
  draggedColumn.value = column
  event.dataTransfer.effectAllowed = 'move'
}

const handleDragOver = (event, widgetId, column) => {
  event.preventDefault()
  
  // Only allow drag within the same column
  if (!draggedWidget.value || draggedColumn.value !== column) {
    return
  }
  
  if (draggedWidget.value === widgetId) return
  
  const widgets = column === 'main' ? mainWidgets : sideWidgets
  
  // Live reorder widgets
  const newOrder = [...widgets.value]
  const dragIndex = newOrder.indexOf(draggedWidget.value)
  const dropIndex = newOrder.indexOf(widgetId)
  
  if (dragIndex === -1 || dropIndex === -1) return
  
  // Remove from current position
  newOrder.splice(dragIndex, 1)
  
  // Insert at new position
  newOrder.splice(dropIndex, 0, draggedWidget.value)
  
  widgets.value = newOrder
}

const handleDrop = (event, widgetId, column) => {
  event.preventDefault()
  
  // Save to localStorage
  if (column === 'main') {
    localStorage.setItem('mainWidgetOrder', JSON.stringify(mainWidgets.value))
  } else {
    localStorage.setItem('sideWidgetOrder', JSON.stringify(sideWidgets.value))
  }
  
  draggedWidget.value = null
  draggedColumn.value = null
}

const handleDragEnd = () => {
  draggedWidget.value = null
  draggedColumn.value = null
}

// Load saved state
const savedMainOrder = localStorage.getItem('mainWidgetOrder')
if (savedMainOrder) {
  try {
    mainWidgets.value = JSON.parse(savedMainOrder)
  } catch (e) {
    console.error('Failed to load main widget order', e)
  }
}

const savedSideOrder = localStorage.getItem('sideWidgetOrder')
if (savedSideOrder) {
  try {
    sideWidgets.value = JSON.parse(savedSideOrder)
  } catch (e) {
    console.error('Failed to load side widget order', e)
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
    grid-template-columns: 1fr 2fr;
    grid-template-rows: auto;
    gap: 1rem;
  }
  
  .left-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    order: 2;
  }
  
  .adaptive-widgets {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    order: 1;
  }
  
  .portfolio-widget {
    min-height: 480px;
    max-height: 480px;
    display: flex;
    flex-direction: column;
  }
  
  .adaptive-widgets > div {
    flex: 1;
    min-height: 190px;
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

/* Widget Footers */
.portfolio-footer,
.widget-footer {
  padding: 1rem 1.5rem;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0 0 0.75rem 0.75rem;
  margin-top: auto;
}

.portfolio-widget {
  display: flex;
  flex-direction: column;
}

.portfolio-widget > div:first-child {
  flex: 1;
}

/* Holdings list scroll - max height for 3 items then scroll */
.holdings-list-scroll {
  max-height: calc(3 * (48px + 6px));
}

.holdings-list-scroll::-webkit-scrollbar {
  width: 6px;
}

.holdings-list-scroll::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.holdings-list-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.holdings-list-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Wishlist scroll styles */
.wishlist-scroll {
  max-height: 400px;
}

.wishlist-scroll::-webkit-scrollbar {
  width: 6px;
}

.wishlist-scroll::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.wishlist-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.wishlist-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
