<template>
  <div class="landing" :class="{ 'landing--black-yellow': LANDING_THEME_BLACK_YELLOW }">
    <div class="landing-bg" aria-hidden="true">
      <div ref="globeHost" class="globe-wrap">
        <canvas ref="globeCanvas" class="globe-3d-canvas" />
      </div>
      <div class="landing-vignette" />
      <div class="landing-grain" aria-hidden="true" />
    </div>

    <div
      class="landing-blackout"
      :style="{ opacity: blackoutOpacity }"
      aria-hidden="true"
    />

    <div
      class="landing-hero-fixed"
      :class="{
        'landing-hero-fixed--on-dark': blackoutOpacity > 0.4,
        'landing-hero-fixed--hidden': heroSuppressed
      }"
    >
      <div class="landing-hero">
        <div
          class="landing-hero-focal"
          :style="{
            opacity: heroFocalScrollOpacity,
            pointerEvents: heroFocalScrollOpacity < 0.03 ? 'none' : undefined
          }"
        >
          <RouterLink to="/" class="landing-brand-title font-goldman"> FXTrade </RouterLink>
          <h1 class="landing-headline">
            <span class="landing-headline-line">Trade From Anywhere.</span>
            <span
              class="landing-headline-line landing-headline-pair-line landing-headline-line--sub"
              aria-live="polite"
              aria-atomic="true"
            >
              <span class="landing-headline-ccy">{{ pairBase }}</span>
              to
              <span class="landing-headline-ccy">{{ pairQuote }}</span>
            </span>
          </h1>
          <p class="landing-deck">
            Live forex platform built by traders for traders.
          </p>
          <div class="landing-hero-actions">
            <RouterLink to="/login" class="landing-btn landing-btn-primary"> Get started </RouterLink>
            <RouterLink to="/news" class="landing-btn landing-btn-secondary"> News </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- scrollProgress 0→1 runs only over --anim height; --hold adds extra scroll at full black -->
    <div
      ref="animationScrollRef"
      class="landing-scroll-spacer landing-scroll-spacer--anim"
      aria-hidden="true"
    />
    <div class="landing-scroll-spacer landing-scroll-spacer--hold" aria-hidden="true" />

    <footer
      ref="bottomBrandSection"
      class="landing-bottom-brand"
      :class="{ 'landing-bottom-brand--visible': footerVisible }"
      aria-label="Project credits"
    >
      <div class="landing-bottom-brand-top">
        <p class="landing-bottom-kicker landing-credits-line" style="--d: 0">FXTrade · Capstone</p>
        <div class="landing-bottom-cols">
          <div class="landing-bottom-col">
            <h2 class="landing-bottom-h2 landing-credits-line" style="--d: 1">Credits</h2>
            <ul class="landing-bottom-list">
              <li class="landing-credits-line" style="--d: 2">Daniel Huynh</li>
              <li class="landing-credits-line" style="--d: 3">Yagna Patel</li>
              <li class="landing-credits-line" style="--d: 4">Johnny Diep</li>
              <li class="landing-credits-line" style="--d: 5">Kevin Yu</li>
            </ul>
          </div>
          <div class="landing-bottom-col">
            <h2 class="landing-bottom-h2 landing-credits-line" style="--d: 6">Tech stack</h2>
            <dl class="landing-bottom-tech">
              <div class="landing-bottom-tech-row landing-credits-line" style="--d: 7">
                <dt>Frontend</dt>
                <dd>Vue.js</dd>
              </div>
              <div class="landing-bottom-tech-row landing-credits-line" style="--d: 8">
                <dt>Backend</dt>
                <dd>Python</dd>
              </div>
              <div class="landing-bottom-tech-row landing-credits-line" style="--d: 9">
                <dt>Database</dt>
                <dd>Supabase</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
      <div class="landing-footer-marquee" aria-hidden="true">
        <div class="landing-footer-marquee-track font-goldman">
          <div
            v-for="segment in 2"
            :key="segment"
            class="landing-footer-marquee-segment"
          >
            <span
              v-for="i in MARQUEE_REPEATS"
              :key="`${segment}-${i}`"
              class="landing-footer-marquee-word"
            >FXTRADE</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'

/** Lenis tuning: lower lerp = heavier smoothing; wheelMultiplier scales delta. */
const LENIS_LERP = 0.202
const LENIS_WHEEL_MULTIPLIER = 0.8

const globeCanvas = ref(null)
const globeHost = ref(null)
const animationScrollRef = ref(null)
const bottomBrandSection = ref(null)
const footerVisible = ref(false)

