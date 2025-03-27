import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginRegister from '../views/LoginRegister.vue'
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
      component: LoginRegister
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
      path: '/test-plans/:id',
      name: 'test-plan-detail',
      component: () => import('../views/TestPlanDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/test-results',
      name: 'test-results',
      component: () => import('../views/TestResultManagement.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/test-results/:id',
      name: 'test-result-detail',
      component: () => import('../views/StudentTestResultDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/test-results-input',
      name: 'test-results-input',
      component: () => import('../views/TestResultInput.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/test-results-analysis',
      name: 'test-results-analysis',
      component: () => import('../views/TestResultAnalysis.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/test-results-reports',
      name: 'test-results-reports',
      component: () => import('../views/TestResultReports.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/scores',
      name: 'TestResults',
      component: () => import('../views/StudentTestResults.vue'),
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
    },
    {
      path: '/health-reports/:id',
      name: 'health-report-detail',
      component: () => import('../views/HealthReportDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/news',
      name: 'news-list',
      component: () => import('../views/NewsList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/news/:id',
      name: 'news-detail',
      component: () => import('../views/NewsDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: () => import('../views/Notifications.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/Profile.vue'),
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
