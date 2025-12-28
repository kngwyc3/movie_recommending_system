import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import MovieDetail from '../views/MovieDetail.vue';
import Categories from '../views/Categories.vue';
import Recommendations from '../views/Recommendations.vue';
import Profile from '../views/Profile.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/recommendations',
    name: 'Recommendations',
    component: Recommendations,
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: Categories
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/movie/:id',
    name: 'MovieDetail',
    component: MovieDetail,
    props: route => ({ id: parseInt(route.params.id) })
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    return { top: 0 };
  }
});

// 全局路由守卫：检查登录状态和token有效性
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token');
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  // 如果需要认证
  if (requiresAuth) {
    if (!token) {
      // 没有token，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
      return;
    }

    // 验证token是否有效
    try {
      const response = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        // token无效或过期，清除登录状态
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('isLoggedIn');
        
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        });
        return;
      }

      // token有效，继续导航
      next();
    } catch (error) {
      console.error('Token验证失败:', error);
      // 验证失败，清除登录状态
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('isLoggedIn');
      
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
    }
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    // 已登录用户访问登录/注册页，跳转到首页
    next('/');
  } else {
    next();
  }
});

export default router;
