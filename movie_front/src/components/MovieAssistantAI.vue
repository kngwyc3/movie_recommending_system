<template>
  <div 
    class="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm transition-opacity duration-300"
    :class="isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'"
    @click.self="closeAssistant"
  >
    <div 
      ref="assistantDialog"
      class="assistant-dialog fixed top-0 right-0 bottom-0 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0f] shadow-[0_20px_60px_rgba(0,0,0,0.8)] border-l border-neon-blue/30 overflow-hidden flex flex-col transition-transform duration-300"
      :style="dialogStyle"
      @click.stop
    >
      <!-- 头部区域 -->
      <div 
        class="bg-gradient-to-r from-neon-blue/20 to-neon-purple/20 p-6 border-b border-neon-blue/20"
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
            @click="closeAssistant"
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
          :class="['flex group/message', message.isUser ? 'justify-end' : 'justify-start']"
        >
          <div 
            :class="[
              'max-w-[70%] p-4 rounded-2xl',
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

          <!-- 操作按钮（仅用户消息显示） -->
          <div 
            v-if="message.isUser"
            class="flex items-center gap-2 ml-2 opacity-0 group-hover/message:opacity-100 transition-opacity"
          >
            <!-- 复制按钮 -->
            <button 
              @click="copyMessage(message.text)"
              class="p-2 hover:bg-neon-blue/20 rounded-lg transition-colors"
              title="复制"
            >
              <svg class="w-4 h-4 text-neon-blue" fill="currentColor" viewBox="0 0 24 24">
                <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
              </svg>
            </button>

            <!-- 删除按钮 -->
            <button 
              @click="deleteMessage(index)"
              class="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
              title="删除此对话"
            >
              <svg class="w-4 h-4 text-red-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
              </svg>
            </button>
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
import * as chatApi from '../api/chat';

const emit = defineEmits(['close']);
const router = useRouter();

// 组件挂载时设置可见
onMounted(async () => {
  isVisible.value = true;
});

const assistantDialog = ref(null);
const chatContainer = ref(null);
const userInput = ref('');
const messages = ref([]);
const isStreaming = ref(false);
const error = ref(null);
const isVisible = ref(false);

// 计算对话框样式
const dialogStyle = computed(() => ({
  width: '400px',
  transform: isVisible.value ? 'translateX(0)' : 'translateX(100%)',
}));

const quickQuestions = [
  '推荐一部科幻电影',
  '最近有什么好电影',
  '推荐动作片',
  '经典爱情电影'
];

// 监听isVisible变化，加载历史
watch(isVisible, (newVal) => {
  if (newVal) {
    loadChatHistory();
  }
});

// 加载聊天历史
const loadChatHistory = async () => {
  try {
    const userId = JSON.parse(localStorage.getItem('user') || '{}').id;
    if (!userId) {
      console.log('[AI助手] 用户未登录，跳过加载历史');
      return;
    }

    console.log('[AI助手] 开始加载历史对话，userId:', userId);
    
    const history = await chatApi.getChatHistory(userId, 1, 50);
    
    if (history && history.chats && history.chats.length > 0) {
      console.log('[AI助手] 加载到 ' + history.chats.length + ' 条历史对话');
      
      // 按时间顺序加载对话（从旧到新），只取最近3条
      const sortedChats = history.chats
        .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
        .slice(-3);
      
      for (const chat of sortedChats) {
        // 添加用户问题
        messages.value.push({
          text: chat.question,
          isUser: true,
          time: new Date(chat.created_at).toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })
        });
        
        // 添加AI回答
        const aiMessage = {
          text: chat.answer,
          isUser: false,
          movies: [],
          time: new Date(chat.created_at).toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })
        };
        
        // 如果有相关电影，获取详情
        if (chat.related_movies && chat.related_movies.length > 0) {
          try {
            aiMessage.movies = await fetchMovieDetails(chat.related_movies);
          } catch (err) {
            console.error('[AI助手] 获取历史对话的电影详情失败:', err);
          }
        }
        
        messages.value.push(aiMessage);
      }
      
      console.log('[AI助手] 历史对话加载完成，共 ' + messages.value.length + ' 条消息');
      nextTick(() => scrollToBottom());
    } else {
      console.log('[AI助手] 没有历史对话');
    }
  } catch (err) {
    console.error('[AI助手] 加载历史对话失败:', err);
    // 不显示错误，静默处理
  }
};

