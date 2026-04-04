<template>
  <div
    ref="containerRef"
    class="tradingview-widget-container tv-stock-heatmap-root"
  >
    <div class="tradingview-widget-container__widget tv-stock-heatmap-widget" />
    <div class="tradingview-widget-copyright">
      <a
        href="https://www.tradingview.com/heatmap/stock/"
        rel="noopener nofollow"
        target="_blank"
      ><span class="blue-text">Stock Heatmap</span></a><span class="trademark"> by TradingView</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const HEATMAP_CONFIG = {
  dataSource: 'SPX500',
  blockSize: 'market_cap_basic',
  blockColor: 'change',
  grouping: 'sector',
  locale: 'en',
  symbolUrl: '',
  colorTheme: 'dark',
  exchanges: [],
  hasTopBar: false,
  isDataSetEnabled: false,
  isZoomEnabled: true,
  hasSymbolTooltip: true,
  isMonoSize: false,
  width: '100%',
  height: '100%',
}

const containerRef = ref(null)
let injectedScript = null

onMounted(() => {
  const el = containerRef.value
  if (!el) return

  const script = document.createElement('script')
  script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js'
  script.type = 'text/javascript'
  script.async = true
  script.innerHTML = JSON.stringify(HEATMAP_CONFIG)
  el.appendChild(script)
  injectedScript = script
})

onUnmounted(() => {
  if (injectedScript?.parentNode) {
    injectedScript.parentNode.removeChild(injectedScript)
  }
  injectedScript = null
})
</script>

<style scoped>
.tv-stock-heatmap-root {
  width: 100%;
  height: 100%;
  min-height: 0;
  position: relative;
  display: flex;
  flex-direction: column;
}

.tv-stock-heatmap-widget {
  width: 100%;
  flex: 1 1 auto;
  min-height: 0;
}

.tradingview-widget-copyright {
  flex-shrink: 0;
  font-size: 11px;
  line-height: 28px;
  text-align: center;
  color: #9ca3af;
  padding-top: 4px;
}

.tradingview-widget-copyright :deep(.blue-text) {
  color: #2962ff;
}

.tradingview-widget-copyright :deep(.blue-text:hover) {
  text-decoration: underline;
}

.tradingview-widget-copyright :deep(.trademark) {
  color: #6b7280;
}
</style>
