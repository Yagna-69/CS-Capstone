import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import LandingView from '../views/LandingView.vue'
import DashboardView from '../views/DashboardView.vue'
import TradingView from '../views/TradingView.vue'
import SettingsView from '../views/SettingsView.vue'
import LLMView from '../views/LLMView.vue'
import HomeView from '../views/HomeView.vue'
import NewsView from '../views/NewsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'landing',
      component: LandingView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/trading',
      name: 'trading',
      component: TradingView
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    },
    {
      path: '/ai',
      name: 'llm',
      component: LLMView
    },
    {
      path: '/demo',
      name: 'home',
      component: HomeView
    },
    {
      path: '/news',
      name: 'news',
      component: NewsView
    }
  ]
})

const PROTECTED = ['dashboard', 'trading', 'settings', 'llm', 'news']

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (PROTECTED.includes(to.name) && !token) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
