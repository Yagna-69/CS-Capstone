<template>
  <div class="min-h-screen flex">
    <!-- Matrix Background (70%) -->
    <div class="hidden lg:flex lg:w-[70%] bg-black relative overflow-hidden">
      <canvas ref="matrixCanvas" class="absolute inset-0 w-full h-full"></canvas>
    </div>

    <!-- Panel (30%) -->
    <div class="w-full lg:w-[30%] flex items-center justify-center bg-bg-secondary p-8 overflow-hidden">
      <div class="w-full max-w-md">
        <!-- Brand -->
        <div class="flex flex-col items-center justify-center mb-8">
          <RouterLink to="/" class="text-6xl font-bold font-goldman text-primary hover:opacity-80 transition">FXTrade</RouterLink>
        </div>

        <Transition name="slide-fade" mode="out-in">

          <!-- Error state (expired / invalid link) -->
          <div v-if="urlError" key="error" class="text-center space-y-5">
            <div class="w-14 h-14 rounded-full bg-red-500/10 flex items-center justify-center mx-auto">
              <svg class="w-7 h-7 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
              </svg>
            </div>
            <p class="text-white font-semibold text-lg">Link expired or invalid</p>
            <p class="text-gray-400 text-sm">{{ urlError }}</p>
            <p class="text-gray-500 text-xs">Request a new reset link from the login page.</p>
            <RouterLink
              to="/login"
              class="block w-full py-3.5 bg-primary text-black rounded-full font-bold hover:opacity-90 transition text-center mt-2"
            >
              Back to Login
            </RouterLink>
          </div>

          <!-- Success state -->
          <div v-else-if="success" key="success" class="text-center space-y-5">
            <div class="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
              <svg class="w-7 h-7 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
            <p class="text-white font-semibold text-lg">Password updated!</p>
            <p class="text-gray-400 text-sm">You can now log in with your new password.</p>
            <RouterLink
              to="/login"
              class="block w-full py-3.5 bg-primary text-black rounded-full font-bold hover:opacity-90 transition text-center mt-2"
            >
              Go to Login
            </RouterLink>
          </div>

          <!-- Form state -->
          <div v-else key="form">
            <h2 class="text-2xl font-bold text-white text-center mb-2">Set a new password</h2>
            <p class="text-gray-500 text-sm text-center mb-8">Choose a strong password for your account.</p>

            <form @submit.prevent="submit" class="space-y-4">

              <!-- New Password -->
              <div class="relative">
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <input
                  v-model="newPassword"
                  :type="showNew ? 'text' : 'password'"
                  placeholder="New password (min. 6 chars)"
                  autocomplete="new-password"
                  class="w-full pl-12 pr-12 py-3.5 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary transition"
                />
                <button type="button" @click="showNew = !showNew" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
                  <svg v-if="!showNew" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                  <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                  </svg>
                </button>
              </div>

              <!-- Confirm Password -->
              <div class="relative">
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <input
                  v-model="confirmPassword"
                  :type="showConfirm ? 'text' : 'password'"
                  placeholder="Confirm new password"
                  autocomplete="new-password"
                  class="w-full pl-12 pr-12 py-3.5 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary transition"
                />
                <button type="button" @click="showConfirm = !showConfirm" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
                  <svg v-if="!showConfirm" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                  <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                  </svg>
                </button>
              </div>

              <!-- Inline error -->
              <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

              <!-- Submit -->
              <button
                type="submit"
                :disabled="loading"
                class="w-full py-3.5 bg-primary text-black rounded-full font-bold hover:opacity-90 transition disabled:opacity-50 mt-2 relative"
              >
                <span v-if="!loading">Set New Password</span>
                <span v-else class="flex items-center justify-center gap-2">
                  <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Updating…
                </span>
              </button>

              <div class="text-center pt-1">
                <RouterLink to="/login" class="text-sm text-gray-500 hover:text-white transition">Back to login</RouterLink>
              </div>
            </form>
          </div>

        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { authApi } from '@/services/api'

const newPassword     = ref('')
const confirmPassword = ref('')
const showNew         = ref(false)
const showConfirm     = ref(false)
const loading         = ref(false)
const error           = ref('')
const success         = ref(false)
const urlError        = ref('')
const accessToken     = ref('')
const matrixCanvas    = ref(null)
let animationId       = null

onMounted(() => {
  // Parse Supabase hash fragment: /reset-password#access_token=XXX&type=recovery
  const hash   = window.location.hash.slice(1)
  const params = new URLSearchParams(hash)

  if (params.get('error')) {
    urlError.value = decodeURIComponent(
      params.get('error_description') || 'The reset link is invalid or has expired.'
    ).replace(/\+/g, ' ')
  } else {
    const token = params.get('access_token')
    const type  = params.get('type')
    if (!token || type !== 'recovery') {
      urlError.value = 'No valid reset token found. Please request a new reset email.'
    } else {
      accessToken.value = token
    }
  }

  startMatrix()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})

function startMatrix() {
  const canvas = matrixCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  canvas.width  = canvas.offsetWidth
  canvas.height = canvas.offsetHeight

  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // Rotate 45 degrees
  ctx.save()
  ctx.translate(canvas.width / 2, canvas.height / 2)
  ctx.rotate(45 * Math.PI / 180)
  ctx.translate(-canvas.width / 2, -canvas.height / 2)

  const chars    = '¥$€£₹₽¢₩₪₴฿₦₡₵₲₱₸₹₺₼₽₾₿'
  const fontSize = 64
  const columns  = Math.ceil(canvas.width * 1.5 / fontSize)
  const drops    = []
  const trails   = []

  for (let i = 0; i < columns; i++) {
    drops[i]  = Math.random() * -50
    trails[i] = []
  }

  function draw() {
    ctx.restore()
    ctx.fillStyle = 'rgba(0, 0, 0, 0.03)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    ctx.save()
    ctx.translate(canvas.width / 2, canvas.height / 2)
    ctx.rotate(45 * Math.PI / 180)
    ctx.translate(-canvas.width / 2, -canvas.height / 2)

    ctx.font       = `${fontSize}px monospace`
    ctx.shadowBlur = 0

    for (let i = 0; i < drops.length; i++) {
      const x = (i - columns / 2) * fontSize + canvas.width / 2
      const y = drops[i] * fontSize

      // Draw trail
      for (let j = trails[i].length - 1; j >= 0; j--) {
        const trailItem = trails[i][j]
        const age     = trails[i].length - j
        const opacity = Math.max(0, 1 - (age / 15))
        if (opacity > 0) {
          ctx.fillStyle = `rgba(255, 215, 0, ${opacity * 0.6})`
          ctx.fillText(trailItem.char, trailItem.x, trailItem.y)
        }
      }

      // Draw leader
      const leaderChar = chars[Math.floor(Math.random() * chars.length)]
      ctx.fillStyle = '#FFD700'
      ctx.fillText(leaderChar, x, y)

      trails[i].push({ char: leaderChar, x, y })
      if (trails[i].length > 15) trails[i].shift()

      if (drops[i] * fontSize > canvas.height * 1.5 && Math.random() > 0.99) {
        drops[i] = -20
        trails[i] = []
      }
      drops[i]++
    }

    setTimeout(() => {
      animationId = requestAnimationFrame(draw)
    }, 50)
  }

  draw()
}

async function submit() {
  error.value = ''
  if (!newPassword.value || newPassword.value.length < 6) {
    error.value = 'Password must be at least 6 characters.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  try {
    await authApi.resetPasswordWithToken(accessToken.value, newPassword.value)
    success.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not update password. The link may have expired.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}
.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}
.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}
</style>
