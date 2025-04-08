&lt;template>
  &lt;a-menu
    v-model:selectedKeys="selectedKeys"
    v-model:openKeys="openKeys"
    mode="inline"
    theme="dark"
    :inline-collapsed="collapsed"
  >
    &lt;a-menu-item key="dashboard" @click="navigateTo('/')">
      &lt;template #icon>
        &lt;dashboard-outlined />
      &lt;/template>
      &lt;span>首页&lt;/span>
    &lt;/a-menu-item>

    &lt;a-menu-item key="test-results" @click="navigateTo('/test-results')">
      &lt;template #icon>
        &lt;bar-chart-outlined />
      &lt;/template>
      &lt;span>成绩查询&lt;/span>
    &lt;/a-menu-item>

    &lt;a-menu-item key="test-plans" @click="navigateTo('/test-plans')">
      &lt;template #icon>
        &lt;calendar-outlined />
      &lt;/template>
      &lt;span>测试计划&lt;/span>
    &lt;/a-menu-item>

    &lt;a-menu-item key="physical-standards" @click="navigateTo('/physical-standards')">
      &lt;template #icon>
        &lt;trophy-outlined />
      &lt;/template>
      &lt;span>体测标准&lt;/span>
    &lt;/a-menu-item>

    &lt;a-menu-item key="health-reports" @click="navigateTo('/health-reports')">
      &lt;template #icon>
        &lt;medicine-box-outlined />
      &lt;/template>
      &lt;span>健康报告&lt;/span>
    &lt;/a-menu-item>

    &lt;a-menu-item key="notifications" @click="navigateTo('/notifications')">
      &lt;template #icon>
        &lt;notification-outlined />
      &lt;/template>
      &lt;span>补考通知&lt;/span>
    &lt;/a-menu-item>

    &lt;a-menu-item key="profile" @click="navigateTo('/profile')">
      &lt;template #icon>
        &lt;user-outlined />
      &lt;/template>
      &lt;span>个人信息&lt;/span>
    &lt;/a-menu-item>
  &lt;/a-menu>
&lt;/template>

&lt;script setup>
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
&lt;/script>

&lt;style scoped>
.ant-menu {
  height: 100%;
}
&lt;/style>
