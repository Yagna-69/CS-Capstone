<template>
  <div class="settings-container">
    <!-- Left Sidebar - 30% -->
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

    <!-- Vertical Divider -->
    <div class="settings-divider"></div>

    <!-- Right Content - 70% -->
    <div class="settings-content">
      <!-- Profile Tab -->
      <div v-if="activeTab === 'profile'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">Profile</h2>
        
        <div class="space-y-6">
          <div class="setting-group">
            <label class="setting-label">Email</label>
            <input
              type="email"
              value="user@example.com"
              disabled
              class="setting-input"
            />
            <p class="setting-description">Your email address cannot be changed</p>
          </div>

          <div class="setting-group">
            <label class="setting-label">Display Name</label>
            <input
              type="text"
              placeholder="Enter display name"
              class="setting-input"
            />
          </div>

          <div class="setting-group">
            <label class="setting-label">Bio</label>
            <textarea
              placeholder="Tell us about yourself"
              rows="4"
              class="setting-input"
            ></textarea>
          </div>

          <button class="btn-primary">Save Changes</button>
        </div>
      </div>

      <!-- Preferences Tab -->
      <div v-if="activeTab === 'preferences'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">Preferences</h2>
        
        <div class="space-y-6">
          <div class="setting-group">
            <label class="setting-label">Default Currency</label>
            <select class="setting-input">
              <option v-for="c in currencies" :key="c.code" :value="c.code">{{ c.code }} - {{ c.name }}</option>
            </select>
          </div>

          <div class="setting-group">
            <label class="setting-label">Language</label>
            <select class="setting-input">
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>

          <div class="setting-group">
            <label class="setting-label">Time Zone</label>
            <select class="setting-input">
              <option value="UTC">UTC</option>
              <option value="EST">Eastern Time</option>
              <option value="PST">Pacific Time</option>
              <option value="GMT">GMT</option>
            </select>
          </div>

          <button class="btn-primary">Save Preferences</button>
        </div>
      </div>

      <!-- Notifications Tab -->
      <div v-if="activeTab === 'notifications'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">Notifications</h2>
        
        <div class="space-y-4">
          <div class="setting-toggle">
            <div>
              <h3 class="setting-toggle-title">Price Alerts</h3>
              <p class="setting-toggle-description">Receive alerts when prices hit your targets</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" checked />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-toggle">
            <div>
              <h3 class="setting-toggle-title">Trade Confirmations</h3>
              <p class="setting-toggle-description">Get notified when trades are executed</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" checked />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-toggle">
            <div>
              <h3 class="setting-toggle-title">Market News</h3>
              <p class="setting-toggle-description">Stay updated with forex market news</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-toggle">
            <div>
              <h3 class="setting-toggle-title">Email Notifications</h3>
              <p class="setting-toggle-description">Receive notifications via email</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" checked />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- Security Tab -->
      <div v-if="activeTab === 'security'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">Security</h2>
        
        <div class="space-y-6">
          <div class="setting-group">
            <label class="setting-label">Current Password</label>
            <input
              type="password"
              placeholder="Enter current password"
              class="setting-input"
            />
          </div>

          <div class="setting-group">
            <label class="setting-label">New Password</label>
            <input
              type="password"
              placeholder="Enter new password"
              class="setting-input"
            />
          </div>

          <div class="setting-group">
            <label class="setting-label">Confirm New Password</label>
            <input
              type="password"
              placeholder="Confirm new password"
              class="setting-input"
            />
          </div>

          <button class="btn-primary">Update Password</button>

          <div class="divider"></div>

          <div class="setting-toggle">
            <div>
              <h3 class="setting-toggle-title">Two-Factor Authentication</h3>
              <p class="setting-toggle-description">Add an extra layer of security to your account</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="divider"></div>

          <div class="setting-toggle">
            <div>
              <h3 class="setting-toggle-title">Enable Admin</h3>
              <p class="setting-toggle-description">Grant admin access to manage LLM API keys</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" :checked="isAdmin" @change="toggleAdmin" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- About Tab -->
      <div v-if="activeTab === 'about'" class="content-section">
        <h2 class="text-2xl font-bold text-white mb-6">About</h2>
        
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-bold text-white mb-2">FXTrade</h3>
            <p class="text-gray-400 text-sm">Version 1.0.0</p>
          </div>

          <div>
            <h3 class="text-sm font-semibold text-gray-400 mb-2">DESCRIPTION</h3>
            <p class="text-gray-300 text-sm leading-relaxed">
              FXTrade is a modern forex trading platform designed for traders who want a seamless, 
              intuitive experience. Trade currencies, manage your portfolio, and stay updated with 
              real-time market news.
            </p>
          </div>

          <div>
            <h3 class="text-sm font-semibold text-gray-400 mb-2">SUPPORT</h3>
            <a href="#" class="text-primary hover:text-primary/80 text-sm">Visit Help Center →</a>
          </div>

          <div>
            <h3 class="text-sm font-semibold text-gray-400 mb-2">LEGAL</h3>
            <div class="space-y-1">
              <a href="#" class="text-gray-400 hover:text-white text-sm block">Terms of Service</a>
              <a href="#" class="text-gray-400 hover:text-white text-sm block">Privacy Policy</a>
              <a href="#" class="text-gray-400 hover:text-white text-sm block">Cookie Policy</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { preferencesApi } from '@/services/api'