/** Hide fixed hero when the yellow footer is in view (no stacked UI). */
const heroSuppressed = computed(() => footerVisible.value)

/** Repeats per marquee half (two halves loop seamlessly). */
const MARQUEE_REPEATS = 42

/** ISO-style 3-letter codes for hero pair subline (e.g. AUD to USD). */
const FX_PAIR_CODES = [
  'USD',
  'EUR',
  'GBP',
  'JPY',
  'AUD',
  'CAD',
  'CHF',
  'NZD',
  'SEK',
  'NOK',
  'MXN',
  'CNH',
  'SGD',
  'HKD',
  'TRY',
  'ZAR',
  'INR',
  'BRL',
  'KRW',
  'PLN'
]

const PAIR_SHUFFLE_MS = 1500

const pairBase = ref('USD')
const pairQuote = ref('AUD')

function pickHeroPair() {
  const codes = FX_PAIR_CODES
  const prevB = pairBase.value
  const prevQ = pairQuote.value
  let base
  let quote
  for (let i = 0; i < 90; i++) {
    base = codes[Math.floor(Math.random() * codes.length)]
    quote = codes[Math.floor(Math.random() * codes.length)]
    if (base === quote) continue
    if (base === prevB && quote === prevQ) continue
    pairBase.value = base
    pairQuote.value = quote
    return
  }
  do {
    base = codes[Math.floor(Math.random() * codes.length)]
    quote = codes[Math.floor(Math.random() * codes.length)]
  } while (base === quote)
  pairBase.value = base
  pairQuote.value = quote
}

/** 0→1 while scrolling through `animationScrollRef` only; stays 1 during hold spacer */
const scrollProgress = ref(0)

const blackoutOpacity = computed(() => {
  const p = scrollProgress.value
  if (p <= 0.32) return 0
  return Math.max(0, Math.min(1, (p - 0.32) / 0.68))
})

/** FXTrade, headline, deck, CTAs fade together over this scrollProgress window. */
const HERO_FOCAL_FADE_START = 0.58
const HERO_FOCAL_FADE_END = 0.82

const heroFocalScrollOpacity = computed(() => {
  const p = scrollProgress.value
  const a = HERO_FOCAL_FADE_START
  const b = HERO_FOCAL_FADE_END
  if (p <= a) return 1
  if (p >= b) return 0
  return 1 - (p - a) / (b - a)
})

/**
 * Theme toggle for the landing hero (edit in code).
 * false — light grey background, black title/CTA, dark wireframe globe.
 * true  — black background, gold/yellow title/CTA and wireframe globe.
 */
const LANDING_THEME_BLACK_YELLOW = true

const TILT = 0.38
const cosT = Math.cos(TILT)
const sinT = Math.sin(TILT)
/** Base camera distance; effective Z increases while scrolling → globe zooms out */
const CAM_Z_BASE = 6.05
const CAM_Z_SCROLL_EXTRA = 6.2

function rotY(p, cosA, sinA) {
  return {
    x: p.x * cosA + p.z * sinA,
    y: p.y,
    z: -p.x * sinA + p.z * cosA
  }
}

function rotX(p) {
  return {
    x: p.x,
    y: p.y * cosT - p.z * sinT,
    z: p.y * sinT + p.z * cosT
  }
}

/** Unit sphere: phi latitude, theta longitude */
function spherePoint(phi, theta) {
  const cp = Math.cos(phi)
  return {
    x: cp * Math.cos(theta),
    y: Math.sin(phi),
    z: cp * Math.sin(theta)
  }
}

function transformWorld(p, angleY) {
  const cosA = Math.cos(angleY)
  const sinA = Math.sin(angleY)
  return rotX(rotY(p, cosA, sinA))
}

function project(p, cx, cy, radiusPx, camZ) {
  const d = camZ - p.z
  if (d < 0.06) return null
  const scale = (camZ / d) * radiusPx
  return {
    x: cx + p.x * scale,
    y: cy + p.y * scale,
    z: p.z
  }
}

/** Uniform random point on unit sphere (y-up, matches globe model). */
function randomSurfacePoint() {
  const theta = Math.random() * Math.PI * 2
  const y = Math.random() * 2 - 1
  const r = Math.sqrt(Math.max(0, 1 - y * y))
  return { x: r * Math.cos(theta), y, z: r * Math.sin(theta) }
}

const ARC_COUNT = 14

/**
 * Quadratic blend on the sphere (normalized): random control c yields non–great-circle arcs.
 * Optional bulge kicks the path slightly off the A–c–B plane for more variation.
 */
