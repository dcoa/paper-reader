import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { 
      title: '登录',
      requiresAuth: false 
    }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { 
      title: '首页',
      requiresAuth: true 
    }
  },
  {
    path: '/papers',
    name: 'PaperList',
    component: () => import('@/views/PaperList.vue'),
    meta: { 
      title: '文献列表',
      requiresAuth: true 
    }
  },
  {
    path: '/upload',
    name: 'PaperUpload',
    component: () => import('@/views/PaperUpload.vue'),
    meta: { 
      title: '上传文献',
      requiresAuth: true 
    }
  },
  {
    path: '/paper/:id',
    name: 'PaperDetail',
    component: () => import('@/views/PaperDetail.vue'),
    meta: { 
      title: '文献详情',
      requiresAuth: true 
    }
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('@/views/TestPage.vue'),
    meta: { 
      title: '环境测试',
      requiresAuth: false 
    }
  },

  // 管理员路由
  {
    path: '/admin',
    name: 'Admin',
    redirect: '/admin/dashboard',
    meta: { 
      title: '管理员控制台',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/AdminDashboard.vue'),
    meta: { 
      title: '管理员仪表板',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/views/AdminUsers.vue'),
    meta: { 
      title: '用户管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/papers',
    name: 'AdminPapers',
    component: () => import('@/views/AdminPapers.vue'),
    meta: { 
      title: '文献管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 科研加速Web应用`
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      next('/login')
      return
    }

    // 检查用户信息是否完整（防止跨域访问时用户信息混乱）
    if (!userStore.user || !userStore.user.user_id) {
      // 用户信息不完整，清除登录状态并重定向到登录页
      userStore.logout()
      next('/login')
      return
    }

    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin) {
      if (!userStore.isAdmin) {
        // 非管理员访问管理员页面，重定向到首页并提示
        next('/home')
        return
      }
    }
  }

  // 如果已登录访问登录页，重定向到首页
  if (to.name === 'Login' && userStore.isLoggedIn) {
    // 验证用户信息完整性
    if (userStore.user && userStore.user.user_id) {
      if (userStore.isAdmin) {
        next('/admin/dashboard')
      } else {
        next('/home')
      }
    } else {
      // 用户信息不完整，清除登录状态
      userStore.logout()
      next('/login')
    }
    return
  }

  next()
})

export default router 