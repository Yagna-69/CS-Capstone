<template>
  <div class="min-h-screen flex">
    <!-- Matrix Background (70%) -->
    <div class="hidden lg:flex lg:w-[70%] bg-black relative overflow-hidden">
      <canvas ref="matrixCanvas" class="absolute inset-0 w-full h-full"></canvas>
    </div>

    <!-- Login Form (30%) -->
    <div class="w-full lg:w-[30%] flex items-center justify-center bg-bg-secondary p-8 overflow-hidden">
      <div class="w-full max-w-md">
        <!-- Title -->
        <div class="flex flex-col items-center justify-center mb-8">
          <RouterLink to="/" class="text-6xl font-bold font-goldman text-primary hover:opacity-80 transition">FXTrade</RouterLink>
        </div>

        <!-- Login/Signup Toggle with Transition -->
        <Transition name="slide-fade" mode="out-in">
          <!-- Login Form -->
          <div v-if="!isSignup" key="login">
            <h2 class="text-2xl font-bold text-white text-center mb-8">Log in to your account</h2>

            <form @submit.prevent="handleLogin" class="space-y-4">
              <!-- Email -->
              <div class="relative">
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
                </svg>
                <input
                  v-model="email"
                  type="email"
                  placeholder="Enter your email"
                  required
                  class="w-full pl-12 pr-4 py-3.5 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary transition"
                />
              </div>

              <!-- Password -->
              <div class="relative">
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Password"
                  required
                  class="w-full pl-12 pr-12 py-3.5 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary transition"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  <svg v-if="!showPassword" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                  <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                  </svg>
                </button>
              </div>

              <!-- Login Button -->
              <button
                type="submit"
                :disabled="loading"
                class="w-full py-3.5 bg-primary text-black rounded-full font-bold hover:bg-primary-dark transition disabled:opacity-50 mt-6 relative"
              >
                <span v-if="!loading">Log In</span>
                <span v-else class="flex items-center justify-center gap-2">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Logging in...
                </span>
              </button>

              <!-- Forgot Password -->
              <div class="text-center pt-2">
                <a href="#" class="text-sm text-gray-400 hover:text-white transition">Forgot password?</a>
              </div>
            </form>

            <!-- Switch to Signup -->
            <div class="mt-8 pt-6 border-t border-gray-700">
              <p class="text-center text-gray-400 mb-4">Don't have an account?</p>
              <button
                @click="goToSignup"
                class="w-full py-3.5 border-2 border-primary text-primary rounded-full font-bold hover:bg-primary hover:text-black transition"
              >
                Create Account
              </button>
            </div>
          </div>

          <!-- Signup Form -->
          <div v-else key="signup">
            <h2 class="text-2xl font-bold text-white text-center mb-8">Create your account</h2>

            <form @submit.prevent="handleSignup" class="space-y-4">
              <!-- Email -->
              <div class="relative">
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
                </svg>
                <input
                  v-model="email"
                  type="email"
                  placeholder="Enter your email"
                  required
                  class="w-full pl-12 pr-4 py-3.5 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary transition"
                />
              </div>

              <!-- Password -->
              <div class="relative">
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Password"
                  required
                  class="w-full pl-12 pr-12 py-3.5 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary transition"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  <svg v-if="!showPassword" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <input
                  v-model="confirmPassword"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Confirm password"
                  required
                  class="w-full pl-12 pr-4 py-3.5 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary transition"
                />
              </div>

              <!-- Signup Button -->
              <button
                type="submit"
                :disabled="loading"
                class="w-full py-3.5 bg-primary text-black rounded-full font-bold hover:bg-primary-dark transition disabled:opacity-50 mt-6 relative"
              >
                <span v-if="!loading">Create Account</span>
                <span v-else class="flex items-center justify-center gap-2">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating account...
                </span>
              </button>
            </form>

            <!-- Switch to Login -->
            <div class="mt-8 pt-6 border-t border-gray-700">
              <p class="text-center text-gray-400 mb-4">Already have an account?</p>
              <button
                @click="goToLogin"
                class="w-full py-3.5 border-2 border-primary text-primary rounded-full font-bold hover:bg-primary hover:text-black transition"
              >
                Log In
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const loading = ref(false)
const matrixCanvas = ref(null)
const isSignup = ref(false)  // Toggle between login/signup
let animationId = null

