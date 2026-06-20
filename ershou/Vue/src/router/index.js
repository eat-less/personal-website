import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Home from '../views/Home.vue';
import Profile from '../views/Profile.vue';
import Publish from '../views/Publish.vue';
import ProductDetail from '../views/ProductDetail.vue';
import PasswordReset from '../views/PasswordReset.vue';
import Messages from '../views/Messages.vue';
import MessageDetail from '../views/MessageDetail.vue';
import Transactions from '../views/Transactions.vue';
import Announcements from '../views/Announcements.vue';
import AdminDashboard from '../views/AdminDashboard.vue';
import NotFound from '../views/NotFound.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
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
    path: '/password-reset',
    name: 'PasswordReset',
    component: PasswordReset
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile/:id',
    name: 'UserProfile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/publish',
    name: 'Publish',
    component: Publish,
    meta: { requiresAuth: true }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: ProductDetail
  },
  {
    path: '/messages',
    name: 'Messages',
    component: Messages,
    meta: { requiresAuth: true }
  },
  {
    path: '/messages/:userId',
    name: 'MessageDetail',
    component: MessageDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: Transactions,
    meta: { requiresAuth: true }
  },
  {
    path: '/announcements',
    name: 'Announcements',
    component: Announcements,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫：检查用户是否已登录
router.beforeEach((to, from, next) => {
  const isAuthenticated = sessionStorage.getItem('access_token');
  const userInfo = JSON.parse(sessionStorage.getItem('user_info'));
  const isAdmin = userInfo?.is_admin || false;
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: 'Login' });
    } else if (to.matched.some(record => record.meta.requiresAdmin)) {
      if (isAdmin) {
        next();
      } else {
        next({ name: 'Home' });
      }
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
