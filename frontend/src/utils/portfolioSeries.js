/** Start of local calendar day (ms). */
export function startOfLocalDayMs(ref = new Date()) {
  const d = new Date(ref)
  d.setHours(0, 0, 0, 0)
  return d.getTime()
}

/** Next local midnight after `ref`'s day (ms) — exclusive end of “today”. */
export function endOfLocalDayMs(ref = new Date()) {
  const d = new Date(ref)
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() + 1)
  return d.getTime()
}

export function formatDateLabel(dateStr, period) {
  const d = new Date(dateStr)
  switch (period) {
    case '1d':
      return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    case '1wk':
      return (
        d.toLocaleDateString('en-US', { weekday: 'short' }) +
        ' ' +
        d.toLocaleTimeString('en-US', { hour: 'numeric' })
      )
    case '1mo':
    case '3mo':
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    case '6mo':
    case '1y':
      return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
    case '3y':
    case '5y':
      return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
    default:
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }
}

/**
 * USD series for portfolio chart / headline — matches GET /portfolio/history?period=…
 */
export function buildPortfolioSeriesUsd(history, period) {
  if (!history?.data_points?.length) {
    return { type: 'empty' }
  }
  if (period === '1d') {
    const nowMs = Date.now()
    const dayStart = startOfLocalDayMs()
    const dayEnd = endOfLocalDayMs()
    const sorted = history.data_points
      .map((dp) => ({ x: new Date(dp.date).getTime(), y: dp.value }))
      .filter((p) => p.x >= dayStart && p.x <= dayEnd && p.x <= nowMs)
      .sort((a, b) => a.x - b.x)
    const data = [...sorted]
    if (data.length > 0) {
      const last = data[data.length - 1]
      if (nowMs > last.x) {
        data.push({ x: nowMs, y: last.y })
      }
    }
    return { type: 'xy', data }
  }
  return {
    type: 'category',
    labels: history.data_points.map((dp) => formatDateLabel(dp.date, period)),
    data: history.data_points.map((dp) => dp.value)
  }
}

export function portfolioHistoryBaselineUsd(history, period) {
  const s = buildPortfolioSeriesUsd(history, period)
  if (s.type === 'empty') return null
  if (s.type === 'xy') return s.data.length ? s.data[0].y : null
  return s.data.length ? s.data[0] : null
}
