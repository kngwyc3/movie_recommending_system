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
              <p class="text-xs text-gray-400">智能推荐 · 精彩影评 · 影史知识</p>
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
            class="px-3 py-1.5 bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue/30 rounded-full text-neon-blue text-xs transition-all"
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
          <h3 class="text-xl font-bold text-white mb-2 font-orbitron">我是您的电影助手</h3>
          <p class="text-gray-400 text-sm max-w-xs">我可以帮您推荐电影、解答电影相关问题、分享影评见解。请选择上方快捷问题或直接提问！</p>
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
            <span 
              :class="['text-xs mt-2 block', message.isUser ? 'text-white/60' : 'text-gray-500']"
            >
              {{ message.time }}
            </span>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="isTyping" class="flex justify-start">
          <div class="bg-gray-800/80 p-4 rounded-2xl rounded-bl-md">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-neon-blue rounded-full animate-bounce"></span>
              <span class="w-2 h-2 bg-neon-blue rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
              <span class="w-2 h-2 bg-neon-blue rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
            </div>
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
            :disabled="isTyping"
          >
          <button 
            @click="sendMessage"
            :disabled="isTyping || !userInput.trim()"
            :class="[
              'px-6 py-3 rounded-xl font-medium transition-all',
              userInput.trim() && !isTyping
                ? 'bg-gradient-to-r from-neon-blue to-neon-purple text-white hover:shadow-[0_5px_20px_rgba(0,240,255,0.3)]' 
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            ]"
          >
            发送
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, computed, onMounted } from 'vue';

defineEmits(['close']);

// 组件挂载时初始化位置
onMounted(() => {
  initializePosition();
});

const assistantDialog = ref(null);
const chatContainer = ref(null);
const userInput = ref('');
const messages = ref([]);
const isTyping = ref(false);

// 拖拽相关状态
const isDragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const dialogPosition = ref({ x: 0, y: 0 });

// 计算对话框样式
const dialogStyle = computed(() => ({
  width: '450px',
  height: '540px',
  transform: `translate(${dialogPosition.value.x}px, ${dialogPosition.value.y}px) scale(0.9)`,
  transition: isDragging.value ? 'none' : 'transform 0.2s ease-out, box-shadow 0.3s ease',
  cursor: isDragging.value ? 'grabbing' : 'default',
  zIndex: isDragging.value ? 101 : 100
}));

const quickQuestions = [
  '推荐一部科幻电影',
  '最近有什么好电影',
  '什么是诺兰式叙事',
  '经典动作片推荐'
];

// 初始化位置到屏幕中心
const initializePosition = () => {
  if (typeof window !== 'undefined') {
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    const dialogWidth = 450;
    const dialogHeight = 540;

    dialogPosition.value = {
      x: (windowWidth - dialogWidth) / 2,
      y: (windowHeight - dialogHeight) / 2
    };
  }
};

// 开始拖拽
const startDrag = (e) => {
  // 只允许鼠标左键拖拽
  if (e.button !== 0) return;
  
  isDragging.value = true;
  dragOffset.value = {
    x: e.clientX - dialogPosition.value.x,
    y: e.clientY - dialogPosition.value.y
  };

  // 拖拽时阻止文本选择
  document.body.style.userSelect = 'none';
  document.body.style.cursor = 'grabbing';

  // 添加全局事件监听
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', stopDrag);
  document.addEventListener('mouseleave', stopDrag);
};