function arcPointOnCurve(arc, t) {
  const omt = 1 - t
  let x = omt * omt * arc.a.x + 2 * t * omt * arc.c.x + t * t * arc.b.x
  let y = omt * omt * arc.a.y + 2 * t * omt * arc.c.y + t * t * arc.b.y
  let z = omt * omt * arc.a.z + 2 * t * omt * arc.c.z + t * t * arc.b.z
  let len = Math.hypot(x, y, z)
  if (len < 1e-7) {
    return { x: arc.a.x, y: arc.a.y, z: arc.a.z }
  }
  x /= len
  y /= len
  z /= len
  if (arc.bulgeAmp > 1e-6) {
    const envelope = Math.sin(Math.PI * t) ** 2
    const k = arc.bulgeAmp * envelope
    x += k * arc.bulgeAxis.x
    y += k * arc.bulgeAxis.y
    z += k * arc.bulgeAxis.z
    len = Math.hypot(x, y, z)
    if (len > 1e-7) {
      x /= len
      y /= len
      z /= len
    }
  }
  return { x, y, z }
}

function randomUnitPerpendicularTo(vx, vy, vz) {
  let ax = Math.random() - 0.5
  let ay = Math.random() - 0.5
  let az = Math.random() - 0.5
  let dot = ax * vx + ay * vy + az * vz
  ax -= dot * vx
  ay -= dot * vy
  az -= dot * vz
  let len = Math.hypot(ax, ay, az)
  if (len < 1e-6) {
    return { x: 1, y: 0, z: 0 }
  }
  return { x: ax / len, y: ay / len, z: az / len }
}

/** @type {{ a: object, b: object, c: object, bulgeAxis: object, bulgeAmp: number, radialBoost: number, phase: number, speed: number, pulseHalf: number, pathSteps: number }[]} */
let travelArcs = []

function initTravelArcs() {
  travelArcs = []
  for (let i = 0; i < ARC_COUNT; i++) {
    let a
    let b
    let dot
    let attempts = 0
    do {
      a = randomSurfacePoint()
      b = randomSurfacePoint()
      dot = a.x * b.x + a.y * b.y + a.z * b.z
      attempts++
    } while ((dot > 0.62 || dot < -0.99) && attempts < 55)

    const mx = (a.x + b.x) * 0.5
    const my = (a.y + b.y) * 0.5
    const mz = (a.z + b.z) * 0.5
    const chordLen = Math.hypot(b.x - a.x, b.y - a.y, b.z - a.z) || 1
    const ux = (b.x - a.x) / chordLen
    const uy = (b.y - a.y) / chordLen
    const uz = (b.z - a.z) / chordLen
    const perp = randomUnitPerpendicularTo(ux, uy, uz)
    const side = Math.random() < 0.5 ? -1 : 1
    const lift = 0.35 + Math.random() * 1.15
    let cx = mx + side * perp.x * lift
    let cy = my + side * perp.y * lift
    let cz = mz + side * perp.z * lift
    let cl = Math.hypot(cx, cy, cz)
    if (cl > 1e-7) {
      cx /= cl
      cy /= cl
      cz /= cl
    }
    const c = { x: cx, y: cy, z: cz }

    const bulgeAxis = randomUnitPerpendicularTo(
      c.x - a.x,
      c.y - a.y,
      c.z - a.z
    )
    const bulgeAmp = Math.random() * 0.38

    travelArcs.push({
      a,
      b,
      c,
      bulgeAxis,
      bulgeAmp,
      /** Slightly larger than unit sphere so arcs read in front of the wireframe shell */
      radialBoost: 1.055 + Math.random() * 0.038,
      phase: Math.random() * Math.PI * 2,
      speed: 0.38 + Math.random() * 1.55,
      pulseHalf: 0.055 + Math.random() * 0.09,
      pathSteps: 36 + Math.floor(Math.random() * 28)
    })
  }
}

function strokeArcPath(ctx, arc, angleY, cx, cy, radiusPx, camZ, t0, t1, steps) {
  let started = false
  ctx.beginPath()
  const n = Math.max(8, steps)
  const rb = arc.radialBoost ?? 1.07
  for (let i = 0; i <= n; i++) {
    const t = t0 + (i / n) * (t1 - t0)
    const q = arcPointOnCurve(arc, t)
    const p = { x: q.x * rb, y: q.y * rb, z: q.z * rb }
    const w = transformWorld(p, angleY)
    const pr = project(w, cx, cy, radiusPx, camZ)
    if (!pr) continue
    if (!started) {
      ctx.moveTo(pr.x, pr.y)
      started = true
    } else {
      ctx.lineTo(pr.x, pr.y)
    }
  }
  return started
}