onMounted(() => {
  const canvas = matrixCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight

  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // Rotate 45 degrees
  ctx.save()
  ctx.translate(canvas.width / 2, canvas.height / 2)
  ctx.rotate(45 * Math.PI / 180)
  ctx.translate(-canvas.width / 2, -canvas.height / 2)

  const chars = '¥$€£₹₽¢₩₪₴฿₦₡₵₲₱₸₹₺₼₽₾₿'
  const fontSize = 64
  const columns = Math.ceil(canvas.width * 1.5 / fontSize)
  const drops = []
  const trails = []
  
  for (let i = 0; i < columns; i++) {
    drops[i] = Math.random() * -50
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

    ctx.font = `${fontSize}px monospace`
    ctx.shadowBlur = 0

    for (let i = 0; i < drops.length; i++) {
      const x = (i - columns / 2) * fontSize + canvas.width / 2
      const y = drops[i] * fontSize
      
      // Draw trail
      for (let j = trails[i].length - 1; j >= 0; j--) {
        const trailItem = trails[i][j]
        const age = trails[i].length - j
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
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})

function goToSignup() {
  isSignup.value = true
  email.value = ''
  password.value = ''
  confirmPassword.value = ''
}

function goToLogin() {
  isSignup.value = false
  email.value = ''
  password.value = ''
  confirmPassword.value = ''
}

async function handleSignup() {
  if (!email.value || !password.value || !confirmPassword.value) {
    alert('Please fill in all fields')
    return
  }
  
  if (password.value !== confirmPassword.value) {
    alert('Passwords do not match')
    return
  }

  loading.value = true
  
  setTimeout(() => {
    loading.value = false
    alert(`Account created for: ${email.value}`)
    router.push('/')
  }, 1000)
}

async function handleLogin() {
  if (!email.value || !password.value) {
    alert('Please enter email and password')
    return
  }

  loading.value = true
  
  setTimeout(() => {
    loading.value = false
    alert(`Login attempted with email: ${email.value}`)
    router.push('/')
  }, 1000)
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

/* Input animations */
input {
  transition: all 0.3s ease;
}

input:focus {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.15);
}

/* Button animations */
button[type="submit"] {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.3);
}

button[type="submit"]:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.2);
}

/* Ripple effect on button click */
button[type="submit"]::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

button[type="submit"]:active::after {
  width: 300px;
  height: 300px;
}

/* Border button animations */
button[type="button"] {
  transition: all 0.3s ease;
}

button[type="button"]:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.2);
}

/* Icon animations */
svg {
  transition: all 0.3s ease;
}

input:focus ~ svg,
input:focus + div svg {
  color: #FFD700;
  transform: scale(1.1);
}

/* Loading animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

button:disabled svg {
  animation: spin 1s linear infinite;
}

/* Form container animation */
form {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Password toggle button animation */
button[type="button"].absolute:hover svg {
  transform: scale(1.15);
}

/* Input error shake */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.shake {
  animation: shake 0.4s ease;
}

/* Pulse animation for primary button */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 215, 0, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 215, 0, 0);
  }
}

button[type="submit"]:not(:disabled):hover {
  animation: pulse 1.5s infinite;
}

/* Currency scroll animation */
@keyframes scroll-left {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-33.33%);
  }
}

.currency-scroll {
  display: inline-block;
  animation: scroll-left 15s linear infinite;
  letter-spacing: 0.15em;
}
</style>
