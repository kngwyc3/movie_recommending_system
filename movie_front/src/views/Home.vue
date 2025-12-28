<template>
  <div class="min-h-screen">
    <!-- 背景效果 -->
    <div class="bg-animation"></div>
    <div class="grid-overlay"></div>

    <!-- 头部导航 -->
    <AppHeader @openAssistant="showAssistant = true" />

    <!-- 主要内容 -->
    <main class="container mx-auto px-4 py-8 pb-24">
      <!-- 错误提示 -->
      <div v-if="error" class="mb-6 p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-300">
        {{ error }}
      </div>

      <!-- 特色推荐 -->
      <FeaturedBanner v-if="!loading" :movie="featuredMovie" />

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-neon-blue"></div>
        <p class="mt-4 text-neon-blue">加载中...</p>
      </div>
    </main>

    <!-- 智能助手对话框 -->
    <MovieAssistantAI v-if="showAssistant" @close="showAssistant = false" />

    <!-- 页脚 -->
    <footer class="py-8 border-t border-gray-800">
      <div class="container mx-auto px-4 text-center">
        <p class="text-gray-500">&copy; 2024 星际影院. 探索无限宇宙,享受电影之旅</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import AppHeader from '../components/AppHeader.vue';
import FeaturedBanner from '../components/FeaturedBanner.vue';
import MovieAssistantAI from '../components/MovieAssistantAI.vue';
import { movieApi, buildResourceUrl, getReliableImageUrl } from '../api/movies';
import { resolvePoster } from '../utils/poster';

const router = useRouter();
const showAssistant = ref(false);

// 电影数据
const featuredMovie = ref(null);
const loading = ref(false);
const error = ref(null);

// 获取特色推荐
const fetchFeaturedMovie = async () => {
  try {
    loading.value = true;
    const response = await movieApi.getFeaturedMovie();
    // request 封装已在 success 且带 data 时返回 data 字段，这里直接使用响应
    const data = response || null;
    featuredMovie.value = data
      ? {
          ...data,
          image: resolvePoster(data.image, data.title, { width: '1200', height: '600', buildResourceUrl, getReliableImageUrl })
        }
      : null;

    if (!featuredMovie.value) {
      error.value = '暂无特色推荐数据';
    }
  } catch (err) {
    console.error('获取特色推荐失败:', err);
    error.value = '加载特色推荐失败';
  } finally {
    loading.value = false;
  }
};

// 页面加载时获取数据
onMounted(async () => {
  await fetchFeaturedMovie();
});
</script>

<style scoped>
</style>
