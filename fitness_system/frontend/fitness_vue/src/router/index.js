import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/Login.vue'
import store from '../store'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/students',
      name: 'students',
      component: () => import('../views/StudentList.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/test-plans',
      name: 'test-plans',
      component: () => import('../views/TestPlan.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/test-results',
      name: 'test-results',
      component: () => import('../views/TestResult.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/scores',
      name: 'TestResults',
      component: () => import('../views/TestResults.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/physical-standards',
      name: 'physical-standards',
      component: () => import('../views/PhysicalStandard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/health-reports',
      name: 'health-reports',
      component: () => import('../views/HealthReport.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated
  const isAdmin = store.getters.isAdmin

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
