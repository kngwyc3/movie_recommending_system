<template>
  <div class="min-h-screen">
    <!-- 背景效果 -->
    <div class="bg-animation"></div>
    <div class="grid-overlay"></div>
    <div ref="starsContainer" class="fixed inset-0 z-[-1] pointer-events-none"></div>
    <div ref="particlesContainer" class="fixed inset-0 z-[-1] pointer-events-none"></div>

    <!-- 头部导航 -->
    <header class="header sticky top-0 z-50 py-4 bg-gradient-to-b from-[rgba(10,10,15,0.95)] to-[rgba(10,10,15,0.8)] backdrop-blur-md border-b border-neon-blue/20">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <router-link to="/" class="logo text-2xl font-black bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent animate-logo-glow font-orbitron cursor-pointer">
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
      <!-- 页面标题 -->
      <h1 class="text-4xl font-bold text-white mb-8 font-orbitron">
        为您推荐
        <span class="absolute bottom-[-10px] left-0 w-[80px] h-[3px] bg-gradient-to-r from-neon-blue to-neon-purple rounded"></span>
      </h1>

      <!-- 错误提示 -->
      <div v-if="error" class="mb-6 p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-300">
        {{ error }}
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-neon-blue"></div>
        <p class="mt-4 text-neon-blue">加载推荐电影中...</p>
      </div>

      <!-- 推荐电影列表 -->
      <div v-else-if="hotMovies.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
        <MovieCard v-for="movie in hotMovies" :key="movie.id" :movie="movie" />
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-16">
        <svg class="w-24 h-24 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
        </svg>
        <p class="text-gray-400 text-lg">暂无推荐电影</p>
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
import { useRouter } from 'vue-router';
import MovieCard from '../components/MovieCard.vue';
import MovieAssistant from '../components/MovieAssistant.vue';
import UserMenu from '../components/UserMenu.vue';
import { movieApi, buildResourceUrl, getReliableImageUrl } from '../api/movies';
import { resolvePoster } from '../utils/poster';

const router = useRouter();
const searchQuery = ref('');
const navItems = ref([
  { name: '首页', path: '/' },
  { name: '推荐', path: '/recommendations' },
  { name: '分类', path: '/categories' },
  { name: '个人中心', path: '/profile' }
]);
const activeNav = ref('推荐');
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
const hotMovies = ref([]);
const loading = ref(false);
const error = ref(null);

// 获取热门电影
const fetchHotMovies = async () => {
  try {
    loading.value = true;
    const response = await movieApi.getHotMovies(1, 15);
    const list = Array.isArray(response?.data) ? response.data : Array.isArray(response) ? response : [];
    hotMovies.value = list.map(m => ({
      ...m,
      image: resolvePoster(m.image, m.title, { width: '400', height: '600', buildResourceUrl, getReliableImageUrl })
    }));

    if (!hotMovies.value.length) {
      error.value = '暂无推荐数据';
    }
  } catch (err) {
    console.error('获取推荐电影失败:', err);
    error.value = '加载推荐电影失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 搜索电影
const searchMovies = () => {
  if (searchQuery.value.trim()) {
    router.push(`/categories?search=${encodeURIComponent(searchQuery.value)}`);
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
  if (e.button !== 0) return;
  
  isButtonDragging.value = true;
  buttonOffset.value = {
    x: e.clientX - buttonPosition.value.x,
    y: e.clientY - buttonPosition.value.y
  };

  document.addEventListener('mousemove', handleButtonDrag);
  document.addEventListener('mouseup', stopButtonDrag);
  document.addEventListener('mouseleave', stopButtonDrag);
};

// 处理按钮拖拽
const handleButtonDrag = (e) => {
  if (!isButtonDragging.value) return;

  let newX = e.clientX - buttonOffset.value.x;
  let newY = e.clientY - buttonOffset.value.y;

  const buttonSize = 60;
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  const minVisible = 30;
  
  if (newX + buttonSize < minVisible) {
    newX = minVisible - buttonSize;
  }
  if (newX > windowWidth - minVisible) {
    newX = windowWidth - minVisible;
  }
  if (newY < 0) {
    newY = 0;
  }
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
  
  document.removeEventListener('mousemove', handleButtonDrag);
  document.removeEventListener('mouseup', stopButtonDrag);
  document.removeEventListener('mouseleave', stopButtonDrag);
};

onMounted(async () => {
  initializeButtonPosition();
  await fetchHotMovies();
});
</script>

<style scoped>
.assistant-button {
  will-change: transform;
  user-select: none;
  -webkit-user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.assistant-button:active {
  cursor: grabbing;
}

.assistant-button svg {
  pointer-events: none;
}
</style>