/** Arcs with a pulse traveling along each path; gold on dark theme, black on light */
function drawTravelArcs(ctx, cx, cy, radiusPx, camZ, angleY, blackYellow, nowMs, zoom01) {
  if (!travelArcs.length) return

  const arcDim = Math.max(0.08, 1 - zoom01 * 0.92)
  const baseAlpha = (blackYellow ? 0.2 : 0.24) * arcDim
  const headAlpha = (blackYellow ? 0.92 : 0.88) * arcDim
  const baseLine = blackYellow ? 1.15 : 1.05
  const headLine = blackYellow ? 2.4 : 2.1

  const baseRgb = blackYellow ? '255, 215, 0' : '22, 22, 20'
  const headRgb = blackYellow ? '255, 235, 140' : '8, 8, 8'
  const shadowRgb = blackYellow ? '255, 215, 0' : '0, 0, 0'

  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'

  for (const arc of travelArcs) {
    const u = 0.5 + 0.5 * Math.sin(nowMs * 0.00038 * arc.speed + arc.phase)
    const half = arc.pulseHalf

    ctx.shadowBlur = 0
    ctx.strokeStyle = `rgba(${baseRgb}, ${baseAlpha})`
    ctx.lineWidth = baseLine
    if (strokeArcPath(ctx, arc, angleY, cx, cy, radiusPx, camZ, 0, 1, arc.pathSteps)) {
      ctx.stroke()
    }

    const t0 = Math.max(0, u - half)
    const t1 = Math.min(1, u + half)
    if (t1 > t0) {
      ctx.save()
      ctx.strokeStyle = `rgba(${headRgb}, ${headAlpha})`
      ctx.lineWidth = headLine
      ctx.shadowColor = `rgba(${shadowRgb}, ${blackYellow ? 0.55 : 0.22})`
      ctx.shadowBlur = blackYellow ? 10 : 5
      if (
        strokeArcPath(
          ctx,
          arc,
          angleY,
          cx,
          cy,
          radiusPx,
          camZ,
          t0,
          t1,
          Math.max(12, Math.round(arc.pathSteps * 0.45))
        )
      ) {
        ctx.stroke()
      }
      ctx.restore()
    }
  }
}

function drawWireframeGlobe(canvas, angleY, blackYellow, nowMs, zoom01) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const rect = canvas.parentElement?.getBoundingClientRect()
  if (!rect?.width) return

  const maxPixels = 3_200_000
  let dpr = Math.min(window.devicePixelRatio || 1, 2)
  let bw = rect.width * dpr
  let bh = rect.height * dpr
  if (bw * bh > maxPixels) {
    const f = Math.sqrt(maxPixels / (bw * bh))
    dpr *= f
    bw = rect.width * dpr
    bh = rect.height * dpr
  }

  canvas.width = Math.floor(bw)
  canvas.height = Math.floor(bh)
  canvas.style.width = `${rect.width}px`
  canvas.style.height = `${rect.height}px`

  const w = rect.width
  const h = rect.height
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  ctx.clearRect(0, 0, w, h)

  const cx = w / 2
  const cy = h / 2
  const z01 = Math.max(0, Math.min(1, zoom01))
  const camZ = CAM_Z_BASE + z01 * CAM_Z_SCROLL_EXTRA
  const radiusPx = Math.min(w, h) * 0.23 * (1 - z01 * 0.42)

  const nLon = 22
  const nLat = 14
  const phiStep = 0.07
  const thetaStep = 0.06

  const segments = []

  function pushSegment(a, b) {
    if (!a || !b) return
    const z = (a.z + b.z) * 0.5
    segments.push({ a, b, z })
  }

  for (let i = 0; i < nLon; i++) {
    const theta0 = (i / nLon) * Math.PI * 2
    let prev = null
    for (let phi = -Math.PI / 2 + 0.02; phi <= Math.PI / 2 - 0.02; phi += phiStep) {
      const p = transformWorld(spherePoint(phi, theta0), angleY)
      const proj = project(p, cx, cy, radiusPx, camZ)
      if (prev && proj) pushSegment(prev, proj)
      prev = proj
    }
  }

  for (let j = 1; j < nLat; j++) {
    const phi = (j / nLat - 0.5) * Math.PI
    let prev = null
    for (let t = 0; t <= Math.PI * 2 + thetaStep; t += thetaStep) {
      const p = transformWorld(spherePoint(phi, t), angleY)
      const proj = project(p, cx, cy, radiusPx, camZ)
      if (prev && proj) pushSegment(prev, proj)
      prev = proj
    }
  }

  segments.sort((u, v) => u.z - v.z)

  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'

  const globeDim = Math.max(0.06, 1 - z01 * 0.88)
  for (const { a, b, z } of segments) {
    const front01 = Math.max(0, Math.min(1, (z + 1) * 0.5))
    const shade = Math.pow(front01, 2.45)
    let alpha = blackYellow ? 0.015 + 0.52 * shade : 0.02 + 0.44 * shade
    alpha *= globeDim
    ctx.strokeStyle = blackYellow
      ? `rgba(255, 215, 0, ${alpha})`
      : `rgba(32, 32, 30, ${alpha})`
    ctx.lineWidth = 0.45 + 0.78 * shade
    ctx.beginPath()
    ctx.moveTo(a.x, a.y)
    ctx.lineTo(b.x, b.y)
    ctx.stroke()
  }

  drawTravelArcs(ctx, cx, cy, radiusPx, camZ, angleY, blackYellow, nowMs, z01)

  const rimA = (blackYellow ? 0.4 : 0.22) * globeDim
  ctx.strokeStyle = blackYellow ? `rgba(255, 215, 0, ${rimA})` : `rgba(26, 26, 24, ${rimA})`
  ctx.lineWidth = 1.1
  ctx.beginPath()
  ctx.arc(cx, cy, radiusPx * 1.002, 0, Math.PI * 2)
  ctx.stroke()
}