import { useForexStore } from '@/stores/forex'

const activeTab = ref('profile')
const isAdmin = ref(false)
const forexStore = useForexStore()
const currencies = computed(() => forexStore.currencies)

onMounted(async () => {
  try {
    const { data } = await preferencesApi.get()
    isAdmin.value = !!data.is_admin
  } catch {
    // preferences may not have is_admin yet
  }
  // Currencies are auto-loaded by forex store pipeline
})

async function toggleAdmin() {
  const newValue = !isAdmin.value
  try {
    await preferencesApi.update({ is_admin: newValue })
    isAdmin.value = newValue
  } catch {
    // revert — keep isAdmin unchanged
  }
}

const tabs = [
  {
    id: 'profile',
    name: 'Profile',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
  },
  {
    id: 'preferences',
    name: 'Preferences',
    icon: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4'
  },
  {
    id: 'notifications',
    name: 'Notifications',
    icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9'
  },
  {
    id: 'security',
    name: 'Security',
    icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z'
  },
  {
    id: 'about',
    name: 'About',
    icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
  }
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

/* Sidebar - 30% */
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

.settings-tab:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.03);
}

.settings-tab.active {
  color: #FFD700;
  background: rgba(255, 215, 0, 0.08);
}

.settings-tab.active::before {
  background: #FFD700;
}

/* Divider */
.settings-divider {
  display: none;
  background: rgba(255, 255, 255, 0.08);
  width: 1px;
}

@media (min-width: 1024px) {
  .settings-divider {
    display: block;
  }
}

/* Content Area - 70% */
.settings-content {
  padding: 2rem;
  overflow-y: auto;
}

@media (min-width: 1024px) {
  .settings-content {
    padding: 2.5rem 3rem;
  }
}

.content-section {
  max-width: 640px;
}

/* Form Elements */
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

.setting-description {
  font-size: 0.75rem;
  color: #6b7280;
}

/* Toggle Switch */
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

.setting-toggle-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
}

.setting-toggle-description {
  font-size: 0.8125rem;
  color: #9ca3af;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #374151;
  transition: 0.3s;
  border-radius: 26px;
}

.toggle-slider:before {
  position: absolute;
  content: '';
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background: white;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle-switch input:checked + .toggle-slider {
  background: #FFD700;
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(22px);
  background: #000;
}

/* Buttons */
.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #FFD700;
  color: black;
  font-weight: 700;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* Divider */
.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 1.5rem 0;
}
</style>
