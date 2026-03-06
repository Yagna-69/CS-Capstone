<template>
  <div class="min-h-screen bg-bg-primary flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-8xl font-bold font-goldman text-primary tracking-tight">FXTrade</h1>
      <RouterLink 
        to="/login"
        class="inline-block mt-10 px-8 py-4 bg-primary text-black rounded-full font-bold text-lg hover:opacity-90 transition-all duration-300"
      >
        Get Started
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>