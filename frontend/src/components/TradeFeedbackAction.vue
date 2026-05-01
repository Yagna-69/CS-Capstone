<template>
  <!-- Outer wrapper — callers must set position:relative on the parent they want covered -->
  <div class="w-full">
    <!-- Feedback overlay: absolutely covers the preview block + button area -->
    <Transition name="feedback-fade">
      <div
        v-if="feedback"
        class="absolute inset-x-0 bottom-0 top-3 z-10 flex items-center justify-center rounded-xl p-3"
        :class="feedback.variant === 'success' ? 'bg-bg-primary/95' : 'bg-bg-primary/97'"
        :role="feedback.variant === 'error' ? 'alert' : 'status'"
      >
        <div
          class="w-full rounded-xl border overflow-hidden"
          :class="feedback.variant === 'success' ? 'border-primary/40' : 'border-red-500/40'"
        >
          <!-- Accent line -->
          <div
            class="h-0.5 w-full"
            :class="feedback.variant === 'success' ? 'bg-primary' : 'bg-red-500'"
          ></div>

          <div class="p-4 space-y-3">
            <div class="flex items-start gap-2.5">
              <div
                class="mt-0.5 shrink-0 w-5 h-5 flex items-center justify-center"
                :class="feedback.variant === 'success' ? 'text-primary' : 'text-red-400'"
                aria-hidden="true"
              >
                <svg v-if="feedback.variant === 'success'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <p
                  class="text-xs font-bold uppercase tracking-widest mb-1"
                  :class="feedback.variant === 'success' ? 'text-primary' : 'text-red-400'"
                >
                  {{ feedback.variant === 'success' ? 'Success' : 'Failed' }}
                </p>
                <p class="text-sm text-gray-300 leading-relaxed">{{ feedback.message }}</p>
              </div>
            </div>

            <button
              type="button"
              class="w-full py-2 bg-primary text-black rounded-full text-sm font-bold hover:opacity-80 transition"
              @click="dismiss"
            >
              OK
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Normal execute button — always rendered so the parent keeps its height -->
    <button
      type="button"
      :disabled="disabled || loading"
      :class="buttonClass"
      @click="$emit('execute')"
    >
      {{ loading ? loadingLabel : buttonLabel }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  feedback:     { type: Object,  default: null  },
  buttonClass:  { type: String,  required: true },
  buttonLabel:  { type: String,  default: 'Execute Trade' },
  disabled:     { type: Boolean, default: false },
  loading:      { type: Boolean, default: false },
  loadingLabel: { type: String,  default: 'Processing...' },
})

const emit = defineEmits(['update:feedback', 'execute'])

function dismiss() {
  emit('update:feedback', null)
}
</script>

<style scoped>
.feedback-fade-enter-active,
.feedback-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.feedback-fade-enter-from,
.feedback-fade-leave-to {
  opacity: 0;
  transform: scale(0.97);
}
</style>
