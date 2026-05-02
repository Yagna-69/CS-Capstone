<template>
  <div class="settings-container">
    <!-- Left Sidebar -->
    <div class="settings-sidebar">
      <h1 class="text-2xl font-bold text-white mb-6 px-6 pt-2">Settings</h1>
      <nav class="settings-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="['settings-tab', { active: activeTab === tab.id }]"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.icon" />
          </svg>
          <span>{{ tab.name }}</span>
        </button>
      </nav>

    </div>

    <div class="settings-divider"></div>

    <!-- Right Content -->
    <div class="settings-content">

      <!-- ── Profile ── -->
      <div v-if="activeTab === 'profile'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">Profile</h2>
        <div class="space-y-6">

          <div class="setting-group">
            <label class="setting-label">Email</label>
            <input type="email" :value="authStore.email" disabled class="setting-input" />
            <p class="setting-description">Your email address cannot be changed</p>
          </div>

          <div class="setting-group">
            <label class="setting-label">Display Name</label>
            <input
              v-model="profileForm.displayName"
              type="text"
              placeholder="Enter display name"
              class="setting-input"
            />
          </div>

          <div class="flex items-center gap-3">
            <button class="btn-primary" :disabled="profileSaving" @click="saveProfile">
              {{ profileSaving ? 'Saving…' : 'Save Changes' }}
            </button>
            <span v-if="profileMsg" :class="msgClass(profileMsg)">{{ profileMsg.text }}</span>
          </div>
        </div>
      </div>

      <!-- ── Preferences ── -->
      <div v-if="activeTab === 'preferences'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">Preferences</h2>
        <div class="space-y-6">

          <div class="setting-group">
            <label class="setting-label">Default Currency</label>
            <select v-model="prefsForm.defaultCurrency" class="setting-input">
              <option v-for="c in currencies" :key="c.code" :value="c.code">{{ c.code }} – {{ c.name }}</option>
            </select>
            <p class="setting-description">Portfolio totals on the dashboard are converted into this currency</p>
          </div>

          <div class="setting-group">
            <label class="setting-label">Time Zone</label>
            <select v-model="prefsForm.timezone" class="setting-input">
              <option value="UTC">UTC</option>
              <option value="US/Eastern">Eastern Time (US)</option>
              <option value="US/Pacific">Pacific Time (US)</option>
              <option value="US/Central">Central Time (US)</option>
              <option value="Europe/London">London (GMT)</option>
              <option value="Europe/Paris">Paris (CET)</option>
              <option value="Asia/Tokyo">Tokyo (JST)</option>
              <option value="Asia/Singapore">Singapore (SGT)</option>
              <option value="Australia/Sydney">Sydney (AEST)</option>
            </select>
            <p class="setting-description">Saved to your account — used for order timestamps</p>
          </div>

          <div class="flex items-center gap-3">
            <button class="btn-primary" :disabled="prefsSaving" @click="savePreferences">
              {{ prefsSaving ? 'Saving…' : 'Save Preferences' }}
            </button>
            <span v-if="prefsMsg" :class="msgClass(prefsMsg)">{{ prefsMsg.text }}</span>
          </div>
        </div>
      </div>

      <!-- ── Notifications ── -->
      <div v-if="activeTab === 'notifications'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">Notifications</h2>
        <div class="space-y-6">

          <div class="setting-toggle">
            <div>
              <h3 class="setting-toggle-title">Trade Confirmation Emails</h3>
              <p class="setting-toggle-description">Send an email to your account address after each completed trade or transfer</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="notifForm.emailNotifications" @change="saveNotifications" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="flex items-center gap-3">
            <button class="btn-secondary" :disabled="emailSending" @click="sendTestEmail">
              {{ emailSending ? 'Sending…' : 'Send Test Email' }}
            </button>
            <span v-if="notifMsg" :class="msgClass(notifMsg)">{{ notifMsg.text }}</span>
          </div>

        </div>
      </div>

      <!-- ── Security ── -->
      <div v-if="activeTab === 'security'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">Security</h2>
        <div class="space-y-6">

          <div class="setting-group">
            <label class="setting-label">Current Password</label>
            <input
              v-model="securityForm.currentPassword"
              type="password"
              placeholder="Enter your current password"
              class="setting-input"
            />
          </div>

          <div class="setting-group">
            <label class="setting-label">New Password</label>
            <input
              v-model="securityForm.newPassword"
              type="password"
              placeholder="Enter new password (min 6 chars)"
              class="setting-input"
            />
          </div>

          <div class="setting-group">
            <label class="setting-label">Confirm New Password</label>
            <input
              v-model="securityForm.confirmPassword"
              type="password"
              placeholder="Confirm new password"
              class="setting-input"
            />
          </div>

          <div class="flex items-center gap-3">
            <button class="btn-primary" :disabled="passwordSaving" @click="changePassword">
              {{ passwordSaving ? 'Updating…' : 'Update Password' }}
            </button>
            <span v-if="passwordMsg" :class="msgClass(passwordMsg)">{{ passwordMsg.text }}</span>
          </div>

          <div class="settings-divider my-2"></div>

          <div>
            <h3 class="text-sm font-semibold text-gray-300 mb-1">Forgot your password?</h3>
            <p class="text-xs text-gray-500 mb-3">We'll send a password reset link to your email address.</p>
            <div class="flex items-center gap-3">
              <button class="btn-secondary" :disabled="resetSending" @click="sendPasswordReset">
                {{ resetSending ? 'Sending…' : 'Send Reset Email' }}
              </button>
              <span v-if="resetMsg" :class="msgClass(resetMsg)">{{ resetMsg.text }}</span>
            </div>
          </div>

          <div class="divider"></div>

          <!-- Sign Out -->
          <div>
            <h3 class="text-sm font-semibold text-gray-300 mb-1">Sign Out</h3>
            <p class="text-xs text-gray-500 mb-3">Log out of your account on this device.</p>
            <button class="btn-danger" @click="handleSignOut">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Sign Out
            </button>
          </div>

        </div>
      </div>

      <!-- ── About ── -->
      <div v-if="activeTab === 'about'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">About</h2>
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-bold text-white mb-1">FXTrade</h3>
            <p class="text-gray-400 text-sm">Version 1.0.0</p>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-widest">Description</h3>
            <p class="text-gray-300 text-sm leading-relaxed">
              FXTrade is a modern forex trading platform designed for traders who want a seamless,
              intuitive experience. Trade currencies, manage your portfolio, and stay updated with
              real-time market news.
            </p>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-widest">Tech Stack</h3>
            <p class="text-gray-300 text-sm">Vue 3, FastAPI, Supabase, yfinance</p>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-widest">Legal</h3>
            <div class="space-y-1">
              <a href="#" class="text-gray-400 hover:text-white text-sm block transition">Terms of Service</a>
              <a href="#" class="text-gray-400 hover:text-white text-sm block transition">Privacy Policy</a>
              <a href="#" class="text-gray-400 hover:text-white text-sm block transition">Cookie Policy</a>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi, preferencesApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useForexStore } from '@/stores/forex'
