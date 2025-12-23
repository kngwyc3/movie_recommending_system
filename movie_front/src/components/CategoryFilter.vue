<template>
  <section class="mb-8">
    <div class="flex flex-wrap gap-3">
      <button 
        v-for="category in categories" 
        :key="category"
        @click="selectCategory(category)"
        :class="[
          'category-tag px-5 py-2 rounded-full font-medium transition-all duration-300',
          selectedCategory === category 
            ? 'bg-neon-blue/20 border-neon-blue text-neon-blue shadow-[0_0_15px_rgba(0,240,255,0.4)] -translate-y-1' 
            : 'bg-neon-blue/10 border-neon-blue/30 text-neon-blue/80 hover:bg-neon-blue/20'
        ]"
        style="border: 1px solid;"
      >
        {{ category }}
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { movieApi } from '../api/movies';

const categories = ref(['全部', '科幻', '动作', '冒险', '悬疑', '爱情', '动画']);
const selectedCategory = ref('全部');

const selectCategory = (category) => {
  selectedCategory.value = category;
};

// 从后端获取分类列表
const fetchCategories = async () => {
  try {
    const response = await movieApi.getCategories();
    if (response.success && response.data) {
      categories.value = response.data;
    }
  } catch (error) {
    console.error('获取分类列表失败:', error);
    // 使用默认分类
  }
};

onMounted(() => {
  fetchCategories();
});

defineExpose({
  selectedCategory
});
</script>
