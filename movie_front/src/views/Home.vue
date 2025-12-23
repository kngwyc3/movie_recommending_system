<template>
  <div class="min-h-screen">
    <!-- 背景效果 -->
    <div class="bg-animation"></div>
    <div class="grid-overlay"></div>

    <!-- 头部导航 -->
    <header class="header sticky top-0 z-50 py-4 bg-gradient-to-b from-[rgba(10,10,15,0.95)] to-[rgba(10,10,15,0.8)] backdrop-blur-md border-b border-neon-blue/20">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <router-link to="/" class="logo text-3xl font-black bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent animate-logo-glow font-orbitron cursor-pointer">
            星际影院
          </router-link>
          
          <nav class="hidden md:flex items-center gap-2">
            <router-link 
              v-for="item in navItems" 
              :key="item.name"
              :to="item.path"
              :class="[
                'nav-link px-5 py-2 rounded-full font-medium transition-all duration-300',
                activeNav === item.name ? 'text-neon-blue bg-neon-blue/10' : 'text-white/70 hover:text-neon-blue'
              ]"
              @click="activeNav = item.name"
            >
              <span v-if="item.icon" class="inline-block mr-1">{{ item.icon }}</span>
              {{ item.name }}
            </router-link>
          </nav>
          
          <div class="search-container relative">
            <svg class="search-icon absolute left-4 top-1/2 -translate-y-1/2 text-neon-blue w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input
              v-model="searchQuery"
              @keyup.enter="searchMovies"
              type="text"
              placeholder="搜索电影、导演、演员..."
              class="search-input"
            >
          </div>

          <!-- 用户菜单 -->
          <UserMenu />

          <!-- 可拖动的智能助手按钮 -->
          <div
            ref="assistantButton"
            class="assistant-button fixed z-50 bg-gradient-to-r from-neon-blue to-neon-purple p-3 rounded-full shadow-[0_0_30px_rgba(0,240,255,0.5)] hover:scale-110 transition-all duration-300 group cursor-move"
            :style="buttonStyle"
            @click="showAssistant = true"
            @mousedown="startButtonDrag"
          >
            <svg class="w-6 h-6 text-white group-hover:animate-pulse pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="container mx-auto px-4 py-8 pb-24">
      <!-- 错误提示 -->
      <div v-if="error" class="mb-6 p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-300">
        {{ error }}
      </div>

      <!-- 特色推荐 -->
      <FeaturedBanner v-if="!loading && featuredMovie" :movie="featuredMovie" :recommended-movies="recommendedMovies" />

      <!-- 热门电影瀑布流 -->
      <section v-if="!loading" class="mb-12">
        <h2 class="text-2xl font-bold text-white mb-6 font-orbitron flex items-center gap-3">
          <span class="w-1 h-8 bg-gradient-to-b from-neon-blue to-neon-purple rounded"></span>
          热门电影
        </h2>
        <!-- 横向滚动容器 -->
        <div class="relative group">
          <div class="flex gap-4 overflow-x-auto pb-4 scroll-smooth hide-scrollbar" ref="scrollContainer">
            <div
              v-for="movie in hotMovies"
              :key="movie.id"
              class="flex-shrink-0 w-[200px]"
            >
              <MovieCard :movie="movie" />
            </div>
          </div>
          <!-- 左右导航按钮 -->
          <button
            v-if="showScrollButtons"
            @click="scrollLeft"
            class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 z-10 w-10 h-10 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full flex items-center justify-center text-white shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:scale-110"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          <button
            v-if="showScrollButtons"
            @click="scrollRight"
            class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 z-10 w-10 h-10 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full flex items-center justify-center text-white shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:scale-110"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </button>
        </div>
      </section>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-neon-blue"></div>
        <p class="mt-4 text-neon-blue">加载中...</p>
      </div>
    </main>

    <!-- 智能助手对话框 -->
    <MovieAssistant v-if="showAssistant" @close="showAssistant = false" />

    <!-- 页脚 -->
    <footer class="py-8 border-t border-gray-800">
      <div class="container mx-auto px-4 text-center">
        <p class="text-gray-500">&copy; 2024 星际影院. 探索无限宇宙,享受电影之旅</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import FeaturedBanner from '../components/FeaturedBanner.vue';
import MovieAssistant from '../components/MovieAssistant.vue';
import UserMenu from '../components/UserMenu.vue';
import MovieCard from '../components/MovieCard.vue';
import { movieApi, buildResourceUrl, getReliableImageUrl } from '../api/movies';
import { resolvePoster } from '../utils/poster';

const searchQuery = ref('');
const navItems = ref([
  { name: '首页', path: '/' },
  { name: '推荐', path: '/recommendations' },
  { name: '分类', path: '/categories' },
  { name: '个人中心', path: '/profile' }
]);
const activeNav = ref('首页');
const showAssistant = ref(false);

