<template>
  <div class="user-menu relative">
    <!-- 已登录：显示用户头像 -->
    <router-link
      v-if="isLoggedIn"
      to="/profile"
      class="flex items-center gap-3 px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue/50 rounded-full transition-all"
    >
      <!-- 如果有头像则显示头像图片，否则显示首字母 -->
      <div v-if="user.avatar" class="relative w-8 h-8 rounded-full overflow-hidden border-2 border-neon-blue/30">
        <img
          :src="user.avatar"
          :alt="user.username"
          class="w-full h-full object-cover"
          onerror="this.parentElement.querySelector('.avatar-fallback')?.style.display='flex'; this.style.display='none'"
        >
      </div>
      <div v-else class="w-8 h-8 rounded-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white font-bold border-2 border-neon-blue/30 avatar-fallback">
        {{ user.username?.charAt(0).toUpperCase() || 'U' }}
      </div>
      <span class="text-neon-blue font-medium">{{ user.username || '用户' }}</span>
    </router-link>

    <!-- 未登录：显示登录/注册按钮 -->
    <div v-else class="flex items-center gap-3">
      <router-link
        to="/login"
        class="px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue/50 rounded-full text-neon-blue font-medium transition-all"
      >
        登录
      </router-link>
      <router-link
        to="/register"
        class="px-4 py-2 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full text-white font-bold hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] transition-all"
      >
        注册
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { buildResourceUrl } from '../api/movies';

const isLoggedIn = ref(false);
const user = ref({
  username: '',
  avatar: ''
});

const checkAuthStatus = () => {
  const token = localStorage.getItem('token');
  const loggedIn = localStorage.getItem('isLoggedIn');
  const userData = localStorage.getItem('user');

  console.log('检查登录状态:', { token, loggedIn, userData });

  if (token && loggedIn === 'true' && userData) {
    const parsedUser = JSON.parse(userData);
    isLoggedIn.value = true;
    user.value = {
      username: parsedUser.username,
      avatar: buildResourceUrl(parsedUser.avatar) || ''
    };
  } else {
    isLoggedIn.value = false;
  }
};

onMounted(() => {
  checkAuthStatus();

  // 监听 localStorage 变化
  window.addEventListener('storage', checkAuthStatus);

  // 定时检查登录状态（用于同页面更新）
  const checkInterval = setInterval(checkAuthStatus, 500);

  onUnmounted(() => {
    clearInterval(checkInterval);
    window.removeEventListener('storage', checkAuthStatus);
  });
});
</script>
