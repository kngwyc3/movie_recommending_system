<template>
  <router-link
    :to="`/movie/${movie.id}`"
    class="movie-card bg-card-bg border border-neon-blue/20 rounded-2xl overflow-hidden transition-all duration-500 relative cursor-pointer hover:translate-y-[-10px] hover:scale-[1.02] hover:border-neon-blue hover:shadow-[0_20px_40px_rgba(0,0,0,0.5),0_0_30px_rgba(0,240,255,0.2)] block"
  >
    <div
      v-if="movie.badge"
      class="recommend-badge absolute top-3 right-3 bg-gradient-to-r from-neon-pink to-neon-purple px-4 py-2 rounded-full text-xs font-bold text-white z-10 animate-badge-pulse"
    >
      {{ movie.badge }}
    </div>
    <div class="relative overflow-hidden">
      <img
        :src="reliableImageUrl"
        :alt="movie.title"
        class="w-full h-[300px] object-cover transition-transform duration-500 hover:scale-110"
        @error="handleImageError"
      >
      <div class="absolute inset-0 bg-gradient-to-t from-[rgba(20,20,35,0.95)] via-transparent to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
    </div>
    <div class="p-4 relative z-10">
      <h3 class="font-orbitron text-lg font-bold text-white mb-2 truncate">{{ movie.title }}</h3>
      <div class="flex justify-between items-center">
        <span class="text-xs text-neon-purple bg-neon-purple/20 px-3 py-1 rounded-full">{{ movie.genre }}</span>
        <div class="flex items-center gap-1 text-yellow-400">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
          </svg>
          <span class="font-bold">{{ movie.rating }}</span>
        </div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { ref, computed } from 'vue';
import { getReliableImageUrl } from '../api/movies';

const props = defineProps({
  movie: {
    type: Object,
    required: true
  }
});

const fallbackUrl = ref('https://placehold.co/400x600/1a1a2e/00f0ff?text=Movie');

const reliableImageUrl = computed(() => {
  return getReliableImageUrl(props.movie.image, '400', '600');
});

const handleImageError = (e) => {
  e.target.src = fallbackUrl.value;
};
</script>

<style scoped>
.movie-card::before {
  content: '';
  @apply absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-neon-blue/10 opacity-0 transition-opacity duration-500 pointer-events-none;
}

.movie-card:hover::before {
  @apply opacity-100;
}
</style>