import { usePrefsStore } from '@/stores/prefs'

const authStore  = useAuthStore()
const prefsStore = usePrefsStore()
const forexStore = useForexStore()
const router     = useRouter()

async function handleSignOut() {
  await authStore.logout()
  router.push('/login')
}
const currencies = computed(() => forexStore.currencies)

const activeTab = ref('profile')

// ── Helpers ──────────────────────────────────────────────────────────────────
function msgClass(msg) {
  return msg?.ok
    ? 'text-sm font-medium text-primary'
    : 'text-sm font-medium text-red-400'
}

function flashMsg(ref_, text, ok, ms = 3500) {
  ref_.value = { text, ok }
  setTimeout(() => { ref_.value = null }, ms)
}

// Scope every localStorage key to the logged-in user so two accounts
// on the same browser never read each other's data.
const uid = authStore.userId || 'anon'
const LS_PROFILE = `fxtrade_profile_${uid}`
const LS_PREFS   = `fxtrade_prefs_local_${uid}`
const LS_NOTIF   = `fxtrade_notif_local_${uid}`

// ── Profile (localStorage) ───────────────────────────────────────────────────
const profileForm = ref({ displayName: '', bio: '' })
const profileSaving = ref(false)
const profileMsg = ref(null)

function loadProfile() {
  try {
    const stored = JSON.parse(localStorage.getItem(LS_PROFILE) || '{}')
    profileForm.value.displayName = stored.displayName || ''
  } catch { /* ignore */ }
}

