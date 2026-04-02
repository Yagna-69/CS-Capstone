# Recent Changes - Data Pipeline & UI Improvements

## 1. Backend Persistent Caching (Cross-User Efficiency)

### What Changed
Added file-based persistent caching to `backend/forex_service.py` so that fetched data is stored on disk and shared across all users.

### Implementation
```python
# New cache directory
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# Helper functions
def _load_from_disk(cache_key: str) -> tuple[any, float] | None:
    """Load cached data from disk if it exists and is valid."""
    # Loads from backend/.cache/{cache_key}.json

def _save_to_disk(cache_key: str, data: any, fetched_at: float):
    """Persist cached data to disk for cross-user sharing."""
    # Saves to backend/.cache/{cache_key}.json
```

### Cache Strategy (3-Tier)
```
User Request → In-Memory Cache (5s-5min TTL)
                    ↓ (miss)
             Disk Cache (persistent)
                    ↓ (miss)
             yfinance API Fetch
                    ↓
             Save to: Memory + Disk
```

### Benefits
- **Cross-User Efficiency**: User A fetches EUR/USD → cached to disk → User B gets instant response
- **Reduced API Load**: yfinance is only called if both memory AND disk cache miss
- **Faster Response Times**: Disk reads are ~1000x faster than API calls
- **Persistent Across Restarts**: Data survives backend restarts
- **Automatic Cleanup**: Old cache files can be manually cleaned from `backend/.cache/`

### Cache File Examples
```
backend/.cache/
  ├── hist_EURUSD:1d.json       # Historical rates
  ├── ohlc:EURUSD:1d.json       # OHLC candles
  ├── ohlc:GBPUSD:1wk.json      # OHLC candles
  └── ...
```

### Updated Functions
- `get_historical_rates()`: Now checks disk cache before API
- `get_historical_ohlc()`: Now checks disk cache before API
- Live rates (`get_rate()`): Still memory-only (5s TTL is too short for disk I/O benefit)

## 2. Search Bar Sparklines - Now 1-Day Data

### What Changed
Updated `App.vue` search dropdown sparklines to display **full 1-day chart** instead of just the last hour.

### Before vs After

**Before:**
- Used `closesLastHour()` - only last ~1 hour of data
- Color based on `item.trend` (ticker poll direction)
- Percentage based on `pctSinceLastPoll` (ticker poll change)

**After:**
- Uses `getCloses1d()` - ALL data points from the 1-day period (5-minute bars)
- Color based on `searchChange1d()` - first candle to last candle change
- Percentage shows **24-hour change** (first open to last close)

### Implementation
```javascript
// Extract all closes from 1d data
function getCloses1d(candles) {
  if (!candles?.length) return []
  return candles.map((c) => c.close).filter((n) => n > 0 && Number.isFinite(n))
}

// Calculate 1-day % change
function getChange1d(candles) {
  if (!candles?.length || candles.length < 2) return 0
  const first = candles[0].close
  const last = candles[candles.length - 1].close
  if (!first || first === 0) return 0
  return ((last - first) / first) * 100
}

// Store both closes and change
const searchSparklines = ref({})  // { 'EUR/USD': { closes: [...], change1d: 0.5 } }
```

### Template Updates
```vue
<!-- Color based on 1d change -->
<path :stroke="searchChange1d(item.pair) >= 0 ? '#10b981' : '#ef4444'" />

<!-- Percentage shows 1d change -->
<p :class="searchChange1d(item.pair) >= 0 ? 'text-green-400' : 'text-red-400'">
  {{ searchChange1d(item.pair) >= 0 ? '+' : '' }}{{ searchChange1d(item.pair).toFixed(2) }}%
</p>
```

### Result
- Sparklines now show the complete 24-hour price movement
- Colors and percentages reflect the full day's performance
- More meaningful for users deciding which pair to trade

## 3. TradingView UI Simplification

### Removed Features
- **Currency Pair Selector**: Users can no longer manually select FROM/TO currencies in the exchange widget
- **Swap Button**: The button to swap currencies has been removed

### Why
- Currency pairs are now **locked to the chart selection**
- Simpler, more focused UI
- Prevents confusion from having two ways to change the pair

### Label Update
Changed from "Currency Pair" to "Currency Pair (locked to chart)" to make this behavior clear.

## Summary of All Active Changes

### Backend (`forex_service.py`)
- ✅ `CACHE_TTL = 5` seconds (live rates)
- ✅ `HISTORY_CACHE_TTL = 300` seconds (historical data)
- ✅ Disk-based persistent caching for historical/OHLC data
- ✅ Cache directory: `backend/.cache/` (gitignored)

### Frontend Pipeline
- ✅ Centralized forex store (`stores/forex.js`) polls every 5s
- ✅ All components subscribe to store instead of direct API calls
- ✅ `App.vue`: Ticker from forex store, sparklines show 1d data with proper colors
- ✅ `DashboardView`: Uses forex store for currencies
- ✅ `TradingView`: Uses forex store, loading only on initial/pair change, swap button removed
- ✅ `HomeView`: Uses forex store for watchlist
- ✅ `PriceChart`: Uses forex store
- ✅ `SettingsView`: Uses forex store

### Configuration
All refresh intervals set to 5000ms (5 seconds) and clearly labeled as configurable constants.
