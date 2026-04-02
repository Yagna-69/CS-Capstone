<template>
  <div class="container mx-auto px-0 py-0">
    <!-- Search Bar -->
    <div class="mb-6">
      <div class="flex gap-2">
        <input
          v-model="searchQuery"
          @keyup.enter="performSearch"
          type="text"
          placeholder="Search financial news (e.g., 'bitcoin', 'fed rates', 'oil prices')..."
          class="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          @click="performSearch"
          class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          Search
        </button>
        <button
          v-if="searchQuery"
          @click="clearSearch"
          class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
        >
          Clear
        </button>
      </div>
    </div>

    <div class="mb-4">
      <p v-if="loading" class="text-sm text-gray-300">Loading world news...</p>
      <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
    </div>

    <!-- Bento Box Grid - Top Featured Stories -->
    <div class="bento-grid mb-6">
      <NewsStoryCard
        v-for="story in featuredStories"
        :key="story.id"
        :story="story"
        :featured="true"
        :class="story.size"
      />
    </div>

    <!-- Regular News Stories Grid -->
    <div v-if="!loading && !error && !featuredStories.length && !regularStories.length" class="text-center text-gray-400 py-20">
      No news available right now. Try again in a moment.
    </div>

    <div class="news-grid">
      <NewsStoryCard
        v-for="story in regularStories"
        :key="story.id"
        :story="story"
      />
    </div>

    <!-- Load More Button -->
    <div v-if="currentSearchQuery && !loading && regularStories.length > 0" class="flex justify-center mt-8 mb-8">
      <button
        @click="loadMoreNews"
        class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
      >
        Load More Articles
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NewsStoryCard from '@/components/NewsStoryCard.vue'
import { newsApi } from '@/services/api'

const featuredStories = ref([])
const regularStories = ref([])
const error = ref(null)
const loading = ref(false)
const searchQuery = ref('')
const currentSearchQuery = ref(null)  // Track active search for Load More button
const moreCount = ref(0)  // Track how many "load more" calls have been made

async function loadNews(query = null) {
  loading.value = true
  error.value = null
  moreCount.value = 0  // Reset pagination

  try {
    let allArticles = []

    if (query) {
      // Search with user query
      currentSearchQuery.value = query
      const { data } = await newsApi.getNews(undefined, 9, query)
      if (data.status === 'ok' && data.articles) {
        allArticles = data.articles
      }
    } else {
      // Default: Get forex news
      currentSearchQuery.value = null
      const { data } = await newsApi.getNews(undefined, 9, "forex")
      if (data.status === 'ok' && data.articles) {
        allArticles = data.articles
      }
    }

    const articles = allArticles.map((article, index) => ({
      id: article.id || `${index}`,
      headline: article.headline || article.title || 'Untitled',
      date: article.date || '',
      image: article.image || 'https://placehold.co/400x300/1a1a1a/FFD700?text=No+Image',
      url: article.url,
      size: index === 0 ? 'large' : index <= 2 ? 'medium' : undefined,
      source: article.source,
    }))

    featuredStories.value = articles.slice(0, 3)
    regularStories.value = articles.slice(3)
  } catch (err) {
    const status = err.response?.status
    const serverDetail = err.response?.data?.detail || err.response?.data?.message
    error.value = serverDetail || `Unable to load news${status ? ` (HTTP ${status})` : ''}.`
  } finally {
    loading.value = false
  }
}

function performSearch() {
  if (searchQuery.value.trim()) {
    loadNews(searchQuery.value.trim())
  }
}

function clearSearch() {
  searchQuery.value = ''
  loadNews()
}

async function loadMoreNews() {
  if (!currentSearchQuery.value) return
  
  loading.value = true
  error.value = null
  moreCount.value += 1

  try {
    const { data } = await newsApi.getNews(undefined, 9, currentSearchQuery.value)
    
    if (data.status !== 'ok' || !data.articles) {
      error.value = 'No more articles available'
      return
    }

    // Convert and append new articles
    const articles = data.articles.map((article, index) => ({
      id: article.id || `more-${moreCount.value}-${index}`,
      headline: article.headline || article.title || 'Untitled',
      date: article.date || '',
      image: article.image || 'https://placehold.co/400x300/1a1a1a/FFD700?text=No+Image',
      url: article.url,
      source: article.source,
    }))

    // Append to regular stories (don't change featured)
    regularStories.value.push(...articles)
  } catch (err) {
    const status = err.response?.status
    const serverDetail = err.response?.data?.detail || err.response?.data?.message
    error.value = serverDetail || `Unable to load more news${status ? ` (HTTP ${status})` : ''}.`
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadNews()
})
</script>

<style scoped>
/* Bento Box Grid for Featured Stories */
.bento-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

@media (min-width: 768px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 250px);
  }

  .large {
    grid-column: 1;
    grid-row: span 2;
  }

  .medium:nth-child(2) {
    grid-column: 2;
    grid-row: 1;
  }

  .medium:nth-child(3) {
    grid-column: 2;
    grid-row: 2;
  }
}

@media (min-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 280px);
  }

  .large {
    grid-column: 1 / 3;
    grid-row: span 2;
  }

  .medium:nth-child(2) {
    grid-column: 3;
    grid-row: 1;
  }

  .medium:nth-child(3) {
    grid-column: 3;
    grid-row: 2;
  }
}

/* Regular News Grid */
.news-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .news-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .news-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1280px) {
  .news-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
