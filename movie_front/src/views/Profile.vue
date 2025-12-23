<template>
  <div class="min-h-screen">
    <!-- 背景效果 -->
    <div class="bg-animation"></div>
    <div class="grid-overlay"></div>

    <!-- 头部导航 -->
    <header class="header sticky top-0 z-50 py-4 bg-gradient-to-b from-[rgba(10,10,15,0.95)] to-[rgba(10,10,15,0.8)] backdrop-blur-md border-b border-neon-blue/20">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <router-link to="/" class="logo text-2xl font-black bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent animate-logo-glow font-orbitron cursor-pointer">
            星际影院
          </router-link>
          
          <nav class="hidden md:flex items-center gap-2">
            <router-link 
              v-for="item in navItems" 
              :key="item.name"
              :to="item.path"
              :class="[
                'nav-link px-5 py-2 rounded-full font-medium transition-all duration-300',
                activeNav === item.name ? 'text-neon-blue bg-neon-blue/10' : 'text-white/70 hover:text-neon-blue'
              ]"
              @click="activeNav = item.name"
            >
              <span v-if="item.icon" class="inline-block mr-1">{{ item.icon }}</span>
              {{ item.name }}
            </router-link>
          </nav>

          <div class="user-menu relative">
            <div 
              class="flex items-center gap-3 px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue/50 rounded-full cursor-pointer transition-all"
            >
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white font-bold">
                {{ user.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
              <span class="text-neon-blue font-medium">{{ user.username || '用户' }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="container mx-auto px-4 py-8 pb-24">
      <h1 class="text-4xl font-bold text-white mb-8 font-orbitron">
        个人中心
        <span class="absolute bottom-[-10px] left-0 w-[80px] h-[3px] bg-gradient-to-r from-neon-blue to-neon-purple rounded"></span>
      </h1>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧用户信息卡片 -->
        <div class="lg:col-span-1">
          <div class="bg-card-bg/80 backdrop-blur-md rounded-2xl p-6 border border-neon-blue/20">
            <!-- 查看模式 -->
            <div v-if="!isEditing" class="flex flex-col items-center text-center">
              <!-- 如果有头像URL则显示头像图片，否则显示首字母 -->
              <div v-if="user.avatar" class="relative w-24 h-24 rounded-full overflow-hidden border-2 border-neon-blue/30 shadow-[0_0_30px_rgba(0,240,255,0.3)] mb-4">
                <img
                  :src="user.avatar"
                  :alt="user.username"
                  class="w-full h-full object-cover"
                  onerror="this.parentElement.querySelector('.avatar-fallback')?.style.display='flex'; this.style.display='none'"
                >
              </div>
              <div v-else class="w-24 h-24 rounded-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white text-4xl font-bold mb-4 shadow-[0_0_30px_rgba(0,240,255,0.3)] border-2 border-neon-blue/30 avatar-fallback">
                {{ user.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
              <h2 class="text-2xl font-bold text-white mb-1">{{ user.username || '用户' }}</h2>
              <p class="text-gray-400 text-sm mb-4">{{ user.email || 'user@example.com' }}</p>

              <div class="grid grid-cols-3 gap-4 w-full mb-6">
                <div class="text-center">
                  <div class="text-2xl font-bold text-neon-blue">{{ stats.favorites }}</div>
                  <div class="text-xs text-gray-400">收藏</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-neon-purple">{{ stats.history }}</div>
                  <div class="text-xs text-gray-400">观影</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-neon-pink">{{ stats.ratings }}</div>
                  <div class="text-xs text-gray-400">评价</div>
                </div>
              </div>

              <button
                @click="startEdit"
                class="w-full py-3 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl text-white font-bold hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] transition-all mb-3"
              >
                编辑资料
              </button>

              <button
                @click="handleLogout"
                class="w-full py-3 bg-gray-700/30 border border-gray-600/50 rounded-xl text-gray-300 font-bold hover:bg-red-500/20 hover:border-red-500/50 hover:text-red-400 transition-all"
              >
                退出登录
              </button>
            </div>

            <!-- 编辑模式 -->
            <div v-else class="space-y-5">
              <!-- 头像上传 -->
              <div class="flex flex-col items-center mb-6">
                <h3 class="text-xl font-bold text-white mb-4 text-center">更换头像</h3>
                <div class="relative group mb-4">
                  <!-- 头像预览 -->
                  <div
                    v-if="avatarPreview"
                    @click="handleAvatarClick"
                    class="w-32 h-32 rounded-full overflow-hidden border-4 border-neon-blue/50 cursor-pointer group-hover:border-neon-blue transition-all shadow-[0_0_30px_rgba(0,240,255,0.3)] relative"
                  >
                    <img :src="avatarPreview" :alt="user.username" class="w-full h-full object-cover pointer-events-none">
                    <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                      <span class="text-white text-2xl">📷</span>
                    </div>
                  </div>
                  <!-- 点击更换 -->
                  <div
                    v-else
                    @click="handleAvatarClick"
                    class="w-32 h-32 rounded-full overflow-hidden border-4 border-neon-blue/30 cursor-pointer group-hover:border-neon-blue/50 transition-all flex items-center justify-center shadow-[0_0_30px_rgba(0,240,255,0.3)] relative"
                  >
                    <div
                      v-if="user.avatar"
                      class="w-full h-full relative"
                    >
                      <img :src="user.avatar" :alt="user.username" class="w-full h-full object-cover pointer-events-none">
                      <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                        <span class="text-white text-2xl">📷</span>
                      </div>
                    </div>
                    <div
                      v-else
                      class="w-full h-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white text-4xl font-bold relative"
                    >
                      {{ user.username?.charAt(0).toUpperCase() || 'U' }}
                      <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                        <span class="text-white text-2xl">📷</span>
                      </div>
                    </div>
                  </div>
                  <input
                    ref="avatarInputRef"
                    type="file"
                    accept="image/*"
                    @change="handleAvatarChange"
                    class="hidden"
                  >
                </div>
                <p class="text-center text-gray-400 text-sm mb-4">点击头像更换</p>

                <!-- 上传头像按钮 -->
                <button
                  v-if="avatarPreview"
                  @click="uploadAvatar"
                  :disabled="avatarLoading"
                  class="w-full py-3 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl text-white font-bold hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] transition-all mb-4 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ avatarLoading ? '上传中...' : '确认上传' }}
                </button>
              </div>

              <!-- 用户名编辑 -->
              <div>
                <label class="block text-white font-medium mb-2">用户名</label>
                <Input
                  v-model="editForm.username"
                  placeholder="请输入用户名"
                  clearable
                  class="edit-input"
                />
              </div>

              <!-- 邮箱编辑 -->
              <div>
                <label class="block text-white font-medium mb-2">邮箱</label>
                <Input
                  v-model="editForm.email"
                  type="email"
                  placeholder="请输入邮箱"
                  clearable
                  class="edit-input"
                />
              </div>

              <!-- 操作按钮 -->
              <div class="flex gap-3">
                <button
                  @click="handleEditProfile"
                  :loading="editLoading"
                  class="flex-1 py-3 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl text-white font-bold hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] transition-all"
                >
                  {{ editLoading ? '保存中...' : '保存' }}
                </button>
                <button
                  @click="cancelEdit"
                  class="px-8 py-3 bg-gray-700/30 border border-gray-600/50 rounded-xl text-gray-300 font-bold hover:bg-gray-700/50 transition-all"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧选项卡内容 -->
        <div class="lg:col-span-2">
          <div class="bg-card-bg/80 backdrop-blur-md rounded-2xl border border-neon-blue/20">
            <div class="flex border-b border-neon-blue/20">
              <button
                v-for="tab in tabs"
                :key="tab.value"
                @click="activeTab = tab.value"
                :class="[
                  'flex-1 py-4 text-center font-medium transition-all',
                  activeTab === tab.value 
                    ? 'text-neon-blue border-b-2 border-neon-blue' 
                    : 'text-gray-400 hover:text-white'
                ]"
              >
                <span class="mr-2">{{ tab.icon }}</span>
                {{ tab.label }}
              </button>
            </div>

            <div class="p-6">
              <!-- 账号设置 -->
              <div v-if="activeTab === 'account'" class="space-y-6">
                <div class="mb-6">
                  <h3 class="text-xl font-bold text-white mb-4">账号安全</h3>
                  <div class="space-y-4">
                    <!-- 修改密码部分 -->
                    <div class="overflow-hidden rounded-xl border border-neon-blue/20">
                      <!-- 收起状态 -->
                      <div
                        v-if="!showChangePassword"
                        @click="showChangePassword = true"
                        class="flex items-center justify-between p-4 bg-black/30 cursor-pointer hover:bg-black/40 transition-all group"
                      >
                        <div class="flex items-center gap-3">
                          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-neon-blue/20 to-neon-purple/20 flex items-center justify-center text-neon-blue group-hover:shadow-[0_0_20px_rgba(0,240,255,0.3)] transition-all">
                            🔒
                          </div>
                          <div>
                            <div class="text-white font-medium">修改密码</div>
                            <div class="text-gray-400 text-sm">定期修改密码保护账号安全</div>
                          </div>
                        </div>
                        <div class="flex items-center gap-2">
                          <span class="px-4 py-2 bg-neon-blue/20 border border-neon-blue/50 rounded-full text-neon-blue text-sm transition-all group-hover:bg-neon-blue/30">
                            修改
                          </span>
                          <svg class="w-5 h-5 text-gray-400 group-hover:text-neon-blue transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                          </svg>
                        </div>
                      </div>

                      <!-- 展开状态 -->
                      <div
                        v-else
                        class="password-form-container"
                      >
                        <!-- 头部 -->
                        <div
                          @click="showChangePassword = false"
                          class="flex items-center justify-between p-4 bg-gradient-to-r from-neon-blue/10 to-neon-purple/10 cursor-pointer hover:from-neon-blue/15 hover:to-neon-purple/15 transition-all border-b border-neon-blue/20"
                        >
                          <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white shadow-[0_0_20px_rgba(0,240,255,0.4)]">
                              🔒
                            </div>
                            <div>
                              <div class="text-white font-bold">修改密码</div>
                              <div class="text-gray-400 text-sm">请输入您的新密码</div>
                            </div>
                          </div>
                          <div class="flex items-center gap-2">
                            <span class="px-4 py-2 bg-gray-600/30 border border-gray-500/50 rounded-full text-gray-300 text-sm transition-all">
                              收起
                            </span>
                            <svg class="w-5 h-5 text-gray-400 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                            </svg>
                          </div>
                        </div>

                        <!-- 表单内容 -->
                        <div class="p-6 space-y-5 bg-black/30">
                          <div class="space-y-1">
                            <label class="block text-white font-medium mb-2 flex items-center gap-2">
                              <span class="text-neon-blue">✦</span>
                              旧密码
                            </label>
                            <Input
                              v-model="passwordForm.oldPassword"
                              type="password"
                              placeholder="请输入当前密码"
                              class="password-input"
                            />
                          </div>

                          <div class="space-y-1">
                            <label class="block text-white font-medium mb-2 flex items-center gap-2">
                              <span class="text-neon-purple">✦</span>
                              新密码
                            </label>
                            <Input
                              v-model="passwordForm.newPassword"
                              type="password"
                              placeholder="请输入新密码（至少6位）"
                              class="password-input"
                            />
                            <div class="text-xs text-gray-500 mt-1">密码长度至少6位，建议包含字母和数字</div>
                          </div>

                          <div class="space-y-1">
                            <label class="block text-white font-medium mb-2 flex items-center gap-2">
                              <span class="text-neon-pink">✦</span>
                              确认新密码
                            </label>
                            <Input
                              v-model="passwordForm.confirmPassword"
                              type="password"
                              placeholder="请再次输入新密码"
                              class="password-input"
                            />
                          </div>

                          <!-- 操作按钮 -->
                          <div class="flex gap-3 pt-2">
                            <button
                              @click="showChangePassword = false; passwordForm = { oldPassword: '', newPassword: '', confirmPassword: '' }"
                              class="flex-1 py-3 bg-gray-700/30 border border-gray-600/50 rounded-xl text-gray-300 font-bold hover:bg-gray-700/50 hover:border-gray-500 transition-all"
                            >
                              取消
                            </button>
                            <button
                              @click="handleChangePassword"
                              :disabled="passwordLoading"
                              class="flex-1 py-3 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl text-white font-bold hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] disabled:opacity-50 disabled:cursor-not-allowed transition-all relative overflow-hidden"
                            >
                              <span v-if="passwordLoading">修改中...</span>
                              <span v-else>确认修改</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 绑定邮箱 -->
                    <div class="flex items-center justify-between p-4 bg-black/30 rounded-xl">
                      <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-lg bg-neon-purple/20 flex items-center justify-center text-neon-purple">
                          📧
                        </div>
                        <div>
                          <div class="text-white font-medium">绑定邮箱</div>
                          <div class="text-gray-400 text-sm">{{ user.email || '未绑定' }}</div>
                        </div>
                      </div>
                      <span class="px-4 py-2 bg-green-500/20 border border-green-500/50 rounded-full text-green-400 text-sm">
                        已绑定
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 class="text-xl font-bold text-white mb-4">隐私设置</h3>
                  <div class="space-y-4">
                    <div class="flex items-center justify-between p-4 bg-black/30 rounded-xl">
                      <div>
                        <div class="text-white font-medium">公开我的观影记录</div>
                        <div class="text-gray-400 text-sm">其他用户可以看到你的观影历史</div>
                      </div>
                      <button 
                        @click="togglePrivacy('watchHistory')"
                        :class="[
                          'w-14 h-8 rounded-full transition-all',
                          privacy.watchHistory ? 'bg-neon-blue' : 'bg-gray-600'
                        ]"
                      >
                        <div 
                          :class="[
                            'w-6 h-6 rounded-full bg-white transition-all',
                            privacy.watchHistory ? 'translate-x-7' : 'translate-x-1'
                          ]"
                        ></div>
                      </button>
                    </div>
                    <div class="flex items-center justify-between p-4 bg-black/30 rounded-xl">
                      <div>
                        <div class="text-white font-medium">公开我的收藏</div>
                        <div class="text-gray-400 text-sm">其他用户可以看到你收藏的电影</div>
                      </div>
                      <button 
                        @click="togglePrivacy('favorites')"
                        :class="[
                          'w-14 h-8 rounded-full transition-all',
                          privacy.favorites ? 'bg-neon-blue' : 'bg-gray-600'
                        ]"
                      >
                        <div 
                          :class="[
                            'w-6 h-6 rounded-full bg-white transition-all',
                            privacy.favorites ? 'translate-x-7' : 'translate-x-1'
                          ]"
                        ></div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 我的收藏 -->
              <div v-if="activeTab === 'favorites'" class="space-y-4">
                <div v-if="favoriteMovies.length > 0" class="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  <div 
                    v-for="movie in favoriteMovies"
                    :key="movie.id"
                    @click="router.push(`/movie/${movie.id}`)"
                    class="cursor-pointer group"
                  >
                    <img 
                      :src="movie.image" 
                      :alt="movie.title"
                      class="w-full h-[180px] object-cover rounded-xl transition-all duration-300 group-hover:scale-105 group-hover:shadow-[0_10px_30px_rgba(0,240,255,0.3)]"
                      onerror="this.src='https://placehold.co/200x300/1a1a2e/00f0ff?text=Movie'"
                    >
                    <p class="mt-2 text-white text-sm truncate group-hover:text-neon-blue transition-colors">{{ movie.title }}</p>
                  </div>
                </div>
                <div v-else class="text-center py-16">
                  <svg class="w-24 h-24 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                  </svg>
                  <p class="text-gray-400">暂无收藏电影</p>
                </div>
              </div>

              <!-- 观看历史 -->
              <div v-if="activeTab === 'history'" class="space-y-4">
                <div v-if="watchHistory.length > 0">
                  <div 
                    v-for="item in watchHistory"
                    :key="item.id"
                    class="flex items-center gap-4 p-4 bg-black/30 rounded-xl hover:bg-neon-blue/10 transition-all cursor-pointer"
                    @click="router.push(`/movie/${item.id}`)"
                  >
                    <img 
                      :src="item.image" 
                      :alt="item.title"
                      class="w-20 h-28 object-cover rounded-lg"
                      onerror="this.src='https://placehold.co/100x140/1a1a2e/00f0ff?text=Movie'"
                    >
                    <div class="flex-1">
                      <h4 class="text-white font-medium mb-1">{{ item.title }}</h4>
                      <p class="text-gray-400 text-sm mb-2">{{ item.genre }}</p>
                      <div class="flex items-center gap-2 text-gray-500 text-xs">
                        <span>观看时间: {{ item.watchTime }}</span>
                      </div>
                    </div>
                    <div class="text-yellow-400">
                      {{ item.rating }}⭐
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-16">
                  <svg class="w-24 h-24 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <p class="text-gray-400">暂无观看历史</p>
                </div>
              </div>

              <!-- 偏好设置 -->
              <div v-if="activeTab === 'preferences'" class="space-y-6">
                <div>
                  <h3 class="text-xl font-bold text-white mb-4">推荐偏好</h3>
                  <div class="space-y-4">
                    <div>
                      <label class="block text-white font-medium mb-2">偏好的电影类型</label>
                      <div class="flex flex-wrap gap-2">
                        <span 
                          v-for="genre in genres"
                          :key="genre"
                          @click="toggleGenre(genre)"
                          :class="[
                            'px-4 py-2 rounded-full text-sm cursor-pointer transition-all',
                            selectedGenres.includes(genre) 
                              ? 'bg-neon-blue text-white' 
                              : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                          ]"
                        >
                          {{ genre }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 class="text-xl font-bold text-white mb-4">显示设置</h3>
                  <div class="space-y-4">
                    <div class="flex items-center justify-between p-4 bg-black/30 rounded-xl">
                      <div>
                        <div class="text-white font-medium">深色模式</div>
                        <div class="text-gray-400 text-sm">使用深色主题</div>
                      </div>
                      <button 
                        @click="toggleDisplay('darkMode')"
                        :class="[
                          'w-14 h-8 rounded-full transition-all',
                          displaySettings.darkMode ? 'bg-neon-blue' : 'bg-gray-600'
                        ]"
                      >
                        <div 
                          :class="[
                            'w-6 h-6 rounded-full bg-white transition-all',
                            displaySettings.darkMode ? 'translate-x-7' : 'translate-x-1'
                          ]"
                        ></div>
                      </button>
                    </div>
                    <div class="flex items-center justify-between p-4 bg-black/30 rounded-xl">
                      <div>
                        <div class="text-white font-medium">显示评分</div>
                        <div class="text-gray-400 text-sm">在电影卡片上显示评分</div>
                      </div>
                      <button 
                        @click="toggleDisplay('showRatings')"
                        :class="[
                          'w-14 h-8 rounded-full transition-all',
                          displaySettings.showRatings ? 'bg-neon-blue' : 'bg-gray-600'
                        ]"
                      >
                        <div 
                          :class="[
                            'w-6 h-6 rounded-full bg-white transition-all',
                            displaySettings.showRatings ? 'translate-x-7' : 'translate-x-1'
                          ]"
                        ></div>
                      </button>
                    </div>
                  </div>
                </div>

                <button 
                  @click="savePreferences"
                  class="w-full py-3 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl text-white font-bold hover:shadow-[0_10px_30px_rgba(0,240,255,0.4)] transition-all"
                >
                  保存设置
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="py-8 border-t border-gray-800">
      <div class="container mx-auto px-4 text-center">
        <p class="text-gray-500">&copy; 2024 星际影院. 探索无限宇宙,享受电影之旅</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Input, MessagePlugin } from 'tdesign-vue-next';