async function saveProfile() {
  profileSaving.value = true
  try {
    localStorage.setItem(LS_PROFILE, JSON.stringify({ displayName: profileForm.value.displayName }))
    flashMsg(profileMsg, 'Profile saved.', true)
  } catch {
    flashMsg(profileMsg, 'Could not save profile.', false)
  } finally {
    profileSaving.value = false
  }
}

// ── Preferences (backend + localStorage for language/currency) ───────────────
const prefsForm = ref({ defaultCurrency: 'USD', timezone: 'UTC' })
const prefsSaving = ref(false)
const prefsMsg = ref(null)

function loadPrefsLocal() {
  try {
    const local = JSON.parse(localStorage.getItem(LS_PREFS) || '{}')
    if (local.defaultCurrency) prefsForm.value.defaultCurrency = local.defaultCurrency
  } catch { /* ignore */ }
}

async function savePreferences() {
  prefsSaving.value = true
  try {
    await preferencesApi.update({ timezone: prefsForm.value.timezone })
    localStorage.setItem(LS_PREFS, JSON.stringify({
      defaultCurrency: prefsForm.value.defaultCurrency,
    }))
    prefsStore.set(prefsForm.value.defaultCurrency)
    flashMsg(prefsMsg, 'Preferences saved.', true)
  } catch (e) {
    flashMsg(prefsMsg, e.response?.data?.detail || 'Could not save preferences.', false)
  } finally {
    prefsSaving.value = false
  }
}

// ── Notifications ────────────────────────────────────────────────────────────
const notifForm = ref({ emailNotifications: true })
const notifMsg = ref(null)
const emailSending = ref(false)

function loadNotifLocal() {
  try {
    const local = JSON.parse(localStorage.getItem(LS_NOTIF) || '{}')
    if ('emailNotifications' in local) notifForm.value.emailNotifications = local.emailNotifications
  } catch { /* ignore */ }
}

async function saveNotifications() {
  try {
    await preferencesApi.update({ enable_notification: notifForm.value.emailNotifications })
    localStorage.setItem(LS_NOTIF, JSON.stringify({ emailNotifications: notifForm.value.emailNotifications }))
    flashMsg(notifMsg, 'Preferences saved.', true)
  } catch (e) {
    flashMsg(notifMsg, e.response?.data?.detail || 'Could not save.', false)
  }
}

async function sendTestEmail() {
  emailSending.value = true
  try {
    await authApi.sendTestEmail()
    flashMsg(notifMsg, 'Test email sent — check your inbox.', true)
  } catch (e) {
    flashMsg(notifMsg, e.response?.data?.detail || 'Could not send email.', false)
  } finally {
    emailSending.value = false
  }
}

// ── Security ──────────────────────────────────────────────────────────────────
const securityForm = ref({ currentPassword: '', newPassword: '', confirmPassword: '' })
const passwordSaving = ref(false)
const passwordMsg = ref(null)
const resetSending = ref(false)
const resetMsg = ref(null)

async function changePassword() {
  const { currentPassword, newPassword, confirmPassword } = securityForm.value
  if (!currentPassword) return flashMsg(passwordMsg, 'Enter your current password.', false)
  if (!newPassword) return flashMsg(passwordMsg, 'Enter a new password.', false)
  if (newPassword.length < 6) return flashMsg(passwordMsg, 'Password must be at least 6 characters.', false)
  if (newPassword !== confirmPassword) return flashMsg(passwordMsg, 'Passwords do not match.', false)
  passwordSaving.value = true
  try {
    await authApi.changePassword(currentPassword, newPassword)
    securityForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
    flashMsg(passwordMsg, 'Password updated successfully.', true)
  } catch (e) {
    flashMsg(passwordMsg, e.response?.data?.detail || 'Could not update password.', false)
  } finally {
    passwordSaving.value = false
  }
}

async function sendPasswordReset() {
  resetSending.value = true
  try {
    await authApi.sendPasswordReset(authStore.email)
    flashMsg(resetMsg, `Reset link sent to ${authStore.email}.`, true)
  } catch (e) {
    flashMsg(resetMsg, e.response?.data?.detail || 'Could not send reset email.', false)
  } finally {
    resetSending.value = false
  }
}