let globeRo
let raf = 0
let angleY = 0
const SPIN = 0.00035
/** Y-axis rotation added from scroll=0 → scroll=1 (on top of idle spin) */
const SCROLL_YAW_RADIANS = Math.PI * 4.25
let teardownScrollListeners = null
let footerIo = null
let lenis = null
let pairShuffleId = null

function globeYawForDraw() {
  return angleY + scrollProgress.value * SCROLL_YAW_RADIANS
}

function readScrollProgress() {
  const zone = animationScrollRef.value
  const h = zone?.offsetHeight ?? 0
  if (h <= 1) {
    scrollProgress.value = 0
    return
  }
  const y = lenis != null ? lenis.scroll : window.scrollY
  scrollProgress.value = Math.max(0, Math.min(1, y / h))
}

function globeFrame(time) {
  lenis?.raf(time)
  const c = globeCanvas.value
  if (!c) {
    raf = requestAnimationFrame(globeFrame)
    return
  }
  angleY += SPIN
  if (angleY > Math.PI * 2000) angleY -= Math.PI * 2000
  drawWireframeGlobe(
    c,
    globeYawForDraw(),
    LANDING_THEME_BLACK_YELLOW,
    performance.now(),
    scrollProgress.value
  )
  raf = requestAnimationFrame(globeFrame)
}

onMounted(async () => {
  await nextTick()
  initTravelArcs()

  readScrollProgress()

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  let onScroll = null
  if (!reduceMotion) {
    lenis = new Lenis({
      lerp: LENIS_LERP,
      wheelMultiplier: LENIS_WHEEL_MULTIPLIER,
      smoothWheel: true,
      autoRaf: false,
      anchors: true
    })
    lenis.on('scroll', readScrollProgress)
    readScrollProgress()
  } else {
    onScroll = () => readScrollProgress()
    window.addEventListener('scroll', onScroll, { passive: true })
  }
  window.addEventListener('resize', readScrollProgress, { passive: true })
  teardownScrollListeners = () => {
    if (onScroll) window.removeEventListener('scroll', onScroll)
    window.removeEventListener('resize', readScrollProgress)
  }

  globeRo = new ResizeObserver(() => {
    readScrollProgress()
    drawWireframeGlobe(
      globeCanvas.value,
      globeYawForDraw(),
      LANDING_THEME_BLACK_YELLOW,
      performance.now(),
      scrollProgress.value
    )
  })
  if (globeHost.value) {
    globeRo.observe(globeHost.value)
  }
  if (animationScrollRef.value) {
    globeRo.observe(animationScrollRef.value)
  }

  footerIo = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        footerVisible.value = e.isIntersecting
      }
    },
    { root: null, rootMargin: '0px 0px -8% 0px', threshold: 0.06 }
  )
  if (bottomBrandSection.value) {
    footerIo.observe(bottomBrandSection.value)
  }

  pickHeroPair()
  pairShuffleId = window.setInterval(pickHeroPair, PAIR_SHUFFLE_MS)

  raf = requestAnimationFrame(globeFrame)
})