import { authApi, userApi, buildResourceUrl, getReliableImageUrl } from '../api/movies';

const router = useRouter();

const activeNav = ref('个人中心');
const activeTab = ref('account');

const navItems = ref([
  { name: '首页', path: '/' },
  { name: '推荐', path: '/recommendations' },
  { name: '分类', path: '/categories' },
  { name: '个人中心', path: '/profile' }
]);

const tabs = [
  { label: '账号设置', value: 'account', icon: '⚙️' },
  { label: '我的收藏', value: 'favorites', icon: '❤️' },
  { label: '观看历史', value: 'history', icon: '📋' },
  { label: '偏好设置', value: 'preferences', icon: '🎯' }
];

const user = ref({
  id: null,
  username: '',
  email: '',
  avatar: ''
});

// 编辑模式
const isEditing = ref(false);
const editForm = ref({
  username: '',
  email: ''
});
const editFormRef = ref(null);
const editLoading = ref(false);

// 头像上传
const avatarInputRef = ref(null);
const avatarPreview = ref('');
const avatarLoading = ref(false);

// 修改密码表单
const showChangePassword = ref(false);
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});
const passwordLoading = ref(false);

// 检查登录状态
const isLoggedIn = ref(false);

// 统计数据
const stats = ref({
  favorites: 0,
  history: 0,
  ratings: 0
});

