<template>
  <div class="min-h-screen flex items-center justify-center">
    <!-- 背景效果 -->
    <div class="bg-animation"></div>
    <div class="grid-overlay"></div>
    <div ref="starsContainer" class="fixed inset-0 z-[-1] pointer-events-none"></div>

    <div class="relative z-10 w-full max-w-md px-4">
      <div class="bg-card-bg/90 backdrop-blur-md rounded-3xl p-8 border border-neon-blue/20 shadow-[0_0_50px_rgba(0,240,255,0.2)]">
        <!-- Logo -->
        <div class="text-center mb-8">
          <router-link to="/" class="text-3xl font-black bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent animate-logo-glow font-orbitron">
            星际影院
          </router-link>
        </div>

        <!-- 登录表单 -->
        <h2 class="text-2xl font-bold text-white mb-6 text-center font-orbitron">用户登录</h2>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-white font-medium mb-2">邮箱</label>
            <input
              v-model="formData.email"
              type="email"
              placeholder="请输入邮箱"
              required
              class="w-full px-4 py-3 bg-black/50 border border-neon-blue/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-neon-blue transition-all"
            >
          </div>

          <div>
            <label class="block text-white font-medium mb-2">密码</label>
            <div class="relative">
              <input
                v-model="formData.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                required
                class="w-full px-4 py-3 bg-black/50 border border-neon-blue/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-neon-blue transition-all"
              >
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-neon-blue transition-colors"
              >
                {{ showPassword ? '👁️' : '🔒' }}
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between text-sm">
            <label class="flex items-center text-gray-400 cursor-pointer">
              <input v-model="formData.remember" type="checkbox" class="mr-2 accent-neon-blue">
              记住我
            </label>
            <a href="#" class="text-neon-blue hover:underline">忘记密码？</a>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl text-white font-bold text-lg hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- 错误提示 -->
        <div v-if="error" class="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm">
          {{ error }}
        </div>

        <!-- 注册链接 -->
        <div class="mt-6 text-center text-gray-400">
          还没有账号？
          <router-link to="/register" class="text-neon-blue hover:underline">立即注册</router-link>
        </div>

        <!-- 返回首页 -->
        <div class="mt-4 text-center">
          <router-link to="/" class="text-gray-500 hover:text-white transition-colors">
            返回首页
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../api/movies';

const router = useRouter();

const formData = ref({
  email: '',
  password: '',
  remember: false
});

const showPassword = ref(false);
const loading = ref(false);
const error = ref('');

// 获取登录后的重定向路径
const redirectPath = computed(() => {
  return router.currentRoute.value.query.redirect || '/';
});

const handleLogin = async () => {
  loading.value = true;
  error.value = '';

  try {
    console.log('开始登录，邮箱:', formData.value.email);
    const response = await authApi.login(formData.value.email, formData.value.password);
    console.log('登录响应:', response);

    // 检查响应格式，支持多种可能的返回格式
    const token = response.token || response.data?.token;
    const user = response.user || response.data?.user || {};
    const isSuccess = response.success !== false;

    if (token) {
      // 保存 token 和用户信息
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('isLoggedIn', 'true');

      console.log('登录成功，token 已保存');
      console.log('重定向到:', redirectPath.value);

      // 延迟跳转，确保数据已保存
      setTimeout(() => {
        router.push(redirectPath.value);
      }, 100);
    } else if (response.message) {
      error.value = response.message;
    } else {
      error.value = '登录失败，请检查邮箱和密码';
    }
  } catch (err) {
    error.value = err.message || '登录失败，请检查邮箱和密码';
    console.error('登录错误:', err);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.assistant-button {
  will-change: transform;
  user-select: none;
  -webkit-user-select: none;
  -webkit-tap-highlight-color: transparent;
}
</style>