// 按钮拖拽相关状态
const assistantButton = ref(null);
const isButtonDragging = ref(false);
const buttonOffset = ref({ x: 0, y: 0 });
const buttonPosition = ref({ x: 0, y: 0 });

// 计算按钮样式
const buttonStyle = computed(() => ({
  transform: `translate(${buttonPosition.value.x}px, ${buttonPosition.value.y}px)`,
  transition: isButtonDragging.value ? 'none' : 'transform 0.2s ease-out',
  cursor: isButtonDragging.value ? 'grabbing' : 'move'
}));

// 电影数据
const featuredMovie = ref(null);
const hotMovies = ref([]);
const loading = ref(false);
const error = ref(null);

// 推荐电影（从热门电影中取3个）
const recommendedMovies = computed(() => hotMovies.value.slice(0, 3));

// 滚动容器引用
const scrollContainer = ref(null);
const showScrollButtons = computed(() => typeof window !== 'undefined' && window.innerWidth >= 768);

// 获取特色推荐
const fetchFeaturedMovie = async () => {
  try {
    const response = await movieApi.getFeaturedMovie();
    const data = response || null;
    featuredMovie.value = data
      ? {
          ...data,
          image: resolvePoster(data.image, data.title, { width: '1200', height: '600', buildResourceUrl, getReliableImageUrl })
        }
      : null;

    if (!featuredMovie.value) {
      console.warn('暂无特色推荐数据');
    }
  } catch (err) {
    console.error('获取特色推荐失败:', err);
    error.value = '加载特色推荐失败';
  }
};

// 获取热门电影
const fetchHotMovies = async () => {
  try {
    const response = await movieApi.getHotMovies(1, 20);
    const data = Array.isArray(response) ? response : (response?.movies || []);
    hotMovies.value = data.map(movie => ({
      ...movie,
      image: resolvePoster(movie.image, movie.title, { width: '400', height: '600', buildResourceUrl, getReliableImageUrl })
    }));
  } catch (err) {
    console.error('获取热门电影失败:', err);
  }
};

// 滚动控制
const scrollLeft = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({ left: -400, behavior: 'smooth' });
  }
};

const scrollRight = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({ left: 400, behavior: 'smooth' });
  }
};

// 初始化按钮位置到右下角
const initializeButtonPosition = () => {
  if (typeof window !== 'undefined') {
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    const buttonSize = 60;

    buttonPosition.value = {
      x: windowWidth - buttonSize - 24,
      y: windowHeight - buttonSize - 24
    };
  }
};

// 开始拖拽按钮
const startButtonDrag = (e) => {
  // 只允许鼠标左键拖拽
  if (e.button !== 0) return;
  
  isButtonDragging.value = true;
  buttonOffset.value = {
    x: e.clientX - buttonPosition.value.x,
    y: e.clientY - buttonPosition.value.y
  };

  // 添加全局事件监听
  document.addEventListener('mousemove', handleButtonDrag);
  document.addEventListener('mouseup', stopButtonDrag);
  document.addEventListener('mouseleave', stopButtonDrag);
};

// 处理按钮拖拽
const handleButtonDrag = (e) => {
  if (!isButtonDragging.value) return;

  let newX = e.clientX - buttonOffset.value.x;
  let newY = e.clientY - buttonOffset.value.y;

  // 边界限制
  const buttonSize = 60;
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;

  // 确保按钮至少有一部分可见
  const minVisible = 30;
  
  // 左边界
  if (newX + buttonSize < minVisible) {
    newX = minVisible - buttonSize;
  }
  // 右边界
  if (newX > windowWidth - minVisible) {
    newX = windowWidth - minVisible;
  }
  // 上边界
  if (newY < 0) {
    newY = 0;
  }
  // 下边界
  if (newY + buttonSize < minVisible) {
    newY = minVisible - buttonSize;
  }
  if (newY > windowHeight - minVisible) {
    newY = windowHeight - minVisible;
  }

  buttonPosition.value = { x: newX, y: newY };
};

// 停止拖拽按钮
const stopButtonDrag = () => {
  isButtonDragging.value = false;
  
  // 移除全局事件监听
  document.removeEventListener('mousemove', handleButtonDrag);
  document.removeEventListener('mouseup', stopButtonDrag);
  document.removeEventListener('mouseleave', stopButtonDrag);
};

// 页面加载时获取数据
onMounted(async () => {
  initializeButtonPosition();
  loading.value = true;
  try {
    await Promise.all([
      fetchFeaturedMovie(),
      fetchHotMovies()
    ]);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.assistant-button {
  /* 使用硬件加速提高性能 */
  will-change: transform;
  /* 防止文本选择干扰拖拽 */
  user-select: none;
  -webkit-user-select: none;
  /* 移除点击时的默认样式 */
  -webkit-tap-highlight-color: transparent;
}

.assistant-button:active {
  cursor: grabbing;
}

.assistant-button svg {
  /* 确保图标不响应拖拽事件 */
  pointer-events: none;
}

/* 隐藏滚动条但保留滚动功能 */
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
