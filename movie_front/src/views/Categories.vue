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

      <!-- 分类标签 -->
      <div class="flex flex-wrap gap-3 mb-8">
        <button
          v-for="category in categories"
          :key="category"
          @click="selectCategory(category)"
          :class="[
            'px-6 py-3 rounded-full font-medium transition-all duration-300',
            selectedCategory === category
              ? 'bg-gradient-to-r from-neon-blue to-neon-purple text-white shadow-[0_0_20px_rgba(0,240,255,0.3)]'
              : 'bg-gray-800/50 text-gray-300 hover:bg-neon-blue/20 hover:text-neon-blue'
          ]"
        >
          {{ category }}
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-neon-blue"></div>
        <p class="mt-4 text-neon-blue">加载中...</p>
      </div>

      <!-- 电影列表 -->
      <section v-if="!loading && movies.length > 0" class="mb-12">
        <h2 class="section-title text-3xl font-bold mb-8 relative inline-block font-orbitron text-white">
          {{ selectedCategory || '全部电影' }}
          <span class="absolute bottom-[-10px] left-0 w-[60px] h-[3px] bg-gradient-to-r from-neon-blue to-neon-purple rounded"></span>
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <MovieCard 
            v-for="movie in movies" 
            :key="movie.id" 
            :movie="movie" 
          />
        </div>
      </section>

      <!-- 无结果提示 -->
      <div v-if="!loading && movies.length === 0" class="text-center py-12">
        <p class="text-gray-400 text-lg">该分类暂无电影</p>
      </div>

      <!-- 加载更多按钮 -->
      <div v-if="!loading && movies.length > 0" class="text-center mt-8">
        <button class="px-10 py-4 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full text-white text-lg font-bold uppercase tracking-wider transition-all hover:translate-y-[-3px] hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)]">
          加载更多电影
        </button>
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
import { useStars } from '../composables/useStars';
import { useParticles } from '../composables/useParticles';
import MovieCard from '../components/MovieCard.vue';
import MovieAssistant from '../components/MovieAssistantAI.vue';
import UserMenu from '../components/UserMenu.vue';
import { movieApi, buildResourceUrl, getReliableImageUrl } from '../api/movies';
import { resolvePoster } from '../utils/poster';

const { starsContainer } = useStars();
const { particlesContainer } = useParticles();

const searchQuery = ref('');
const navItems = ref([
  { name: '首页', path: '/' },
  { name: '推荐', path: '/recommendations' },
  { name: '分类', path: '/categories' },
  { name: '个人中心', path: '/profile' }
]);
const activeNav = ref('分类');
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
const movies = ref([]);
const selectedCategory = ref('全部');
const loading = ref(false);
const error = ref(null);

// 分类列表
const categories = ref([]);

const normalizeMovies = (list) => {
  const arr = Array.isArray(list) ? list : [];
  return arr.map(item => ({
    ...item,
    image: resolvePoster(item.image, item.title, { width: '200', height: '300', buildResourceUrl, getReliableImageUrl })
  }));
};

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await movieApi.getCategories();
    const categoryList = response?.data ?? response;
    const list = Array.isArray(categoryList) ? categoryList : [];
    // 去重并确保“全部”只保留一个且排在首位
    const merged = ['全部', ...list.filter((c) => c && c !== '全部')];
    categories.value = Array.from(new Set(merged));
  } catch (err) {
    console.error('获取分类列表失败:', err);
    // 降级使用默认分类
    categories.value = ['全部', '科幻', '动作', '冒险', '喜剧', '恐怖', '爱情', '悬疑', '动画', '纪录片'];
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

// 选择分类
const selectCategory = async (category) => {
  selectedCategory.value = category;
  
  try {
    loading.value = true;
    let response;
    
    if (category === '全部') {
      response = await movieApi.getHotMovies(1, 12);
    } else {
      response = await movieApi.getMoviesByCategory(category, 1, 12);
    }
    
    const data = response?.data ?? response;
    movies.value = normalizeMovies(data);
  } catch (err) {
    console.error('获取分类电影失败:', err);
    error.value = '加载失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 搜索电影
const searchMovies = async () => {
  if (!searchQuery.value.trim()) {
    selectCategory('全部');
    return;
  }

  try {
    loading.value = true;
    const response = await movieApi.searchMovies(searchQuery.value, 1, 12);
    const data = response?.data ?? response;
    movies.value = normalizeMovies(data);
    selectedCategory.value = null;
  } catch (err) {
    console.error('搜索电影失败:', err);
    error.value = '搜索失败，请稍后重试';
  } finally {
    loading.value = false;
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

// 页面加载时获取数据
onMounted(async () => {
  initializeButtonPosition();
  await fetchCategories();
  await selectCategory('全部');
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