onUnmounted(() => {
  cancelAnimationFrame(raf)
  if (pairShuffleId != null) {
    clearInterval(pairShuffleId)
    pairShuffleId = null
  }
  lenis?.destroy()
  lenis = null
  teardownScrollListeners?.()
  footerIo?.disconnect()
  globeRo?.disconnect()
})
</script>

<style scoped>
.landing {
  position: relative;
  flex: 1 1 auto;
  width: 100%;
  min-width: 100%;
  min-height: calc(100vh - 4rem);
  min-height: calc(100dvh - 4rem);
  overflow-x: hidden;
}

/* Animation zone: scrollProgress 0→1 (globe / blackout). Tuning this changes animation speed. */
.landing-scroll-spacer {
  flex-shrink: 0;
  pointer-events: none;
}

.landing-scroll-spacer--anim {
  height: 265vh;
}

/* Extra scroll after animation finishes (scrollProgress stays 1); lengthens “black” before footer */
.landing-scroll-spacer--hold {
  height: 220vh;
}

.landing-blackout {
  position: fixed;
  left: 0;
  right: 0;
  top: 4rem;
  bottom: 0;
  z-index: 5;
  background: #000000;
  pointer-events: none;
}

/* Full viewport layer (sits under sticky header z-50) so the hero isn’t clipped below the nav */
.landing-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  background: #ecebe8;
}

.globe-wrap {
  position: absolute;
  left: 50%;
  top: 50%;
  /* Cover viewport corners; cap so the canvas is not oversized */
  width: min(140vmax, calc(max(100vw, 100vh) * 1.35));
  height: min(140vmax, calc(max(100vw, 100vh) * 1.35));
  max-width: none;
  max-height: none;
  transform: translate(-50%, -50%);
  opacity: 0.62;
  pointer-events: none;
  z-index: 1;
}

.globe-3d-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.landing-vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
  box-shadow: inset 0 0 100px 40px rgba(0, 0, 0, 0.35),
    inset 0 0 220px 90px rgba(0, 0, 0, 0.2);
  background: radial-gradient(
    ellipse 85% 75% at 50% 50%,
    transparent 0%,
    transparent 45%,
    rgba(0, 0, 0, 0.12) 100%
  );
}

/* Film grain (fixed over globe + vignette; pointer-events none) */
.landing-grain {
  position: fixed;
  inset: 0;
  z-index: 4;
  pointer-events: none;
  opacity: 0.11;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='280' height='280'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 280px 280px;
  mix-blend-mode: multiply;
  animation: landing-grain-shift 0.8s steps(6) infinite;
}

@media (prefers-reduced-motion: reduce) {
  .landing-grain {
    animation: none;
  }
}

@keyframes landing-grain-shift {
  0% {
    transform: translate(0, 0);
  }
  20% {
    transform: translate(-1.5%, 1%);
  }
  40% {
    transform: translate(1%, -0.5%);
  }
  60% {
    transform: translate(-0.5%, -1.2%);
  }
  80% {
    transform: translate(1.2%, 0.8%);
  }
  100% {
    transform: translate(0, 0);
  }
}

/* Hero stays pinned in the viewport while the page scrolls */
.landing-hero-fixed {
  position: fixed;
  left: 0;
  right: 0;
  top: 4rem;
  bottom: 0;
  z-index: 6;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  text-align: center;
  pointer-events: none;
}

.landing-hero-fixed .landing-hero {
  pointer-events: auto;
}

/* Light text when the black layer rises behind the hero */
.landing-hero-fixed--on-dark .landing-brand-title,
.landing-hero-fixed--on-dark .landing-headline,
.landing-hero-fixed--on-dark .landing-deck {
  color: #f5f5f5;
  text-shadow: 0 2px 24px rgba(0, 0, 0, 0.5);
}

.landing-hero-fixed--on-dark .landing-deck {
  color: rgba(245, 245, 245, 0.78);
}

.landing-hero-fixed--on-dark .landing-btn-primary {
  background: #f5f5f5;
  color: #0a0a0a;
  border-color: #f5f5f5;
}

.landing-hero-fixed--on-dark .landing-btn-primary:hover {
  background: #ffffff;
  border-color: #ffffff;
  color: #0a0a0a;
}

.landing-hero-fixed--on-dark .landing-btn-secondary {
  color: #f5f5f5;
  border-color: rgba(245, 245, 245, 0.75);
}

.landing-hero-fixed--on-dark .landing-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-color: #fff;
}

.landing-hero-fixed--hidden {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition:
    opacity 0.45s ease,
    visibility 0.45s ease;
}