const privacy = ref({
  watchHistory: true,
  favorites: true
});

const favoriteMovies = ref([]);

const watchHistory = ref([]);

const genres = ['科幻', '动作', '悬疑', '爱情', '喜剧', '动画', '恐怖', '纪录片', '战争', '历史'];
const selectedGenres = ref(['科幻', '动作']);
const displaySettings = ref({
  darkMode: true,
  showRatings: true
});

// 加载用户信息
const loadUserInfo = async () => {
  const userData = localStorage.getItem('user');
  const loggedIn = localStorage.getItem('isLoggedIn');

  if (loggedIn === 'true' && userData) {
    const parsedUser = JSON.parse(userData);
    const parsedAvatar = buildResourceUrl(parsedUser.avatar);
    user.value = {
      id: parsedUser.id,
      username: parsedUser.username || '用户',
      email: parsedUser.email || 'user@example.com',
      avatar: parsedAvatar || ''
    };
    isLoggedIn.value = true;

    // 如果有用户ID，从API获取详细数据
    if (parsedUser.id) {
      await loadUserData(parsedUser.id);
    }
  } else {
    isLoggedIn.value = false;
  }
};

// 从API加载用户数据
const loadUserData = async (userId) => {
  try {
    // 获取用户信息
    console.log('开始获取用户信息，userId:', userId);
    const userInfo = await userApi.getUserInfo(userId);
    console.log('获取到的用户信息:', userInfo);

    if (userInfo) {
      user.value = {
        id: userInfo.id,
        username: userInfo.username || user.value.username,
        email: userInfo.email || user.value.email,
        avatar: buildResourceUrl(userInfo.avatar) || ''
      };

      const prefs = userInfo.preferences || {};
      selectedGenres.value = Array.isArray(prefs.favorite_genres) && prefs.favorite_genres.length > 0
        ? prefs.favorite_genres
        : selectedGenres.value;
      displaySettings.value.darkMode = prefs.dark_mode !== undefined ? prefs.dark_mode : displaySettings.value.darkMode;
      displaySettings.value.showRatings = prefs.show_ratings !== undefined ? prefs.show_ratings : displaySettings.value.showRatings;

      console.log('更新后的用户信息:', user.value);
      console.log('头像完整URL:', user.value.avatar);

      // 同步更新localStorage
      const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
      storedUser.username = user.value.username;
      storedUser.email = user.value.email;
      storedUser.avatar = user.value.avatar || '';
      localStorage.setItem('user', JSON.stringify(storedUser));
      console.log('已更新localStorage');
    }

    // 获取收藏列表
    const favorites = await userApi.getFavorites(userId);
    if (favorites) {
      favoriteMovies.value = favorites.map(item => ({
        id: item.movie_id || item.id,
        title: item.title,
        image: getReliableImageUrl(item.poster || item.image, '200', '300')
      }));
      stats.value.favorites = favoriteMovies.value.length;
    }

    // 获取观看历史
    const history = await userApi.getHistory(userId);
    if (history) {
      watchHistory.value = history.map(item => ({
        id: item.movie_id || item.id,
        title: item.title,
        genre: item.genre || '未知',
        image: getReliableImageUrl(item.poster || item.image, '100', '140'),
        watchTime: item.watch_time || item.watchTime,
        rating: item.rating || 0
      }));
      stats.value.history = watchHistory.value.length;
    }

    // 获取评分列表
    const ratings = await userApi.getRatings(userId);
    if (ratings) {
      stats.value.ratings = Array.isArray(ratings) ? ratings.length : 0;
    }
  } catch (err) {
    console.error('加载用户数据失败:', err);
  }
};

