<template>
  <div class="min-h-screen flex items-center justify-center py-8">
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

        <!-- 注册表单 -->
        <h2 class="text-2xl font-bold text-white mb-6 text-center font-orbitron">用户注册</h2>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-white font-medium mb-2">用户名</label>
            <input
              v-model="formData.username"
              type="text"
              placeholder="请输入用户名（3-20个字符）"
              required
              minlength="3"
              maxlength="20"
              class="w-full px-4 py-3 bg-black/50 border border-neon-blue/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-neon-blue transition-all"
            >
          </div>

          <div>
            <label class="block text-white font-medium mb-2">邮箱</label>
            <input
              v-model="formData.email"
              type="email"
              placeholder="请输入邮箱地址"
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
                placeholder="请输入密码（至少6个字符）"
                required
                minlength="6"
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

          <div>
            <label class="block text-white font-medium mb-2">确认密码</label>
            <input
              v-model="formData.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="请再次输入密码"
              required
              minlength="6"
              class="w-full px-4 py-3 bg-black/50 border border-neon-blue/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-neon-blue transition-all"
            >
          </div>

          <!-- 同意条款 -->
          <label class="flex items-start text-gray-400 text-sm cursor-pointer">
            <input v-model="formData.agreeTerms" type="checkbox" required class="mt-1 mr-2 accent-neon-blue">
            <span>我已阅读并同意 <a href="#" class="text-neon-blue hover:underline">用户协议</a> 和 <a href="#" class="text-neon-blue hover:underline">隐私政策</a></span>
          </label>

          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="w-full py-3 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl text-white font-bold text-lg hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>

        <!-- 错误提示 -->
        <div v-if="error" class="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm">
          {{ error }}
        </div>

        <!-- 成功提示 -->
        <div v-if="success" class="mt-4 p-3 bg-green-500/20 border border-green-500/50 rounded-lg text-green-300 text-sm">
          {{ success }}
        </div>

        <!-- 登录链接 -->
        <div class="mt-6 text-center text-gray-400">
          已有账号？
          <router-link to="/login" class="text-neon-blue hover:underline">立即登录</router-link>
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
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
});

const showPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const error = ref('');
const success = ref('');

const isFormValid = computed(() => {
  return formData.value.username.length >= 3 &&
         formData.value.email.length > 0 &&
         formData.value.password.length >= 6 &&
         formData.value.password === formData.value.confirmPassword &&
         formData.value.agreeTerms;
});

const handleRegister = async () => {
  loading.value = true;
  error.value = '';
  success.value = '';

  // 密码确认
  if (formData.value.password !== formData.value.confirmPassword) {
    error.value = '两次输入的密码不一致';
    loading.value = false;
    return;
  }

  try {
    console.log('开始注册:', {
      username: formData.value.username,
      email: formData.value.email
    });

    const response = await authApi.register(
      formData.value.username,
      formData.value.email,
      formData.value.password
    );

    console.log('注册响应:', response);

    // 支持多种响应格式
    const isSuccess = response.success !== false;

    if (isSuccess) {
      success.value = '注册成功！正在跳转到登录页...';
      error.value = '';

      setTimeout(() => {
        router.push('/login');
      }, 1500);
    } else {
      error.value = response.message || '注册失败';
      success.value = '';
    }
  } catch (err) {
    error.value = err.message || '注册失败，请稍后重试';
    success.value = '';
    console.error('注册错误:', err);
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
