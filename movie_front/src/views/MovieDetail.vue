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
          
          <button 
            @click="router.back()"
            class="flex items-center gap-2 px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue/50 rounded-full text-neon-blue transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            返回
          </button>

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

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-neon-blue"></div>
        <p class="mt-4 text-neon-blue">加载电影信息中...</p>
      </div>
    </div>

    <!-- 电影详情 -->
    <main v-else-if="movie" class="container mx-auto px-4 py-8 pb-24">
      <div class="bg-card-bg/80 backdrop-blur-md rounded-3xl p-8 border border-neon-blue/20">
        <!-- 头部信息 -->
        <div class="flex flex-col lg:flex-row gap-8 mb-8">
          <!-- 电影海报 -->
          <div class="flex-shrink-0 mx-auto lg:mx-0">
            <img
              :src="reliablePosterUrl"
              :alt="movie.title"
              class="w-[300px] rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.5)] border border-neon-blue/20"
              @error="handlePosterError"
            >
          </div>

          <!-- 基本信息 -->
          <div class="flex-1">
            <h1 class="text-4xl md:text-5xl font-bold text-white mb-4 font-orbitron">{{ movie.title }}</h1>
            
            <div class="flex flex-wrap items-center gap-4 mb-6">
              <span class="px-4 py-2 bg-neon-purple/30 border border-neon-purple/50 rounded-full text-neon-purple text-sm font-medium">
                {{ movie.genre }}
              </span>
              
              <div class="flex items-center gap-2">
                <svg class="w-6 h-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span class="text-2xl font-bold text-yellow-400">{{ movie.rating }}</span>
                <span class="text-gray-400">/ 10</span>
              </div>

              <span v-if="movie.year" class="text-gray-400">{{ movie.year }}</span>
              
              <span v-if="movie.duration" class="text-gray-400">{{ movie.duration }}</span>
            </div>

            <!-- 剧情简介 -->
            <div class="mb-6">
              <h2 class="text-xl font-bold text-neon-blue mb-3 font-orbitron">剧情简介</h2>
              <p class="text-gray-300 leading-relaxed">{{ movie.plot }}</p>
            </div>

            <!-- 导演 -->
            <div v-if="movie.director" class="mb-4">
              <h3 class="text-lg font-semibold text-white mb-2">导演</h3>
              <p class="text-neon-purple">{{ movie.director }}</p>
            </div>
          </div>
        </div>

        <div class="border-t border-neon-blue/20 pt-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- 演员列表 -->
            <div v-if="movie.cast && movie.cast.length > 0">
              <h3 class="text-xl font-bold text-neon-blue mb-4 font-orbitron">主要演员</h3>
              <div class="grid grid-cols-2 gap-4">
                <div v-for="(actor, index) in movie.cast" :key="index" class="flex items-center gap-3 p-3 bg-black/30 rounded-xl hover:bg-neon-blue/10 transition-all cursor-pointer">
                  <div class="w-12 h-12 rounded-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white font-bold text-lg">
                    {{ actor.charAt(0) }}
                  </div>
                  <span class="text-gray-200">{{ actor }}</span>
                </div>
              </div>
            </div>

            <!-- 电影标签 -->
            <div v-if="movie.tags && movie.tags.length > 0">
              <h3 class="text-xl font-bold text-neon-blue mb-4 font-orbitron">电影标签</h3>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="(tag, index) in movie.tags" 
                  :key="index"
                  class="px-4 py-2 bg-neon-blue/20 border border-neon-blue/30 rounded-full text-neon-blue text-sm hover:bg-neon-blue/30 transition-all cursor-pointer"
                >
                  {{ tag }}
                </span>
              </div>
            </div>

            <!-- 额外信息 -->
            <div v-if="movie.country || movie.language">
              <h3 class="text-xl font-bold text-neon-blue mb-4 font-orbitron">电影信息</h3>
              <div class="space-y-3">
                <div v-if="movie.country" class="flex items-center gap-3">
                  <span class="text-gray-400 w-20">国家/地区:</span>
                  <span class="text-white">{{ movie.country }}</span>
                </div>
                <div v-if="movie.language" class="flex items-center gap-3">
                  <span class="text-gray-400 w-20">语言:</span>
                  <span class="text-white">{{ movie.language }}</span>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex flex-col gap-3">
              <button
                class="w-full py-4 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl text-white font-bold text-lg hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] transition-all"
                @click="addToHistory"
              >
                立即观看
              </button>
              <button
                class="w-full py-4 bg-neon-blue/20 border border-neon-blue/50 rounded-xl text-neon-blue font-bold text-lg hover:bg-neon-blue/30 transition-all"
                @click="toggleFavorite"
              >
                {{ isFavorite ? '已收藏' : '加入收藏' }}
              </button>
              <button class="w-full py-4 bg-gray-700/30 border border-gray-600/50 rounded-xl text-gray-300 font-bold text-lg hover:bg-gray-700/50 transition-all">
                分享电影
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 相关推荐 -->
      <section v-if="relatedMovies.length > 0" class="mt-12">
        <h2 class="section-title text-3xl font-bold mb-8 relative inline-block font-orbitron text-white">
          相关推荐
          <span class="absolute bottom-[-10px] left-0 w-[60px] h-[3px] bg-gradient-to-r from-neon-blue to-neon-purple rounded"></span>
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          <div
            v-for="relatedMovie in relatedMovies"
            :key="relatedMovie.id"
            @click="router.push(`/movie/${relatedMovie.id}`)"
            class="cursor-pointer group"
          >
            <img
              :src="reliableMovieUrl(relatedMovie.image)"
              :alt="relatedMovie.title"
              class="w-full h-[200px] object-cover rounded-xl transition-all duration-300 group-hover:scale-105 group-hover:shadow-[0_10px_30px_rgba(0,240,255,0.3)]"
              @error="handleMovieImageError"
            >
            <p class="mt-2 text-white text-sm truncate group-hover:text-neon-blue transition-colors">{{ relatedMovie.title }}</p>
            <div class="flex items-center gap-1 text-yellow-400 text-xs">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              <span>{{ relatedMovie.rating }}</span>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 错误提示 -->
    <div v-else-if="error" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center">
        <svg class="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <h2 class="text-2xl font-bold text-red-400 mb-2">加载失败</h2>
        <p class="text-gray-400 mb-6">{{ error }}</p>
        <button 
          @click="router.push('/')"
          class="px-6 py-3 bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue rounded-full text-neon-blue transition-all"
        >
          返回首页
        </button>
      </div>
    </div>

    <!-- 智能助手对话框 -->
    <MovieAssistant v-if="showAssistant" @close="showAssistant = false" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import MovieAssistant from '../components/MovieAssistant.vue';
