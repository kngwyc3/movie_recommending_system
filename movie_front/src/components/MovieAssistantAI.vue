<template>
  <div 
    class="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm"
    @click.self="$emit('close')"
  >
    <div 
      ref="assistantDialog"
      class="assistant-dialog fixed bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0f] rounded-3xl shadow-[0_20px_60px_rgba(0,0,0,0.8)] border border-neon-blue/30 overflow-hidden flex flex-col"
      :style="dialogStyle"
      @click.stop
    >
      <!-- 头部拖拽区域 -->
      <div 
        class="drag-handle bg-gradient-to-r from-neon-blue/20 to-neon-purple/20 p-6 border-b border-neon-blue/20 cursor-move"
        @mousedown="startDrag"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-neon-blue to-neon-purple rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <h2 class="text-xl font-bold text-white font-orbitron">AI 电影助手</h2>
              <p class="text-xs text-gray-400">
                {{ isStreaming ? '正在思考中...' : '智能推荐 · 精彩影评 · 影史知识' }}
              </p>
            </div>
          </div>
          <button 
            @click="$emit('close')"
            class="p-2 hover:bg-white/10 rounded-full transition-colors"
          >
            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- 快捷问题 -->
        <div class="flex flex-wrap gap-2">
          <button 
            v-for="quickQuestion in quickQuestions" 
            :key="quickQuestion"
            @click="handleQuickQuestion(quickQuestion)"
            :disabled="isStreaming"
            class="px-3 py-1.5 bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue/30 rounded-full text-neon-blue text-xs transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ quickQuestion }}
          </button>
        </div>
      </div>

      <!-- 聊天区域 -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center">
          <div class="w-20 h-20 bg-gradient-to-br from-neon-blue to-neon-purple rounded-full flex items-center justify-center mb-4 animate-pulse">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-white mb-2 font-orbitron">我是您的 AI 电影助手</h3>
          <p class="text-gray-400 text-sm max-w-xs">基于 RAG 技术，我可以为您智能推荐电影、解答电影相关问题。请选择上方快捷问题或直接提问！</p>
        </div>

        <!-- 消息列表 -->
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          :class="['flex', message.isUser ? 'justify-end' : 'justify-start']"
        >
          <div 
            :class="[
              'max-w-[80%] p-4 rounded-2xl',
              message.isUser 
                ? 'bg-gradient-to-r from-neon-blue to-neon-purple text-white rounded-br-md' 
                : 'bg-gray-800/80 text-gray-200 rounded-bl-md'
            ]"
          >
            <p class="whitespace-pre-wrap">{{ message.text }}</p>
            
            <!-- 推荐的电影列表 -->
            <div v-if="message.movies && message.movies.length > 0" class="mt-3 space-y-2">
              <div class="text-xs text-gray-400 mb-2">为您推荐以下电影：</div>
              <div 
                v-for="movie in message.movies" 
                :key="movie.id"
                class="flex items-center gap-2 p-2 bg-gray-900/50 rounded-lg hover:bg-gray-900/70 transition-colors cursor-pointer"
                @click="goToMovie(movie.id)"
              >
                <div class="text-neon-blue text-sm">🎬</div>
                <div class="flex-1">
                  <div class="text-sm font-medium">{{ movie.title }}</div>
                  <div class="text-xs text-gray-500">{{ movie.genres?.join(' · ') || '未分类' }}</div>
                </div>
              </div>
            </div>

            <span 
              :class="['text-xs mt-2 block', message.isUser ? 'text-white/60' : 'text-gray-500']"
            >
              {{ message.time }}
            </span>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="isStreaming" class="flex justify-start">
          <div class="bg-gray-800/80 p-4 rounded-2xl rounded-bl-md">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-neon-blue rounded-full animate-bounce"></span>
              <span class="w-2 h-2 bg-neon-blue rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
              <span class="w-2 h-2 bg-neon-blue rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="flex justify-center">
          <div class="bg-red-500/20 border border-red-500 rounded-lg p-3 text-red-300 text-sm">
            {{ error }}
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="p-4 border-t border-neon-blue/20 bg-[#0a0a0f]">
        <div class="flex gap-3">
          <input
            v-model="userInput"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="输入您的问题..."
            class="flex-1 bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-neon-blue transition-all"
            :disabled="isStreaming"
          >
          <button 
            @click="sendMessage"
            :disabled="isStreaming || !userInput.trim()"
            :class="[
              'px-6 py-3 rounded-xl font-medium transition-all',
              userInput.trim() && !isStreaming
                ? 'bg-gradient-to-r from-neon-blue to-neon-purple text-white hover:shadow-[0_5px_20px_rgba(0,240,255,0.3)]' 
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            ]"
          >
            {{ isStreaming ? '思考中...' : '发送' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { aiApi } from '../api/ai';
import { movieApi } from '../api/movies';

const emit = defineEmits(['close']);
const router = useRouter();

// 组件挂载时初始化位置
onMounted(() => {
  initializePosition();
});

const assistantDialog = ref(null);
const chatContainer = ref(null);
const userInput = ref('');
const messages = ref([]);
const isStreaming = ref(false);
const error = ref(null);

// 拖拽相关状态
const isDragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const dialogPosition = ref({ x: 0, y: 0 });

// 计算对话框样式
const dialogStyle = computed(() => ({
  width: '500px',
  height: '600px',
  transform: `translate(${dialogPosition.value.x}px, ${dialogPosition.value.y}px)`,
  transition: isDragging.value ? 'none' : 'transform 0.2s ease-out, box-shadow 0.3s ease',
  cursor: isDragging.value ? 'grabbing' : 'default',
  zIndex: isDragging.value ? 101 : 100
}));

const quickQuestions = [
  '推荐一部科幻电影',
  '最近有什么好电影',
  '推荐动作片',
  '经典爱情电影'
];

// 初始化位置到屏幕中心
const initializePosition = () => {
  if (typeof window !== 'undefined') {
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    const dialogWidth = 500;
    const dialogHeight = 600;

    dialogPosition.value = {
      x: (windowWidth - dialogWidth) / 2,
      y: (windowHeight - dialogHeight) / 2
    };
  }
};

// 开始拖拽
const startDrag = (e) => {
  if (e.button !== 0) return;
  
  isDragging.value = true;
  dragOffset.value = {
    x: e.clientX - dialogPosition.value.x,
    y: e.clientY - dialogPosition.value.y
  };

  document.body.style.userSelect = 'none';
  document.body.style.cursor = 'grabbing';

  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', stopDrag);
  document.addEventListener('mouseleave', stopDrag);
};

// 处理拖拽
const handleDrag = (e) => {
  if (!isDragging.value) return;

  let newX = e.clientX - dragOffset.value.x;
  let newY = e.clientY - dragOffset.value.y;

  const dialogWidth = 500;
  const dialogHeight = 600;
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  const minVisible = 50;
  
  if (newX + dialogWidth < minVisible) {
    newX = minVisible - dialogWidth;
  }
  if (newX > windowWidth - minVisible) {
    newX = windowWidth - minVisible;
  }
  if (newY < 0) {
    newY = 0;
  }
  if (newY + dialogHeight < minVisible) {
    newY = minVisible - dialogHeight;
  }
  if (newY > windowHeight - minVisible) {
    newY = windowHeight - minVisible;
  }

  dialogPosition.value = { x: newX, y: newY };
};

// 停止拖拽
const stopDrag = () => {
  isDragging.value = false;
  document.body.style.userSelect = '';
  document.body.style.cursor = '';
  
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
  document.removeEventListener('mouseleave', stopDrag);
};

const handleQuickQuestion = (question) => {
  userInput.value = question;
  sendMessage();
};

// 获取电影详情
const fetchMovieDetails = async (movieIds) => {
  const movies = [];
  for (const id of movieIds) {
    try {
      const movie = await movieApi.getMovieDetail(id);
      movies.push({
        id: movie.id,
        title: movie.title,
        genres: movie.genres ? movie.genres.split(', ') : []
      });
    } catch (err) {
      console.error(`获取电影 ${id} 详情失败:`, err);
      // 如果获取失败，使用默认信息
      movies.push({
        id,
        title: `电影 ${id}`,
        genres: []
      });
    }
  }
  return movies;
};

const sendMessage = async () => {
  const text = userInput.value.trim();
  if (!text || isStreaming.value) return;

  console.log('[AI助手] 开始发送消息:', text);

  // 清除之前的错误
  error.value = null;

  // 添加用户消息
  messages.value.push({
    text,
    isUser: true,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  });
  
  userInput.value = '';
  isStreaming.value = true;

  // 滚动到底部
  await nextTick();
  scrollToBottom();

  try {
    console.log('[AI助手] 调用 aiApi.recommendStream...');
    
    // 使用流式 API
    let aiResponse = '';
    let recommendedMovieIds = [];

    await aiApi.recommendStream(
      text,
      5,
      3,
      {
        onMessage: async (data) => {
          console.log('[AI助手] 收到消息:', data.type, data);
          
          if (data.type === 'retrieval') {
            // 接收到检索结果
            recommendedMovieIds = data.data.recommended_movie_ids || [];
            console.log('[AI助手] 推荐的电影ID:', recommendedMovieIds);
          } else if (data.type === 'llm_chunk') {
            // 接收到 LLM 内容片段
            aiResponse += data.data.content;
            
            // 更新最后一条 AI 消息
            const lastMessage = messages.value[messages.value.length - 1];
            if (lastMessage && !lastMessage.isUser) {
              lastMessage.text = aiResponse;
            } else {
              messages.value.push({
                text: aiResponse,
                isUser: false,
                movies: [],
                time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
              });
            }
            
            nextTick(() => scrollToBottom());
          } else if (data.type === 'complete') {
            console.log('[AI助手] 生成完成，开始获取电影详情...');
            // 完成，添加推荐电影信息
            const lastMessage = messages.value[messages.value.length - 1];
            if (lastMessage && !lastMessage.isUser && recommendedMovieIds.length > 0) {
              // 获取电影详情
              console.log('[AI助手] 开始获取电影详情...');
              const movieDetails = await fetchMovieDetails(recommendedMovieIds);
              console.log('[AI助手] 电影详情:', movieDetails);
              lastMessage.movies = movieDetails;
              nextTick(() => scrollToBottom());
            }
          }
        },
        onError: (err) => {
          console.error('[AI助手] 流式推荐失败:', err);
          error.value = '抱歉，AI 服务暂时不可用，请稍后重试';
          isStreaming.value = false;
        },
        onComplete: () => {
          console.log('[AI助手] 流式响应完成');
          isStreaming.value = false;
          nextTick(() => scrollToBottom());
        }
      }
    );
  } catch (err) {
    console.error('[AI助手] 发送消息失败:', err);
    error.value = '发送失败，请检查网络连接';
    isStreaming.value = false;
  }
};

const goToMovie = (movieId) => {
  router.push(`/movie/${movieId}`);
  emit('close');
};

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

// 监听消息变化，自动滚动
watch(messages, () => {
  nextTick(() => scrollToBottom());
}, { deep: true });
</script>

<style scoped>
.assistant-dialog {
  will-change: transform;
  user-select: none;
}

.assistant-dialog * {
  user-select: text;
}

.drag-handle {
  user-select: none;
  -webkit-user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}
</style>