// ── Mount: load everything ────────────────────────────────────────────────────
onMounted(async () => {
  loadProfile()
  loadPrefsLocal()
  prefsStore.set(prefsForm.value.defaultCurrency)
  loadNotifLocal()
  try {
    const { data } = await preferencesApi.get()
    if (data.timezone) prefsForm.value.timezone = data.timezone
    if ('enable_notification' in data) notifForm.value.emailNotifications = data.enable_notification
  } catch { /* preferences may not exist yet */ }
})

const tabs = [
  { id: 'profile',       name: 'Profile',       icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
  { id: 'preferences',   name: 'Preferences',   icon: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4' },
  { id: 'notifications', name: 'Notifications', icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
  { id: 'security',      name: 'Security',      icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
  { id: 'about',         name: 'About',         icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
]
</script>

<style scoped>
.settings-container {
  display: grid;
  grid-template-columns: 1fr;
  min-height: calc(100vh - 120px);
  background: rgba(255, 255, 255, 0.01);
  border-radius: 1rem;
  overflow: hidden;
}

@media (min-width: 1024px) {
  .settings-container {
    grid-template-columns: 30% 1px 1fr;
  }
}

.settings-sidebar {
  padding: 1.5rem 0;
  background: rgba(255, 255, 255, 0.02);
}

.settings-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.settings-tab {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  text-align: left;
  color: #9ca3af;
  font-weight: 500;
  font-size: 0.9375rem;
  transition: all 0.2s;
  border: none;
  background: transparent;
  cursor: pointer;
  position: relative;
  width: 100%;
}

.settings-tab::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  transition: background 0.2s;
}

.settings-tab:hover { color: #ffffff; background: rgba(255, 255, 255, 0.03); }
.settings-tab.active { color: #FFD700; background: rgba(255, 215, 0, 0.08); }
.settings-tab.active::before { background: #FFD700; }


.settings-divider {
  display: none;
  background: rgba(255, 255, 255, 0.08);
  width: 1px;
}

@media (min-width: 1024px) {
  .settings-divider { display: block; }
}

.settings-content {
  padding: 2rem;
  overflow-y: auto;
}

@media (min-width: 1024px) {
  .settings-content { padding: 2.5rem 3rem; }
}

.content-section { max-width: 640px; }

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #d1d5db;
}

.setting-input {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  transition: all 0.2s;
  width: 100%;
}

.setting-input:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1);
}

.setting-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* make select options dark */
.setting-input option {
  background: #0a0a0a;
  color: white;
}

.setting-description {
  font-size: 0.75rem;
  color: #6b7280;
}

.setting-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  transition: all 0.2s;
}

.setting-toggle:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
}

.setting-toggle-title { font-size: 0.9375rem; font-weight: 600; color: white; margin-bottom: 0.25rem; }
.setting-toggle-description { font-size: 0.8125rem; color: #9ca3af; }

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
}

.toggle-switch input { opacity: 0; width: 0; height: 0; }

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #374151;
  transition: 0.3s;
  border-radius: 26px;
}

.toggle-slider:before {
  position: absolute;
  content: '';
  height: 20px; width: 20px;
  left: 3px; bottom: 3px;
  background: white;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle-switch input:checked + .toggle-slider { background: #FFD700; }
.toggle-switch input:checked + .toggle-slider:before { transform: translateX(22px); background: #000; }

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #FFD700;
  color: black;
  font-weight: 700;
  border-radius: 9999px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.btn-primary:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: transparent;
  color: #FFD700;
  font-weight: 600;
  border-radius: 9999px;
  border: 1px solid rgba(255, 215, 0, 0.4);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.btn-secondary:hover:not(:disabled) { border-color: #FFD700; background: rgba(255, 215, 0, 0.08); }
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: transparent;
  color: #f87171;
  font-weight: 600;
  border-radius: 9999px;
  border: 1px solid rgba(239, 68, 68, 0.35);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}
.btn-danger:hover { background: rgba(239, 68, 68, 0.08); border-color: #ef4444; color: #fca5a5; }

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 1.5rem 0;
}
</style>
