import { defineStore } from 'pinia'
import { ref } from 'vue'
import { llmApi } from '@/services/api'

export const useLlmStore = defineStore('llm', () => {
  const messages = ref([])   // [{ role: 'user'|'assistant', content: string, timestamp: Date }]
  const loading  = ref(false)
  const error    = ref(null)
  
  // Limit context window to last N messages to reduce cost
  const MAX_CONTEXT_MESSAGES = 10  // Keep only last 10 messages (5 exchanges)

  async function sendMessage(content) {
    error.value = null
    messages.value.push({ role: 'user', content, timestamp: new Date() })

    loading.value = true
    try {
      // Only send recent message history to reduce tokens/cost
      const recentMessages = messages.value.slice(-MAX_CONTEXT_MESSAGES)
      const history = recentMessages.map(m => ({ role: m.role, content: m.content }))
      
      const { data } = await llmApi.chat(history)
      messages.value.push({ role: 'assistant', content: data.reply, timestamp: new Date() })
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to get AI response.'
    } finally {
      loading.value = false
    }
  }

  function clearChat() {
    messages.value = []
    error.value = null
  }

  return { messages, loading, error, sendMessage, clearChat }
})
