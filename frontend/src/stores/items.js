import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

export const useItemsStore = defineStore('items', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchItems() {
    loading.value = true
    error.value = null
    try {
      const response = await api.getItems()
      items.value = response.data
    } catch (e) {
      error.value = e.message
      console.error('Error fetching items:', e)
    } finally {
      loading.value = false
    }
  }

  async function addItem(item) {
    loading.value = true
    error.value = null
    try {
      const response = await api.createItem(item)
      items.value.push(response.data[0])
    } catch (e) {
      error.value = e.message
      console.error('Error creating item:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    loading,
    error,
    fetchItems,
    addItem
  }
})
