<template>
  <div class="mb-8">
    <h2 class="text-4xl font-bold text-primary mb-4 font-goldman">{{ title }}</h2>

    <div v-if="loading" class="glass p-6 rounded-xl">
      <div class="text-sm text-gray-300">Loading {{ title }} posts...</div>
    </div>
    <div v-else-if="error" class="glass p-6 rounded-xl">
      <div class="text-sm text-red-400">{{ error }}</div>
    </div>

    <div v-else-if="posts.length > 0" class="relative">
      <button
        v-if="currentIndex > 0"
        type="button"
        class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 p-3 bg-bg-secondary/90 hover:bg-primary/20 rounded-full transition-colors border border-gray-700 hover:border-primary shadow-lg"
        @click="manualPrevSlide"
      >
        <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <button
        v-if="currentIndex + 3 < posts.length"
        type="button"
        class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 p-3 bg-bg-secondary/90 hover:bg-primary/20 rounded-full transition-colors border border-gray-700 hover:border-primary shadow-lg"
        @click="manualNextSlide"
      >
        <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a
          v-for="post in visiblePosts"
          :key="post.id"
          :href="post.url"
          target="_blank"
          rel="noopener noreferrer"
          class="reddit-carousel-card glass rounded-xl overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer group"
        >
          <div
            class="reddit-carousel-image relative w-full"
            :style="post.thumbnail ? {} : { background: 'radial-gradient(circle at center, rgba(255, 215, 0, 0.15) 0%, rgba(26, 26, 26, 0.95) 70%)' }"
          >
            <img
              v-if="post.thumbnail"
              :src="post.thumbnail"
              alt=""
              referrerpolicy="no-referrer"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              @error="onCarouselImgError"
            />
            <div v-else class="flex items-center justify-center h-full">
              <svg class="w-12 h-12 text-primary/30" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
              </svg>
            </div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
          </div>

          <div class="p-4 bg-bg-primary/80 backdrop-blur-sm relative">
            <div class="flex items-start justify-between gap-2 mb-2">
              <span v-if="post.flair" class="inline-block px-2 py-0.5 bg-primary/20 text-primary text-xs font-semibold rounded flex-shrink-0">
                {{ post.flair }}
              </span>
              <span class="text-xs text-gray-500 flex-shrink-0">{{ post.time }}</span>
            </div>

            <h3 class="text-sm font-bold text-white mb-2 line-clamp-2 leading-tight group-hover:text-primary transition-colors">
              {{ post.title }}
            </h3>

            <div class="flex items-center justify-between text-xs text-gray-500">
              <div class="flex items-center gap-3">
                <span class="flex items-center gap-1">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                  </svg>
                  {{ post.score }}
                </span>
                <span class="flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  {{ post.num_comments }}
                </span>
              </div>
              <span class="text-xs">u/{{ post.author }}</span>
            </div>
          </div>
        </a>
      </div>

      <div v-if="posts.length > 3" class="flex justify-center gap-2 mt-4">
        <button
          v-for="pageIndex in Math.ceil(posts.length / 3)"
          :key="pageIndex"
          type="button"
          :class="[
            'h-2 rounded-full transition-all',
            Math.floor(currentIndex / 3) === pageIndex - 1
              ? 'bg-primary w-8'
              : 'bg-gray-600 hover:bg-gray-500 w-2'
          ]"
          @click="currentIndex = (pageIndex - 1) * 3"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  posts: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null },
})

const currentIndex = ref(0)
let autoRotateTimer = null

const visiblePosts = computed(() =>
  props.posts.slice(currentIndex.value, currentIndex.value + 3)
)

function nextSlide() {
  if (currentIndex.value + 3 < props.posts.length) {
    currentIndex.value += 3
  } else {
    currentIndex.value = 0
  }
}

function prevSlide() {
  if (currentIndex.value > 0) {
    currentIndex.value -= 3
  } else {
    const totalPages = Math.ceil(props.posts.length / 3)
    currentIndex.value = (totalPages - 1) * 3
  }
}

function stopAutoRotate() {
  if (autoRotateTimer) {
    clearInterval(autoRotateTimer)
    autoRotateTimer = null
  }
}

function startAutoRotate() {
  stopAutoRotate()
  if (props.posts.length > 3) {
    autoRotateTimer = setInterval(nextSlide, 8000)
  }
}

function manualNextSlide() {
  stopAutoRotate()
  nextSlide()
  setTimeout(startAutoRotate, 15000)
}

function manualPrevSlide() {
  stopAutoRotate()
  prevSlide()
  setTimeout(startAutoRotate, 15000)
}

/** Reddit preview CDN often 403s with a third-party Referer; strip ?params once on error. */
function onCarouselImgError(ev) {
  const el = ev.target
  if (!(el instanceof HTMLImageElement) || el.dataset.fallbackDone) return
  const src = el.currentSrc || el.src
  if (!src?.includes('?')) return
  el.dataset.fallbackDone = '1'
  el.src = src.split('?')[0]
}

watch(
  () => [props.posts.length, props.loading],
  () => {
    currentIndex.value = 0
    stopAutoRotate()
    if (!props.loading && props.posts.length > 0) {
      startAutoRotate()
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  stopAutoRotate()
})
</script>

<style scoped>
.reddit-carousel-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.reddit-carousel-card:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 215, 0, 0.3);
  transform: translateY(-2px);
}

.reddit-carousel-image {
  height: 180px;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  overflow: hidden;
  position: relative;
}

@media (min-width: 768px) {
  .reddit-carousel-image {
    height: 200px;
  }
}

@media (min-width: 1024px) {
  .reddit-carousel-image {
    height: 220px;
  }
}
</style>
