<template>
  <div class="container mx-auto px-0 py-0">
    <!-- <h1 class="text-6xl font-bold font-goldman text-primary mb-8">Dashboard</h1>
    
    <!-- Adaptive Bento Box Layout -->
    <div class="dashboard-grid">
      <!-- Portfolio Widget - Always the largest -->
      <div 
        class="portfolio-area glass p-6 rounded-xl hover:shadow-xl widget-card"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <div 
              draggable="true"
              @dragstart="handleDragStart($event, 'portfolio')"
              @dragend="handleDragEnd"
              class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
            >
              <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-white">Portfolio</h2>
          </div>
        </div>
        <div class="h-64 bg-bg-primary rounded-lg flex items-center justify-center">
        </div>
      </div>

      <!-- Adaptive Widgets Container -->
      <div class="adaptive-widgets">
        <template v-for="widgetId in sideWidgets" :key="widgetId">
          <!-- Wishlist Widget -->
          <div 
            v-if="widgetId === 'wishlist'"
            @dragover.prevent="handleDragOver($event, 'wishlist')"
            @drop="handleDrop($event, 'wishlist')"
            :class="`glass p-6 rounded-xl hover:shadow-xl widget-card ${
              draggedWidget === 'wishlist' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'wishlist')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Wishlist</h2>
              </div>
            </div>
            <div class="space-y-2">
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
            </div>
          </div>

          <!-- Feed Widget -->
          <div 
            v-else-if="widgetId === 'feed'"
            @dragover.prevent="handleDragOver($event, 'feed')"
            @drop="handleDrop($event, 'feed')"
            :class="`glass p-6 rounded-xl hover:shadow-xl widget-card ${
              draggedWidget === 'feed' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'feed')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Feed</h2>
              </div>
            </div>
            <div class="space-y-2">
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-primary rounded-lg animate-pulse"></div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Portfolio is always main, only side widgets can be reordered
const sideWidgets = ref(['wishlist', 'feed'])
const draggedWidget = ref(null)

const handleDragStart = (event, widgetId) => {
  // Only allow dragging side widgets
  if (widgetId === 'portfolio') return
  
  draggedWidget.value = widgetId
  event.dataTransfer.effectAllowed = 'move'
}

const handleDragOver = (event, widgetId) => {
  event.preventDefault()
  
  if (!draggedWidget.value || draggedWidget.value === widgetId || draggedWidget.value === 'portfolio') {
    return
  }
  
  // Live reorder side widgets
  const newOrder = [...sideWidgets.value]
  const dragIndex = newOrder.indexOf(draggedWidget.value)
  const dropIndex = newOrder.indexOf(widgetId)
  
  // Remove from current position
  newOrder.splice(dragIndex, 1)
  
  // Insert at new position
  newOrder.splice(dropIndex, 0, draggedWidget.value)
  
  sideWidgets.value = newOrder
}

const handleDrop = (event, widgetId) => {
  event.preventDefault()
  
  // Save to localStorage
  localStorage.setItem('sideWidgetOrder', JSON.stringify(sideWidgets.value))
  
  draggedWidget.value = null
}

const handleDragEnd = () => {
  draggedWidget.value = null
}

// Load saved state
const savedOrder = localStorage.getItem('sideWidgetOrder')
if (savedOrder) {
  try {
    sideWidgets.value = JSON.parse(savedOrder)
  } catch (e) {
    console.error('Failed to load widget order', e)
  }
}
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.glass:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 215, 0, 0.2);
}

/* Adaptive Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 2fr 1fr;
    grid-template-rows: auto;
    gap: 1rem;
  }
  
  .portfolio-area {
    grid-row: span 2;
    min-height: 500px;
  }
  
  .adaptive-widgets {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .adaptive-widgets > div {
    flex: 1;
    min-height: 240px;
  }
}

/* Smooth transitions */
.widget-card {
  transition: all 0.3s ease;
}

/* Placeholder for dragged widget */
.dragging-placeholder {
  opacity: 0.3;
  border: 2px dashed rgba(255, 215, 0, 0.5);
}

/* Drag handle */
.drag-handle {
  transition: all 0.2s ease;
}

.drag-handle:hover {
  transform: scale(1.1);
}
</style>