// 登出
const handleLogout = () => {
  authApi.logout();
  isLoggedIn.value = false;
  router.push('/login');
};

const togglePrivacy = (key) => {
  privacy.value[key] = !privacy.value[key];
};

const toggleGenre = (genre) => {
  if (selectedGenres.value.includes(genre)) {
    selectedGenres.value = selectedGenres.value.filter(g => g !== genre);
  } else {
    selectedGenres.value.push(genre);
  }
};

const toggleDisplay = (key) => {
  displaySettings.value[key] = !displaySettings.value[key];
};

const savePreferences = () => {
  if (!user.value.id) {
    MessagePlugin.error('请先登录');
    return;
  }
  const payload = {
    favorite_genres: selectedGenres.value,
    dark_mode: displaySettings.value.darkMode,
    show_ratings: displaySettings.value.showRatings
  };
  userApi.updatePreferences(user.value.id, payload)
    .then(() => {
      MessagePlugin.success('设置已保存');
    })
    .catch((err) => {
      console.error('保存偏好设置失败:', err);
      MessagePlugin.error(err.message || '保存失败，请稍后重试');
    });
};

// 处理编辑资料
const handleEditProfile = async () => {
  // 简单验证
  if (!editForm.value.username?.trim()) {
    MessagePlugin.warning('请输入用户名');
    return;
  }
  if (!editForm.value.email?.trim()) {
    MessagePlugin.warning('请输入邮箱');
    return;
  }
  if (!editForm.value.email.includes('@')) {
    MessagePlugin.warning('请输入有效的邮箱地址');
    return;
  }

  if (!user.value.id) {
    MessagePlugin.error('用户信息不完整');
    return;
  }

  try {
    editLoading.value = true;
    await userApi.updateUserInfo(user.value.id, {
      username: editForm.value.username,
      email: editForm.value.email
    });

    // 重新从服务器获取最新的用户信息
    await loadUserInfo();

    isEditing.value = false;
    MessagePlugin.success('资料更新成功');
  } catch (err) {
    console.error('更新资料失败:', err);
    MessagePlugin.error(err.message || '更新失败，请稍后重试');
  } finally {
    editLoading.value = false;
  }
};