import { movieApi, userApi, getReliableImageUrl, buildResourceUrl } from '../api/movies';
import { resolvePoster } from '../utils/poster';

const props = defineProps({
  id: {
    type: Number,
    required: true
  }
});

const router = useRouter();

const movie = ref(null);
const relatedMovies = ref([]);
const loading = ref(false);
const error = ref(null);
const showAssistant = ref(false);
const isFavorite = ref(false);

const currentUserId = computed(() => {
  const user = localStorage.getItem('user');
  if (!user) return null;
  try {
    return JSON.parse(user).id;
  } catch (e) {
    return null;
  }
});

// 图片fallback
const fallbackPosterUrl = 'https://placehold.co/300x450/1a1a2e/00f0ff?text=No+Image';
const fallbackMovieUrl = 'https://placehold.co/200x300/1a1a2e/00f0ff?text=Movie';

// 计算可靠的图片URL
const reliablePosterUrl = computed(() => {
  return movie.value ? resolvePoster(movie.value.image, movie.value.title, { width: '300', height: '450', buildResourceUrl, getReliableImageUrl }) : fallbackPosterUrl;
});

const reliableMovieUrl = (imageUrl) => {
  return resolvePoster(imageUrl, '', { width: '200', height: '300', buildResourceUrl, getReliableImageUrl });
};

// 图片加载错误处理
const handlePosterError = (e) => {
  e.target.src = fallbackPosterUrl;
};

const handleMovieImageError = (e) => {
  e.target.src = fallbackMovieUrl;
};

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

const normalizeMovie = (raw) => {
  if (!raw) return null;
  const resolvedImage = resolvePoster(raw.image, raw.title, { width: '300', height: '450', buildResourceUrl, getReliableImageUrl });
  return {
    id: raw.id,
    title: raw.title,
    image: resolvedImage,
    genre: raw.genre || '未知',
    rating: raw.rating ?? 'N/A',
    year: raw.year || '',
    duration: raw.duration || '',
    plot: raw.plot || raw.description || '暂无简介',
    director: raw.director || '',
    cast: raw.cast || [],
    tags: raw.tags || [],
    country: raw.country || '',
    language: raw.language || ''
  };
};

// 获取电影详情
const fetchMovieDetail = async () => {
  try {
    loading.value = true;
    const response = await movieApi.getMovieDetail(props.id);
    const data = response?.data ?? response;
    movie.value = normalizeMovie(data);

    if (!movie.value) {
      error.value = '电影不存在';
    }
  } catch (err) {
    console.error('获取电影详情失败:', err);
    error.value = '加载电影信息失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 获取相关电影
const fetchRelatedMovies = async () => {
  try {
    const response = await movieApi.getHotMovies(1, 5);
    const list = response?.data ?? response ?? [];
    relatedMovies.value = (Array.isArray(list) ? list : [])
      .filter(m => m.id !== props.id)
      .map(m => ({ ...m, image: resolvePoster(m.image, m.title, '200', '300') }));
      .map(m => ({ ...m, image: resolvePoster(m.image, m.title, { width: '200', height: '300', buildResourceUrl, getReliableImageUrl }) }));
  } catch (err) {
    console.error('获取相关电影失败:', err);
  }
};

const addToHistory = async () => {
  if (!currentUserId.value) return;
  try {
    await userApi.addHistory(currentUserId.value, props.id);
  } catch (err) {
    console.warn('添加观看历史失败', err);
  }
};

const checkFavorite = async () => {
  if (!currentUserId.value) return;
  try {
    const favorites = await userApi.getFavorites(currentUserId.value);
    const list = favorites?.data ?? favorites ?? [];
    isFavorite.value = Array.isArray(list) && list.some(item => (item.movie_id || item.id) === props.id);
  } catch (err) {
    console.warn('检查收藏状态失败', err);
  }
};

const toggleFavorite = async () => {
  if (!currentUserId.value) {
    router.push({ path: '/login', query: { redirect: `/movie/${props.id}` } });
    return;
  }
  try {
    if (isFavorite.value) {
      await userApi.removeFavorite(currentUserId.value, props.id);
      isFavorite.value = false;
    } else {
      await userApi.addFavorite(currentUserId.value, props.id);
      isFavorite.value = true;
    }
  } catch (err) {
    console.error('更新收藏失败', err);
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

onMounted(async () => {
  initializeButtonPosition();
  await fetchMovieDetail();
  await fetchRelatedMovies();
  await addToHistory();
  await checkFavorite();
});

function resolvePoster(path, title = '', width = '400', height = '600') {
  // 优先已配置的真实海报
  return resolvePoster(path, title, { width, height, buildResourceUrl, getReliableImageUrl });
}
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
</style>
