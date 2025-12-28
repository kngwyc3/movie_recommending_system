<template>
  <header class="header sticky top-0 z-50 py-4 bg-gradient-to-b from-[rgba(10,10,15,0.95)] to-[rgba(10,10,15,0.8)] backdrop-blur-md border-b border-neon-blue/20">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <!-- Logo -->
        <router-link to="/" class="logo text-3xl font-black bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent animate-logo-glow font-orbitron cursor-pointer">
          星际影院
        </router-link>
        
        <!-- 导航菜单 -->
        <nav class="hidden md:flex items-center gap-2">
          <router-link 
            v-for="item in navItems" 
            :key="item.name"
            :to="item.path"
            :class="[
              'nav-link px-5 py-2 rounded-full font-medium transition-all duration-300',
              isActive(item.path) ? 'text-neon-blue bg-neon-blue/10' : 'text-white/70 hover:text-neon-blue'
            ]"
          >
            <span v-if="item.icon" class="inline-block mr-1">{{ item.icon }}</span>
            {{ item.name }}
          </router-link>
        </nav>
        
        <!-- 右侧功能区 -->
        <div class="flex items-center gap-4">
          <!-- 搜索框 -->
          <div class="search-container relative">
            <svg class="search-icon absolute left-4 top-1/2 -translate-y-1/2 text-neon-blue w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              type="text"
              placeholder="搜索电影、导演、演员..."
              class="search-input"
            >
          </div>

          <!-- AI 助手按钮 -->
          <button
            @click="$emit('openAssistant')"
            class="ai-assistant-btn flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full text-white font-medium shadow-[0_0_20px_rgba(0,240,255,0.3)] hover:shadow-[0_0_30px_rgba(0,240,255,0.5)] hover:scale-105 transition-all duration-300 group"
            title="AI 电影助手"
          >
            <svg class="w-5 h-5 group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <span class="hidden lg:inline">AI 助手</span>
          </button>

          <!-- 用户菜单 -->
          <UserMenu />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import UserMenu from './UserMenu.vue';

const router = useRouter();
const route = useRoute();
const searchQuery = ref('');

defineEmits(['openAssistant']);

const navItems = ref([
  { name: '首页', path: '/' },
  { name: '推荐', path: '/recommendations' },
  { name: '分类', path: '/categories' },
  { name: '个人中心', path: '/profile' }
]);

const isActive = (path) => {
  return route.path === path;
};

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/categories?search=${encodeURIComponent(searchQuery.value)}`);
  }
};
</script>

<style scoped>
.search-input {
  @apply w-64 pl-12 pr-4 py-2 bg-gray-800/50 border border-gray-700 rounded-full text-white placeholder-gray-500 focus:outline-none focus:border-neon-blue transition-all;
}

.search-icon {
  pointer-events: none;
}

.nav-link {
  position: relative;
  overflow: hidden;
}

.nav-link::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #00f0ff, #a855f7);
  transform: translateX(-50%);
  transition: width 0.3s ease;
}

.nav-link:hover::before {
  width: 80%;
}
</style>