// 取消编辑
const cancelEdit = () => {
  editForm.value = {
    username: user.value.username,
    email: user.value.email
  };
  avatarPreview.value = '';
  isEditing.value = false;
};

// 开始编辑
const startEdit = () => {
  editForm.value = {
    username: user.value.username,
    email: user.value.email
  };
  isEditing.value = true;
};

// 处理头像上传
const handleAvatarClick = () => {
  avatarInputRef.value?.click();
};

const handleAvatarChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    MessagePlugin.error('请选择图片文件');
    return;
  }

  // 验证文件大小（最大2MB）
  if (file.size > 2 * 1024 * 1024) {
    MessagePlugin.error('图片大小不能超过2MB');
    return;
  }

  // 显示预览
  const reader = new FileReader();
  reader.onload = (e) => {
    avatarPreview.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const uploadAvatar = async () => {
  if (!avatarInputRef.value?.files?.[0]) {
    MessagePlugin.warning('请先选择头像图片');
    return;
  }

  if (!user.value.id) {
    MessagePlugin.error('用户信息不完整');
    return;
  }

  const file = avatarInputRef.value.files[0];

  try {
    avatarLoading.value = true;

    // 调用后端API上传头像
    const formData = new FormData();
    formData.append('avatar', file);
    await userApi.uploadAvatar(user.value.id, formData);

    // 重新从服务器获取最新的用户信息（包括新头像）
    await loadUserInfo();

    // 清空预览，但不退出编辑模式，让用户可以继续修改其他信息
    avatarPreview.value = '';
    MessagePlugin.success('头像上传成功');
  } catch (err) {
    console.error('上传头像失败:', err);
    MessagePlugin.error(err.message || '上传失败，请稍后重试');
  } finally {
    avatarLoading.value = false;
    // 清空input
    if (avatarInputRef.value) {
      avatarInputRef.value.value = '';
    }
  }
};

// 处理修改密码
const handleChangePassword = async () => {
  // 验证输入
  if (!passwordForm.value.oldPassword?.trim()) {
    MessagePlugin.warning('请输入旧密码');
    return;
  }

  if (!passwordForm.value.newPassword?.trim()) {
    MessagePlugin.warning('请输入新密码');
    return;
  }

  if (passwordForm.value.newPassword.length < 6) {
    MessagePlugin.warning('新密码长度至少为6位');
    return;
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    MessagePlugin.warning('两次输入的新密码不一致');
    return;
  }

  try {
    passwordLoading.value = true;
    // 调用后端API修改密码
    await authApi.changePassword?.(passwordForm.value.oldPassword, passwordForm.value.newPassword);

    showChangePassword.value = false;
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    MessagePlugin.success('密码修改成功');
  } catch (err) {
    console.error('修改密码失败:', err);
    MessagePlugin.error(err.message || '修改失败，请检查旧密码是否正确');
  } finally {
    passwordLoading.value = false;
  }
};

onMounted(() => {
  loadUserInfo();
});
</script>

<style scoped>
.assistant-button {
  will-change: transform;
  user-select: none;
  -webkit-user-select: none;
  -webkit-tap-highlight-color: transparent;
}

/* 密码表单容器动画 */
.password-form-container {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 密码输入框样式 */
.password-input :deep(.t-input__inner) {
  background: rgba(0, 0, 0, 0.6);
  border: 1.5px solid rgba(0, 240, 255, 0.3);
  color: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  transition: all 0.3s ease;
  font-size: 15px;
}

.password-input :deep(.t-input__inner):hover {
  border-color: rgba(0, 240, 255, 0.6);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
  background: rgba(0, 0, 0, 0.7);
}

.password-input :deep(.t-input__inner):focus {
  border-color: #00f0ff;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.25), 0 0 8px rgba(138, 43, 226, 0.15);
  background: rgba(0, 0, 0, 0.8);
  outline: none;
}

.password-input :deep(.t-input__inner)::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* 内联编辑输入框样式 */
.edit-input {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: #fff;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.edit-input :deep(.t-input__inner) {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: #fff;
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.3s ease;
}

.edit-input :deep(.t-input__inner):hover {
  border-color: rgba(0, 240, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
}

.edit-input :deep(.t-input__inner):focus {
  border-color: #00f0ff;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.3), 0 0 5px rgba(138, 43, 226, 0.2);
  outline: none;
}

.edit-input :deep(.t-input__inner)::placeholder {
  color: rgba(255, 255, 255, 0.4);
}
</style>
