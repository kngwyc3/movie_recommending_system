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

// 全局路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const isLoggedIn = token !== null && token !== '';

  // 检查页面是否需要登录
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  console.log('路由守卫:', {
    to: to.path,
    from: from.path,
    requiresAuth,
    isLoggedIn
  });

  if (requiresAuth && !isLoggedIn) {
    // 未登录访问需要认证的页面，跳转到登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    });
  } else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    // 已登录用户访问登录/注册页，跳转到首页
    next('/');
  } else {
    next();
  }
});

export default router;
