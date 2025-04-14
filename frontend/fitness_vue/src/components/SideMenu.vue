<template>
  <a-menu
    v-model:selectedKeys="selectedKeys"
    v-model:openKeys="openKeys"
    mode="inline"
    theme="dark"
    :inline-collapsed="collapsed"
  >
    <a-menu-item key="dashboard" @click="navigateTo('/')">
      <template #icon>
        <dashboard-outlined />
      </template>
      <span>首页</span>
    </a-menu-item>

    <a-menu-item key="test-results" @click="navigateTo('/test-results')">
      <template #icon>
        <bar-chart-outlined />
      </template>
      <span>成绩查询</span>
    </a-menu-item>

    <a-menu-item key="test-plans" @click="navigateTo('/test-plans')">
      <template #icon>
        <calendar-outlined />
      </template>
      <span>测试计划</span>
    </a-menu-item>

    <a-menu-item key="physical-standards" @click="navigateTo('/physical-standards')">
      <template #icon>
        <trophy-outlined />
      </template>
      <span>体测标准</span>
    </a-menu-item>

    <a-menu-item key="health-reports" @click="navigateTo('/health-reports')">
      <template #icon>
        <medicine-box-outlined />
      </template>
      <span>健康报告</span>
    </a-menu-item>

    <a-menu-item key="notifications" @click="navigateTo('/notifications')">
      <template #icon>
        <notification-outlined />
      </template>
      <span>补考通知</span>
    </a-menu-item>

    <a-menu-item key="profile" @click="navigateTo('/profile')">
      <template #icon>
        <user-outlined />
      </template>
      <span>个人信息</span>
    </a-menu-item>
  </a-menu>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined,
  BarChartOutlined,
  CalendarOutlined,
  TrophyOutlined,
  MedicineBoxOutlined,
  NotificationOutlined,
  UserOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()
const route = useRoute()
const selectedKeys = ref([route.path.split('/')[1] || 'dashboard'])
const openKeys = ref(['dashboard'])

const navigateTo = (path) => {
  router.push(path)
}

watch(
  () => route.path,
  (path) => {
    selectedKeys.value = [path.split('/')[1] || 'dashboard']
  }
)
</script>

<style scoped>
.ant-menu {
  height: 100%;
}
</style>