const handleQuickQuestion = (question) => {
  userInput.value = question;
  sendMessage();
};

const closeAssistant = () => {
  isVisible.value = false;
  emit('close');
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
          
          // 保存对话到历史
          saveChatToHistory(text, aiResponse, recommendedMovieIds);
        }
      }
    );
  } catch (err) {
    console.error('[AI助手] 发送消息失败:', err);
    error.value = '发送失败，请检查网络连接';
    isStreaming.value = false;
  }
};

// 保存对话到历史
const saveChatToHistory = async (question, answer, relatedMovies) => {
  try {
    const userId = JSON.parse(localStorage.getItem('user') || '{}').id;
    if (!userId) {
      console.log('[AI助手] 用户未登录，不保存对话');
      return;
    }

    console.log('[AI助手] 保存对话到历史...');
    await chatApi.saveChat(userId, question, answer, relatedMovies);
    console.log('[AI助手] 对话已保存');
  } catch (err) {
    console.error('[AI助手] 保存对话失败:', err);
    // 不显示错误，静默处理
  }
};

const goToMovie = (movieId) => {
  router.push(`/movie/${movieId}`);
  emit('close');
};

const deleteMessage = async (index) => {
  // 检查是否是用户消息
  if (!messages.value[index].isUser) return;

  // 获取用户消息和对应的AI回复
  const userMessage = messages.value[index];
  
  // 从集合中删除用户消息和紧接着的AI消息
  messages.value.splice(index, 1);
  // 删除AI回答（现在在index位置，因为用户消息已删除）
  if (index < messages.value.length && !messages.value[index].isUser) {
    messages.value.splice(index, 1);
  }

  // 尝试从后端删除对话记录
  try {
    const userId = JSON.parse(localStorage.getItem('user') || '{}').id;
    if (!userId) return;

    // 根据问题内容查找对应的chat记录
    const history = await chatApi.getChatHistory(userId, 1, 50);
    if (history && history.chats) {
      const chatToDelete = history.chats.find(chat => 
        chat.question === userMessage.text
      );
      
      if (chatToDelete) {
        await chatApi.deleteChat(chatToDelete.id);
        console.log('[AI助手] 对话已删除');
        showNotification('对话已删除', 'success');
      }
    }
  } catch (err) {
    console.error('[AI助手] 删除对话失败:', err);
    showNotification('删除失败', 'error');
  }
};

const copyMessage = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    console.log('[AI助手] 消息已复制到剪贴板');
    showNotification('已复制到剪贴板', 'success');
  }).catch(err => {
    console.error('[AI助手] 复制失败:', err);
    showNotification('复制失败', 'error');
  });
};

const showNotification = (message, type = 'success') => {
  // 创建通知元素
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 px-4 py-2 rounded-lg text-white text-sm z-[200] animate-fade-in ${
    type === 'success' ? 'bg-green-500' : 'bg-red-500'
  }`;
  notification.textContent = message;
  document.body.appendChild(notification);

  // 3秒后移除
  setTimeout(() => {
    notification.remove();
  }, 3000);
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

/* 自定义滚动条样式 */
.assistant-dialog ::-webkit-scrollbar {
  width: 6px;
}

.assistant-dialog ::-webkit-scrollbar-track {
  background: transparent;
}

.assistant-dialog ::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #00f0ff, #b000ff);
  border-radius: 3px;
}

.assistant-dialog ::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #00f0ff, #b000ff);
  opacity: 0.8;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
</style>
