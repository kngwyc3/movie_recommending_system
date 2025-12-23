<template>
  <div class="min-h-screen">
    <!-- 背景效果 -->
    <div class="bg-animation"></div>
    <div class="grid-overlay"></div>
    <div ref="starsContainer" class="fixed inset-0 z-[-1] pointer-events-none"></div>
    <div ref="particlesContainer" class="fixed inset-0 z-[-1] pointer-events-none"></div>

    <!-- 路由视图 -->
    <router-view></router-view>
  </div>
</template>

<script setup>
// Background effects are handled via CSS and global layout
</script>


