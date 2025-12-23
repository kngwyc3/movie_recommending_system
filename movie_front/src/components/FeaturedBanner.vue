<template>
  <section v-if="movies.length > 0" class="relative mb-10 rounded-2xl overflow-hidden">
    <div 
      ref="bannerContainer"
      class="w-full h-[500px] relative overflow-hidden cursor-grab active:cursor-grabbing"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="stopDrag"
      @mouseleave="stopDrag"
      @touchstart="startDrag"
      @touchmove="onDrag"
      @touchend="stopDrag"
    >
      <!-- 可横向滑动的电影横幅 -->
      <div 
        class="absolute inset-0 flex transition-transform duration-500 ease-out"
        :style="{ transform: `translateX(${-currentIndex * 100}%)` }"
      >
        <div 
          v-for="(mov, index) in movies" 
          :key="mov.id"
          class="w-full h-full flex-shrink-0 relative"
        >
          <div 
            class="absolute inset-0 bg-cover bg-center"
            :style="`background-image: url('${mov.image}'); filter: brightness(0.6) saturate(1.2);`"
          ></div>
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-[#0a0a0f]"></div>
          <div 
            class="absolute inset-0"
            style="animation: bannerPulse 10s ease-in-out infinite;"
          ></div>
          <div class="absolute bottom-0 left-0 right-0 p-10 bg-gradient-to-t from-[rgba(10,10,15,0.95)] to-transparent z-10">
            <h1 class="text-5xl font-black text-white mb-4 neon-text font-orbitron">{{ mov.title }}</h1>
            <p class="text-lg text-white/80 max-w-2xl leading-relaxed">
              {{ mov.description }}
            </p>
            <button class="mt-5 px-10 py-4 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full text-white text-lg font-bold uppercase tracking-wider transition-all hover:translate-y-[-3px] hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)]">
              立即观看
            </button>
          </div>
        </div>
      </div>

      <!-- 左右导航按钮 -->
      <button
        v-if="movies.length > 1"
        @click.stop="prevMovie"
        class="absolute left-4 top-1/2 -translate-y-1/2 z-20 w-12 h-12 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full flex items-center justify-center text-white shadow-lg opacity-0 hover:opacity-100 transition-opacity duration-300 hover:scale-110"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <button
        v-if="movies.length > 1"
        @click.stop="nextMovie"
        class="absolute right-4 top-1/2 -translate-y-1/2 z-20 w-12 h-12 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full flex items-center justify-center text-white shadow-lg opacity-0 hover:opacity-100 transition-opacity duration-300 hover:scale-110"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </button>

      <!-- 指示器 -->
      <div v-if="movies.length > 1" class="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 flex gap-2">
        <button
          v-for="(_, index) in movies"
          :key="index"
          @click.stop="goToSlide(index)"
          :class="[
            'w-2 h-2 rounded-full transition-all duration-300',
            currentIndex === index ? 'bg-neon-blue w-8' : 'bg-white/30 hover:bg-white/50'
          ]"
        ></button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  movie: {
    type: Object,
    default: null
  },
  recommendedMovies: {
    type: Array,
    default: () => []
  }
});

// 特色推荐电影列表（包含主推荐和推荐电影）
const movies = computed(() => {
  const result = [];
  if (props.movie) {
    result.push(props.movie);
  }
  if (props.recommendedMovies && props.recommendedMovies.length > 0) {
    result.push(...props.recommendedMovies);
  }
  return result;
});

const currentIndex = ref(0);
const bannerContainer = ref(null);
const isDragging = ref(false);
const startX = ref(0);
const currentTranslate = ref(0);
const prevTranslate = ref(0);

const goToSlide = (index) => {
  currentIndex.value = index;
};

const prevMovie = () => {
  currentIndex.value = currentIndex.value === 0 ? movies.value.length - 1 : currentIndex.value - 1;
};

const nextMovie = () => {
  currentIndex.value = (currentIndex.value + 1) % movies.value.length;
};

const startDrag = (e) => {
  isDragging.value = true;
  startX.value = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
  prevTranslate.value = -currentIndex.value * 100;
};

const onDrag = (e) => {
  if (!isDragging.value) return;
  
  const currentX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
  const diff = currentX - startX.value;
  currentTranslate.value = prevTranslate.value + diff;
};

const stopDrag = () => {
  if (!isDragging.value) return;
  
  const moved = currentTranslate.value - prevTranslate.value;
  const threshold = 50;
  
  if (moved > threshold) {
    prevMovie();
  } else if (moved < -threshold) {
    nextMovie();
  }
  
  isDragging.value = false;
  currentTranslate.value = -currentIndex.value * 100;
};
</script>

<style scoped>
.hide-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 240, 255, 0.3) transparent;
}

.hide-scrollbar::-webkit-scrollbar {
  height: 6px;
}

.hide-scrollbar::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.hide-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 240, 255, 0.3);
  border-radius: 3px;
}

.hide-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 240, 255, 0.5);
}
</style>
