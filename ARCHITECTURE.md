# FXTrade Data Architecture

## Centralized Data Pipeline

All forex data (rates, currencies, historical OHLC) flows through a single pipeline: **`stores/forex.js`**

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Forex Store Pipeline                  │
│                   (stores/forex.js)                      │
│                                                           │
│  • Polls /api/forex/rates every 5s (REFRESH_INTERVAL_MS) │
│  • Caches rates, currencies, pair history                │
│  • Single source of truth for all forex data             │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Components subscribe to store
                     │
      ┌──────────────┼──────────────┬──────────────┐
      │              │               │              │
      ▼              ▼               ▼              ▼
┌──────────┐  ┌──────────┐   ┌──────────┐  ┌──────────┐
│ App.vue  │  │Dashboard │   │ Trading  │  │HomeView  │
│ (ticker) │  │   View   │   │   View   │  │(watchlist)
│          │  │ (chart)  │   │  (chart) │  │          │
└──────────┘  └──────────┘   └──────────┘  └──────────┘
```

## Key Components

### 1. Forex Store (`stores/forex.js`)
- **Purpose**: Single data pipeline for all forex data
- **State**:
  - `rates`: Live spot prices (e.g., `{ 'EURUSD': 1.0850 }`)
  - `currencies`: List of supported currencies
  - `pairHistory`: Cached OHLC data per pair/period
  - `lastUpdate`: Timestamp of last successful update
- **Methods**:
  - `startPipeline()`: Begins polling rates every 5s
  - `stopPipeline()`: Stops polling
  - `fetchPairHistory(from, to, period)`: Fetch/cache OHLC data
  - `getCachedPairHistory(from, to, period)`: Read cache without fetch
  - `getRate(from, to)`: Get spot rate from cache
- **Configuration**:
  - `REFRESH_INTERVAL_MS = 5000`: Main polling interval (configurable)

### 2. Portfolio Store (`stores/portfolio.js`)
- **Purpose**: User's holdings and portfolio history
- **State**:
  - `holdings`: Current currency holdings
  - `historyData`: Portfolio value over time
- **Methods**:
  - `fetchHoldings()`: Get current holdings from API
  - `fetchHistory(period)`: Get portfolio history for period
- **Note**: Each view manages its own refresh timer for portfolio data

## Component Data Flow

### App.vue (Header + Ticker)
- **Data**: Subscribes to `forexStore.rates` (computed)
- **Refresh**: Automatic via forex store pipeline
- **Search Sparklines**: Uses `forexStore.fetchPairHistory()` on demand

### DashboardView
- **Data**: 
  - Currencies: `forexStore.currencies` (computed)
  - Portfolio: `portfolioStore.holdings` + `portfolioStore.historyData`
- **Refresh**: 
  - Portfolio refreshes every 5s via local timer
  - Currencies auto-update from forex store
- **Configuration**: `PORTFOLIO_REFRESH_INTERVAL_MS = 5000`

### TradingView
- **Data**:
  - Currencies: `forexStore.currencies` (computed)
  - Chart OHLC: `forexStore.fetchPairHistory()`
  - Exchange rates: `tradeApi.getRate()` (separate, not cached in forex store)
- **Refresh**:
  - Chart refreshes every 5s via `CHART_REFRESH_INTERVAL_MS`
  - Exchange rates refresh every 5s via `RATE_REFRESH_INTERVAL_MS`
- **Loading Behavior**: Only shows "loading" on initial load or pair change, not during background refreshes

### HomeView (Watchlist)
- **Data**:
  - Watchlist pairs: `forexStore.fetchPairHistory()` for each pair
  - Portfolio metrics: `portfolioStore`
- **Refresh**: `WATCHLIST_REFRESH_INTERVAL_MS = 5000`

### PriceChart Component
- **Data**: `forexStore.fetchPairHistory()`
- **Refresh**: Via parent component props changes

## Backend Caching

**File**: `backend/forex_service.py`

```python
CACHE_TTL = 5           # Live rate cache (5 seconds)
HISTORY_CACHE_TTL = 300 # Historical data cache (5 minutes)
```

- **Live rates**: Cached for 5s per pair
- **OHLC history**: Cached for 5 minutes per pair/period combination
- **Implementation**: In-memory dictionaries with timestamp checks

## Configuration Summary

All refresh intervals are configurable via constants at the top of each file:

| Component | Constant | Default | What it controls |
|-----------|----------|---------|------------------|
| `stores/forex.js` | `REFRESH_INTERVAL_MS` | 5000ms | Main pipeline polling |
| `App.vue` | *(removed)* | - | Uses forex store pipeline |
| `DashboardView.vue` | `PORTFOLIO_REFRESH_INTERVAL_MS` | 5000ms | Portfolio data refresh |
| `TradingView.vue` | `CHART_REFRESH_INTERVAL_MS` | 5000ms | Chart data refresh |
| `TradingView.vue` | `RATE_REFRESH_INTERVAL_MS` | 5000ms | Exchange rate refresh |
| `HomeView.vue` | `WATCHLIST_REFRESH_INTERVAL_MS` | 5000ms | Watchlist refresh |
| `backend/forex_service.py` | `CACHE_TTL` | 5s | Live rate cache |
| `backend/forex_service.py` | `HISTORY_CACHE_TTL` | 300s | History cache |

## Benefits

1. **Single Source of Truth**: All components read from same data pipeline
2. **Reduced API Load**: Forex store handles deduplication and caching
3. **Consistent Updates**: All components see same data simultaneously
4. **Easy Configuration**: Change refresh rate in one place per component
5. **Better UX**: Loading states only on initial load, not during refreshes
6. **Data Persistence**: Previous values maintained during errors/refreshes

## Data Freshness

- **Ticker/Search**: Updates every 5s from forex store
- **Dashboard Chart**: Portfolio data every 5s
- **Trading Chart**: OHLC data every 5s, exchange rates every 5s
- **Watchlist**: Updates every 5s
- **Backend Cache**: 5s for live rates, 5min for historical data