.landing-credits-line {
  opacity: 0;
  transform: translateY(1.75rem);
  transition:
    opacity 0.85s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.85s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: calc(var(--d, 0) * 75ms);
}

.landing-bottom-brand--visible .landing-credits-line {
  opacity: 1;
  transform: translateY(0);
}

.landing-bottom-brand {
  position: relative;
  z-index: 8;
  background: #ffd700;
  color: #0a0a0a;
  padding: clamp(0.65rem, 1.8vw, 1rem) 0 0;
  overflow: hidden;
  isolation: isolate;
}

.landing-bottom-brand-top {
  width: 100%;
  padding: 0 clamp(1rem, 4vw, 2.5rem) clamp(0.5rem, 1.2vw, 0.75rem);
  text-align: left;
  box-sizing: border-box;
}

.landing-bottom-kicker {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.62rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(10, 10, 10, 0.48);
  margin: 0 0 0.55rem;
}

.landing-bottom-h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1rem, 2.2vw, 1.2rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: #0a0a0a;
  margin: 0 0 0.35rem;
}

.landing-bottom-cols {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: clamp(0.85rem, 3vw, 2rem);
  align-items: start;
}

.landing-bottom-col {
  min-width: 0;
}

.landing-bottom-list {
  list-style: none;
  margin: 0;
  padding: 0;
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
  font-size: 0.82rem;
  line-height: 1.45;
  color: rgba(10, 10, 10, 0.88);
}

.landing-bottom-tech {
  margin: 0;
  padding: 0;
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
}

.landing-bottom-tech-row {
  display: grid;
  grid-template-columns: 4.75rem minmax(0, 1fr);
  gap: 0.35rem 0.65rem;
  margin: 0 0 0.35rem;
  font-size: 0.8rem;
  line-height: 1.35;
}

.landing-bottom-tech-row dt {
  margin: 0;
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.6rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(10, 10, 10, 0.45);
}

.landing-bottom-tech-row dd {
  margin: 0;
  color: rgba(10, 10, 10, 0.92);
}

.landing-footer-marquee {
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  padding: 0.15rem 0 0.1rem;
  opacity: 0;
  transform: translateY(10%);
  transition:
    opacity 0.65s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.65s cubic-bezier(0.22, 1, 0.36, 1);
  mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 6%,
    black 94%,
    transparent 100%
  );
  -webkit-mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 6%,
    black 94%,
    transparent 100%
  );
}

.landing-bottom-brand--visible .landing-footer-marquee {
  opacity: 1;
  transform: translateY(0);
}

.landing-footer-marquee-track {
  display: flex;
  width: max-content;
  flex-shrink: 0;
  will-change: transform;
  animation: landing-footer-marquee-ltr 300s linear infinite;
}

.landing-footer-marquee-segment {
  display: flex;
  flex-shrink: 0;
  flex-wrap: nowrap;
  align-items: center;
  gap: clamp(0.65rem, 2vw, 1.35rem);
}

.landing-footer-marquee-word {
  flex-shrink: 0;
  font-weight: 700;
  font-size: clamp(1.85rem, 7.5vw, 3.75rem);
  line-height: 0.85;
  letter-spacing: -0.055em;
  color: #0a0a0a;
  padding: 0;
  margin: 0;
  user-select: none;
}

@media (prefers-reduced-motion: reduce) {
  .landing-footer-marquee-track {
    animation: none;
    transform: translateX(0);
  }
}

@keyframes landing-footer-marquee-ltr {
  from {
    transform: translateX(-50%);
  }
  to {
    transform: translateX(0);
  }
}

.landing-hero {
  max-width: 42rem;
  width: 100%;
}

