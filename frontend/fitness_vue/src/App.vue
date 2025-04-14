<!--
  @description 应用主布局组件 - 包含侧边栏、顶部导航和内容区域
  @author Fitness System Team
  @date 2025-04-13
  @version 1.2.0
  @roles 所有用户
  @features 
    - 响应式布局设计
    - 根据用户角色动态显示菜单项
    - 用户信息弹窗
    - 深色/浅色主题切换
-->
<template>
  <a-config-provider :locale="zhCN">
    <div class="app-container">
      <template v-if="isAuthenticated">
        <a-layout style="min-height: 100vh">
          <a-layout-sider
            v-model:collapsed="collapsed"
            collapsible
            class="custom-sider"
            :trigger="null"
            :width="240"
          >
            <div class="logo-container">
              <div class="logo">
                <span class="logo-icon">
                  <DashboardOutlined />
                </span>
                <h2 v-if="!collapsed" class="logo-text">体测管理系统</h2>
              </div>
            </div>
            <a-menu
              v-model:selectedKeys="selectedKeys"
              theme="dark"
              mode="inline"
              class="custom-menu"
            >
              <a-menu-item key="/">
                <template #icon>
                  <HomeOutlined />
                </template>
                <router-link to="/">首页</router-link>
              </a-menu-item>
              
              <a-menu-item key="/students" v-if="isAdmin">
                <template #icon>
                  <TeamOutlined />
                </template>
                <router-link to="/students">学生管理</router-link>
              </a-menu-item>
              
              <a-menu-item key="/test-plans">
                <template #icon>
                  <CalendarOutlined />
                </template>
                <router-link to="/test-plans">测试计划</router-link>
              </a-menu-item>
              
              <!-- 成绩管理子菜单 -->
              <a-sub-menu key="test-results-sub" v-if="isAdmin">
                <template #icon>
                  <FileTextOutlined />
                </template>
                <template #title>成绩管理</template>
                
                <a-menu-item key="/test-results">
                  <router-link to="/test-results">成绩总览</router-link>
                </a-menu-item>
                
                <a-menu-item key="/test-results-input">
                  <router-link to="/test-results-input">成绩录入</router-link>
                </a-menu-item>
                
                <a-menu-item key="/test-results-analysis">
                  <router-link to="/test-results-analysis">成绩分析</router-link>
                </a-menu-item>
                
                <a-menu-item key="/test-results-reports">
                  <router-link to="/test-results-reports">成绩报表</router-link>
                </a-menu-item>
              </a-sub-menu>
              
              <a-menu-item key="/scores" v-if="!isAdmin">
                <template #icon>
                  <TrophyOutlined />
                </template>
                <router-link to="/scores">我的成绩</router-link>
              </a-menu-item>
              
              <a-menu-item key="/physical-standards">
                <template #icon>
                  <BarChartOutlined />
                </template>
                <router-link to="/physical-standards">体测标准</router-link>
              </a-menu-item>
              
              <a-menu-item key="/health-reports">
                <template #icon>
                  <MedicineBoxOutlined />
                </template>
                <router-link to="/health-reports">体质报告</router-link>
              </a-menu-item>
              
              <a-menu-item key="/news">
                <template #icon>
                  <ReadOutlined />
                </template>
                <router-link to="/news">体育新闻</router-link>
              </a-menu-item>

              <a-menu-item key="/notifications">
                <template #icon>
                  <NotificationOutlined />
                </template>
                <router-link to="/notifications">补考通知</router-link>
              </a-menu-item>

              <a-menu-item key="/ai-chat">
                <template #icon>
                  <MessageOutlined />
                </template>
                <router-link to="/ai-chat">AI助手</router-link>
              </a-menu-item>

              <a-menu-item key="/profile">
                <template #icon>
                  <UserOutlined />
                </template>
                <router-link to="/profile">个人信息</router-link>
              </a-menu-item>
            </a-menu>
          </a-layout-sider>
          
          <a-layout class="site-layout">
            <a-layout-header class="site-header">
              <div class="header-left">
                <a-button
                  type="text"
                  class="trigger-button" 
                  @click="collapsed = !collapsed"
                >
                  <MenuFoldOutlined v-if="!collapsed" />
                  <MenuUnfoldOutlined v-else />
                </a-button>
                <breadcrumb-nav />
              </div>
              <div class="header-right">
                <a-badge status="success" text="在线" style="margin-right: 16px;" />
                <a-dropdown placement="bottomRight">
                  <div class="user-dropdown-link">
                    <a-avatar class="user-avatar" :style="{ backgroundColor: avatarColor }">
                      {{ usernameFirstChar }}
                    </a-avatar>
                    <span class="username">{{ username }}</span>
                    <span class="user-type">{{ userTypeText }}</span>
                    <DownOutlined />
                  </div>
                  <template #overlay>
                    <a-menu class="user-dropdown-menu">
                      <a-menu-item key="profile" @click="showUserInfoModal">
                        <UserOutlined /> 个人信息
                      </a-menu-item>
                      <a-menu-divider />
                      <a-menu-item key="logout" @click="handleLogout">
                        <LogoutOutlined /> 退出登录
                      </a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
                
                <!-- 用户信息弹窗 -->
                <a-modal
                  v-model:open="userInfoModalVisible"
                  title="个人信息"
                  :footer="null"
                  width="500px"
                >
                  <div class="user-info-modal">
                    <div class="user-info-header">
                      <a-avatar :size="80" :style="{ backgroundColor: avatarColor }">
                        {{ usernameFirstChar }}
                      </a-avatar>
                      <div class="user-info-name">
                        <h2>{{ username }}</h2>
                        <a-tag :color="userTypeColor">{{ userTypeText }}</a-tag>
                      </div>
                    </div>
                    
                    <a-divider />
                    
                    <a-descriptions bordered>
                      <a-descriptions-item label="用户名" :span="3">
                        {{ username }}
                      </a-descriptions-item>
                      <a-descriptions-item label="用户类型" :span="3">
                        {{ userTypeText }}
                      </a-descriptions-item>
                      <a-descriptions-item label="邮箱" :span="3">
                        {{ store.state.user?.email || '未设置' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="最后登录" :span="3">
                        {{ formatDate(store.state.user?.last_login) || '未记录' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="账号创建日期" :span="3">
                        {{ formatDate(store.state.user?.date_joined) || '未记录' }}
                      </a-descriptions-item>
                    </a-descriptions>
                    
                    <template v-if="store.state.user?.user_type === 'student' && store.state.user?.student_profile">
                      <a-divider>学生信息</a-divider>
                      <a-descriptions bordered>
                        <a-descriptions-item label="学号" :span="3">
                          {{ store.state.user.student_profile.student_id || '未设置' }}
                        </a-descriptions-item>
                        <a-descriptions-item label="班级" :span="3">
                          {{ store.state.user.student_profile.class_name || '未设置' }}
                        </a-descriptions-item>
                        <a-descriptions-item label="专业" :span="3">
                          {{ store.state.user.student_profile.major || '未设置' }}
                        </a-descriptions-item>
                        <a-descriptions-item label="年级" :span="3">
                          {{ store.state.user.student_profile.grade || '未设置' }}
                        </a-descriptions-item>
                      </a-descriptions>
                    </template>
                    
                    <div class="user-info-actions">
                      <a-button type="primary" @click="userInfoModalVisible = false">
                        关闭
                      </a-button>
                    </div>
                  </div>
                </a-modal>
              </div>
            </a-layout-header>
            
            <a-layout-content class="site-content">
              <div class="content-wrapper">
                <router-view v-slot="{ Component }">
                  <transition name="fade">
                    <div :key="$route.fullPath" class="route-wrapper">
                      <component :is="Component" />
                    </div>
                  </transition>
                </router-view>
              </div>
            </a-layout-content>
            
            <a-layout-footer class="footer">
              <div class="footer-content">
                <span>体测管理系统 2025</span>
                <span>|</span>
                <span>打造专业体育测试管理平台</span>
              </div>
            </a-layout-footer>
          </a-layout>
        </a-layout>
      </template>
      
      <template v-else>
        <router-view v-slot="{ Component }">
          <transition name="fade">
            <div :key="$route.fullPath" class="route-wrapper">
              <component :is="Component" />
            </div>
          </transition>
        </router-view>
      </template>
    </div>
  </a-config-provider>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { message } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { 
  HomeOutlined,
  TeamOutlined,
  CalendarOutlined,
  FileTextOutlined,
  TrophyOutlined,
  BarChartOutlined,
  MedicineBoxOutlined,
  ReadOutlined,
  BellOutlined,
  MessageOutlined,
  UserOutlined,
  DashboardOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LoginOutlined,
  SettingOutlined,
  ProfileOutlined,
  LogoutOutlined,
  NotificationOutlined,
  DownOutlined
} from '@ant-design/icons-vue'
// 定义内联的 BreadcrumbNav 组件
const BreadcrumbNav = {
  template: `
    <a-breadcrumb class="breadcrumb">
      <a-breadcrumb-item v-for="(item, index) in breadcrumbItems" :key="index">
        {{ item }}
      </a-breadcrumb-item>
    </a-breadcrumb>
  `,
  setup() {
    const route = useRoute()
    const breadcrumbItems = computed(() => {
      const paths = route.path.split('/').filter(Boolean)
      if (paths.length === 0) return ['首页']
      
      const items = ['首页']
      const pathMap = {
        'students': '学生管理',
        'test-plans': '测试计划',
        'test-results': '成绩管理',
        'scores': '我的成绩',
        'physical-standards': '体测标准',
        'health-reports': '体质报告',
        'news': '体育新闻',
        'notifications': '补考通知',
        'ai-chat': 'AI助手',
        'profile': '个人信息'
      }
      
      paths.forEach(path => {
        if (pathMap[path]) {
          items.push(pathMap[path])
        }
      })
      
      return items
    })
    
    return {
      breadcrumbItems
    }
  }
}

const store = useStore()
const router = useRouter()
const route = useRoute()

// 应用初始化时加载用户详细信息（包含学生资料）
onMounted(async () => {
  if (store.getters.isAuthenticated) {
    try {
      await store.dispatch('fetchCurrentUser')
      console.log('用户信息已加载', store.state.user)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
})

const collapsed = ref(false)
const selectedKeys = ref([route.path])

const isAuthenticated = computed(() => store.getters.isAuthenticated)
const isAdmin = computed(() => store.getters.isAdmin)
const username = computed(() => store.state.user?.username || '')

const avatarColor = computed(() => {
  const colors = ['#f56a00', '#7265e6', '#ffbf00', '#00a2ae']
  const index = username.value.charCodeAt(0) % colors.length
  return colors[index]
})

const usernameFirstChar = computed(() => username.value.charAt(0).toUpperCase())

const userTypeText = computed(() => {
  if (isAdmin.value) return '管理员'
  if (store.state.user?.user_type === 'student') return '学生'
  return '未知'
})

const userTypeColor = computed(() => {
  if (isAdmin.value) return 'blue'
  if (store.state.user?.user_type === 'student') return 'green'
  return 'gray'
})

const userInfoModalVisible = ref(false)

const showUserInfoModal = () => {
  userInfoModalVisible.value = true
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()
  return `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')} ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}:${second.toString().padStart(2, '0')}`
}

watch(
  () => route.path,
  (newPath) => {
    selectedKeys.value = [newPath]
  }
)

const handleLogout = async () => {
  try {
    await store.dispatch('logout')
    message.success('已退出登录')
    router.push('/login')
  } catch (error) {
    message.error('退出失败')
  }
}
</script>

<style>
:root {
  --primary-color: #1890ff;
  --dark-primary-color: #096dd9;
  --light-primary-color: #e6f7ff;
  --secondary-color: #00c1d4;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #f5222d;
  --background-color: #f0f2f5;
  --text-color: rgba(0, 0, 0, 0.85);
  --text-secondary: rgba(0, 0, 0, 0.45);
  --border-radius: 4px;
  --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  --header-height: 64px;
  --footer-height: 64px;
  --sider-width: 240px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-color);
  background-color: var(--background-color);
}

.app-container {
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏样式 */
.custom-sider {
  position: relative;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.25);
  z-index: 10;
  transition: all 0.2s;
  background: linear-gradient(180deg, #001529 0%, #002140 100%);
}

.logo-container {
  position: relative;
  padding: 16px;
  overflow: hidden;
  transition: all 0.3s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  height: 32px;
}

.logo-icon {
  font-size: 24px;
  color: var(--primary-color);
  margin-right: 12px;
  display: flex;
  align-items: center;
}

.logo-text {
  color: white;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: opacity 0.3s;
}

.custom-menu {
  border-right: 0;
  padding-top: 8px;
}

.custom-menu :deep(.ant-menu-item) {
  margin: 4px 0;
  border-radius: 0 22px 22px 0;
  margin-right: 12px;
  transition: all 0.3s;
}

.custom-menu :deep(.ant-menu-item:hover) {
  background-color: rgba(24, 144, 255, 0.1);
}

.custom-menu :deep(.ant-menu-item-selected) {
  background-color: var(--primary-color);
}

.custom-menu :deep(.ant-menu-item a) {
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  transition: all 0.3s;
}

.custom-menu :deep(.ant-menu-item-selected a) {
  color: #fff;
}

/* 主体布局样式 */
.site-layout {
  transition: all 0.3s;
  background-color: var(--background-color);
}

.site-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  z-index: 9;
  height: var(--header-height);
}

.header-left {
  display: flex;
  align-items: center;
}

.trigger-button {
  height: 64px;
  width: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s;
}

.trigger-button:hover {
  color: var(--primary-color);
}

.breadcrumb {
  margin-left: 8px;
}

.header-right {
  display: flex;
  align-items: center;
  padding-right: 24px;
}

.user-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.user-dropdown-link:hover {
  background: rgba(0, 0, 0, 0.03);
}

.username {
  margin-left: 8px;
  font-weight: 500;
}

.user-type {
  font-size: 12px;
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: 8px;
}

.user-avatar {
  background-color: var(--primary-color);
}

.user-dropdown-menu {
  min-width: 160px;
}

.user-info-modal {
  .user-info-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 24px;
  }

  .user-info-name {
    display: flex;
    flex-direction: column;

    h2 {
      margin-bottom: 8px;
      font-size: 24px;
    }
  }

  .user-info-actions {
    margin-top: 24px;
    display: flex;
    justify-content: flex-end;
  }
}

/* 内容区域样式 */
.site-content {
  padding: 24px;
  overflow-y: auto;
  height: calc(100vh - var(--header-height));
  max-height: calc(100vh - var(--header-height));
}

.content-wrapper {
  background: white;
  padding: 24px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  min-height: 100px;
  height: auto;
  overflow-y: visible;
}

/* 页脚样式 */
.footer {
  padding: 20px 0;
  text-align: center;
  background: #f5f5f5;
}

.footer-content {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  color: #666;
  font-size: 14px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .site-content {
    padding: 12px;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .username {
    display: none;
  }
}
</style>