// 处理拖拽
const handleDrag = (e) => {
  if (!isDragging.value) return;

  let newX = e.clientX - dragOffset.value.x;
  let newY = e.clientY - dragOffset.value.y;

  // 边界限制
  const dialogWidth = 450;
  const dialogHeight = 540;
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;

  // 确保对话框至少有一部分可见
  const minVisible = 50;
  
  // 左边界
  if (newX + dialogWidth < minVisible) {
    newX = minVisible - dialogWidth;
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
  
  // 恢复文本选择和鼠标样式
  document.body.style.userSelect = '';
  document.body.style.cursor = '';
  
  // 移除全局事件监听
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
  document.removeEventListener('mouseleave', stopDrag);
};

const aiResponses = {
  '推荐一部科幻电影': `🎬 推荐以下经典科幻电影：

1. 《星际穿越》 - 9.4分
   诺兰执导，探讨时空与爱的深刻主题，视觉效果震撼。

2. 《银翼杀手2049》 - 8.9分
   视觉艺术的巅峰之作，对人工智能与人性的深度思考。

3. 《黑客帝国》 - 9.5分
   开创性的虚拟现实题材，哲学思辨与动作场面完美结合。

4. 《降临》 - 8.7分
   独特的时空叙事，探讨语言与思维的关系。

需要更详细的介绍或其他类型推荐吗？`,

  '最近有什么好电影': `🎥 近期热门电影推荐：

**新片上映：**
- 《沙丘2》- 史诗级科幻续作
- 《银河护卫队3》- 漫威情怀收官
- 《奥本海默》- 诺兰传记力作
- 《芭比》- 社会讽刺喜剧

**高评分佳作：**
- 《瞬息全宇宙》- 多元宇宙创意
- 《巴比伦》- 好莱坞黄金时代
- 《鲸》- 亲情深度剖析

想了解哪部电影的详细信息？`,

  '什么是诺兰式叙事': `🎬 诺兰式叙事特点：

**核心特征：**
1. **非线性叙事** - 打破时间顺序，通过闪回、平行时空等手法重构故事
2. **多重时间线** - 如《盗梦空间》的梦境层级、《敦刻尔克》的海陆空三条线
3. **记忆与现实模糊** - 《记忆碎片》的倒叙手法
4. **哲学思考** - 探讨时间、记忆、身份等深层主题

**经典代表作品：**
- 《盗梦空间》- 梦境套梦
- 《星际穿越》- 爱超越时空
- 《信条》- 时间逆转
- 《致命魔术》- 献身艺术

想深入了解哪部作品？`,

  '经典动作片推荐': `💥 动作片经典推荐：

**现代动作经典：**
1. 《疾速追杀》系列
   "枪斗术"开创者，动作设计教科书级

2. 《疾速特攻》系列
   跑酷动作与枪战的完美结合

3. 《碟中谍》系列
   特技实拍，汤姆·克鲁斯拼命演出

**香港动作经典：**
- 《精武门》- 李小龙功夫巅峰
- 《英雄本色》- 枪战港片经典
- 《杀破狼》- 硬核动作片

**华语近作：**
- 《战狼》系列- 军事动作
- 《流浪地球》- 科幻动作

偏好哪种风格？我可以推荐更多！`
};

const defaultResponses = [
  `好问题！让我来帮您解答...

根据我的电影数据库，这是一部非常值得观看的作品。建议您可以先关注以下几个方面：

📌 导演的独特风格
📌 演员的精彩表演
📌 叙事结构的巧妙设计

需要我为您提供更多相关信息吗？`,

  `这是一个很有趣的话题！

在电影史上，这个主题产生了许多经典作品。我认为最值得推荐的是那些能够引发观众深度思考的佳作。

如果您有特定的偏好（比如年代、类型、导演等），我可以为您提供更精准的推荐！`,

  `感谢您的提问！

作为一名电影助手，我建议您可以从以下几个角度来欣赏电影：
1. 关注影片的视觉风格和摄影
2. 留意配乐对情绪的烘托
3. 思考导演想要传达的主题

您还想了解电影的其他方面吗？`
];

const handleQuickQuestion = (question) => {
  userInput.value = question;
  sendMessage();
};

const sendMessage = async () => {
  const text = userInput.value.trim();
  if (!text) return;

  // 添加用户消息
  messages.value.push({
    text,
    isUser: true,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  });
  
  userInput.value = '';
  isTyping.value = true;

  // 滚动到底部
  await nextTick();
  scrollToBottom();

  // 模拟AI回复
  setTimeout(() => {
    const response = aiResponses[text] || defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
    
    messages.value.push({
      text: response,
      isUser: false,
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    });
    
    isTyping.value = false;
    
    // 滚动到底部
    nextTick(() => scrollToBottom());
  }, 1000 + Math.random() * 1000);
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
  /* 使用硬件加速提高性能 */
  will-change: transform;
  /* 隐藏拖拽时的默认文本选择 */
  user-select: none;
}

.assistant-dialog * {
  user-select: text;
}

.drag-handle {
  /* 拖拽手柄样式 */
  user-select: none;
  -webkit-user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}
</style>