.landing-brand-title {
  display: block;
  margin: 0 auto 1rem;
  font-size: clamp(2.75rem, 9vw, 4.25rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1;
  text-decoration: none;
  color: #0a0a0a;
  transition: opacity 0.2s ease;
}

.landing-brand-title:hover {
  opacity: 0.85;
}

.landing-hero-focal {
  transition: opacity 0.45s ease;
}

.landing-headline {
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  font-family: 'Fraunces', Georgia, 'Times New Roman', serif;
  font-weight: 600;
  font-size: clamp(2.35rem, 7.5vw, 4.25rem);
  line-height: 1.06;
  letter-spacing: -0.03em;
  color: #0a0a0a;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.35);
}

.landing-headline-line {
  display: block;
  width: max-content;
  max-width: 100%;
  text-align: center;
}

.landing-headline-line + .landing-headline-line {
  margin-top: 0.12em;
}

/* Second line: live pair, slightly smaller than main headline */
.landing-headline-line--sub {
  font-size: clamp(1.45rem, 5vw, 2.65rem);
  opacity: 0.9;
}

/* Fixed-width code slots so random pairs don’t shift layout */
.landing-headline-pair-line {
  min-height: 1.06em;
}

.landing-headline-ccy {
  display: inline-block;
  box-sizing: border-box;
  width: 3.55ch;
  margin: 0 0.06em;
  text-align: center;
  font: inherit;
  letter-spacing: inherit;
  vertical-align: baseline;
}

.landing-deck {
  margin: 1.35rem auto 0;
  max-width: 34rem;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: clamp(0.95rem, 2.2vw, 1.125rem);
  line-height: 1.55;
  font-weight: 500;
  color: rgba(10, 10, 10, 0.72);
}

.landing-hero-actions {
  margin-top: 1.75rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1rem;
  justify-content: center;
  align-items: center;
}

.landing-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.9rem 1.65rem;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  border-radius: 9999px;
  text-decoration: none;
  transition: transform 0.2s ease, background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.landing-btn:hover {
  transform: translateY(-1px);
}

.landing-btn-primary {
  background: #0a0a0a;
  color: #fafaf8;
  border: 2px solid #0a0a0a;
  box-shadow: 0 2px 14px rgba(0, 0, 0, 0.12);
}

.landing-btn-primary:hover {
  background: #1a1a1a;
  border-color: #1a1a1a;
  color: #fff;
}

.landing-btn-secondary {
  background: transparent;
  color: #0a0a0a;
  border: 2px solid #0a0a0a;
}

.landing-btn-secondary:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #0a0a0a;
}

/* —— Black / gold theme (LANDING_THEME_BLACK_YELLOW = true) —— */
.landing--black-yellow .landing-bg {
  background: #000000;
}

.landing--black-yellow .globe-wrap {
  opacity: 0.78;
}

.landing--black-yellow .landing-vignette {
  box-shadow: inset 0 0 120px 50px rgba(0, 0, 0, 0.65),
    inset 0 0 200px 100px rgba(0, 0, 0, 0.45);
  background: radial-gradient(
    ellipse 80% 70% at 50% 50%,
    transparent 0%,
    transparent 40%,
    rgba(255, 215, 0, 0.04) 70%,
    rgba(0, 0, 0, 0.35) 100%
  );
}

.landing--black-yellow .landing-grain {
  opacity: 0.16;
  mix-blend-mode: soft-light;
}

.landing--black-yellow .landing-headline {
  color: #f5f0e6;
  text-shadow: 0 0 48px rgba(255, 215, 0, 0.12), 0 2px 24px rgba(0, 0, 0, 0.45);
}

.landing--black-yellow .landing-deck {
  color: rgba(245, 240, 230, 0.72);
}

.landing--black-yellow .landing-brand-title {
  color: #ffd700;
}

.landing--black-yellow .landing-btn-primary {
  background: #ffd700;
  color: #0a0a0a;
  border-color: #ffd700;
  box-shadow: 0 2px 24px rgba(255, 215, 0, 0.2);
}

.landing--black-yellow .landing-btn-primary:hover {
  background: #ffe033;
  border-color: #ffe033;
  color: #0a0a0a;
}

.landing--black-yellow .landing-btn-secondary {
  background: transparent;
  color: #f5f0e6;
  border-color: rgba(255, 215, 0, 0.65);
}

.landing--black-yellow .landing-btn-secondary:hover {
  background: rgba(255, 215, 0, 0.1);
  color: #fff;
  border-color: #ffd700;
}

/* Keep gold/cream hero when blackout rises on the dark theme */
.landing--black-yellow .landing-hero-fixed--on-dark .landing-brand-title {
  color: #ffd700;
  text-shadow: 0 0 32px rgba(255, 215, 0, 0.2), 0 2px 20px rgba(0, 0, 0, 0.6);
}

.landing--black-yellow .landing-hero-fixed--on-dark .landing-headline {
  color: #f5f0e6;
}

.landing--black-yellow .landing-hero-fixed--on-dark .landing-deck {
  color: rgba(245, 240, 230, 0.78);
}

.landing--black-yellow .landing-hero-fixed--on-dark .landing-btn-primary {
  background: #ffd700;
  color: #0a0a0a;
  border-color: #ffd700;
}

.landing--black-yellow .landing-hero-fixed--on-dark .landing-btn-secondary {
  color: #f5f0e6;
  border-color: rgba(255, 215, 0, 0.7);
}
</style>
