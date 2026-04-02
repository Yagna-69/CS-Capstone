<template>
  <div 
    class="news-card glass rounded-xl overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer"
    :class="{ 'featured-card': featured }"
    @click="handleClick"
  >
    <!-- Image Container -->
    <div class="image-container">
      <img 
        :src="story.image" 
        :alt="story.headline"
        class="w-full h-full object-cover"
        loading="lazy"
      />
      <div class="image-overlay"></div>
    </div>

    <!-- Footer with Headline and Date -->
    <div class="card-footer">
      <h3 class="headline" :class="{ 'headline-featured': featured }">
        {{ story.headline }}
      </h3>
      <div class="date-container">
        <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span class="date-text">{{ formattedDate }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  story: {
    type: Object,
    required: true
  },
  featured: {
    type: Boolean,
    default: false
  }
})

const formattedDate = computed(() => {
  const date = new Date(props.story.date)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  })
})

const handleClick = () => {
  if (props.story.url) {
    window.open(props.story.url, '_blank', 'noopener')
  } else {
    console.log('News story clicked:', props.story.id)
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
  transform: translateY(-2px);
}

.news-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.image-container {
  position: relative;
  width: 100%;
  flex: 1;
  min-height: 200px;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  overflow: hidden;
}

.featured-card .image-container {
  min-height: 100%;
  position: relative;
}

.image-container img {
  transition: transform 0.3s ease;
}

.news-card:hover .image-container img {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(to bottom, transparent, rgba(0, 0, 0, 0.7));
  pointer-events: none;
}

.card-footer {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 10;
}

.featured-card .card-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 2rem 1.5rem 1.5rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.95), transparent);
}

.headline {
  font-size: 0.95rem;
  font-weight: 600;
  color: white;
  line-height: 1.4;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.headline-featured {
  font-size: 1.1rem;
  -webkit-line-clamp: 3;
}

.date-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-text {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
}

/* Responsive adjustments */
@media (min-width: 768px) {
  .headline {
    font-size: 1rem;
  }
  
  .headline-featured {
    font-size: 1.25rem;
    -webkit-line-clamp: 4;
  }
  
  .date-text {
    font-size: 0.8rem;
  }
}

@media (min-width: 1024px) {
  .card-footer {
    padding: 1.25rem;
  }
  
  .headline-featured {
    font-size: 1.5rem;
  }
}
</style>
