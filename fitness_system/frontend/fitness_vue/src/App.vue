<template>
  <a-config-provider :locale="zhCN">
    <div class="app-container">
      <template v-if="isAuthenticated">
        <a-layout style="min-height: 100vh">
          <a-layout-sider v-model:collapsed="collapsed" collapsible>
            <div class="logo">
              <h2 v-if="!collapsed">体测管理系统</h2>
              <h2 v-else>体测</h2>
            </div>
            <a-menu
              v-model:selectedKeys="selectedKeys"
              theme="dark"
              mode="inline"
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
              
              <a-menu-item key="/test-results">
                <template #icon>
                  <FileTextOutlined />
                </template>
                <router-link to="/test-results">测试成绩</router-link>
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
            </a-menu>
          </a-layout-sider>
          
          <a-layout>
            <a-layout-header style="background: #fff; padding: 0">
              <div class="header-right">
                <a-dropdown>
                  <a class="ant-dropdown-link" @click.prevent>
                    <UserOutlined /> {{ username }}
                    <DownOutlined />
                  </a>
                  <template #overlay>
                    <a-menu>
                      <a-menu-item key="logout" @click="handleLogout">
                        <LogoutOutlined /> 退出登录
                      </a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
              </div>
            </a-layout-header>
            
            <a-layout-content style="margin: 0 16px">
              <router-view></router-view>
            </a-layout-content>
            
            <a-layout-footer style="text-align: center">
              体测管理系统 2025 Created by Your Company
            </a-layout-footer>
          </a-layout>
        </a-layout>
      </template>
      
      <template v-else>
        <router-view></router-view>
      </template>
    </div>
  </a-config-provider>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import {
  HomeOutlined,
  TeamOutlined,
  CalendarOutlined,
  FileTextOutlined,
  BarChartOutlined,
  MedicineBoxOutlined,
  UserOutlined,
  DownOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'

const store = useStore()
const router = useRouter()
const route = useRoute()

const collapsed = ref(false)
const selectedKeys = ref([route.path])

const isAuthenticated = computed(() => store.getters.isAuthenticated)
const isAdmin = computed(() => store.getters.isAdmin)
const username = computed(() => store.state.user?.username || '')

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
.app-container {
  height: 100vh;
}

.logo {
  height: 32px;
  margin: 16px;
  color: white;
  text-align: center;
  overflow: hidden;
}

.logo h2 {
  color: white;
  margin: 0;
  font-size: 18px;
}

.header-right {
  float: right;
  margin-right: 24px;
}

.ant-dropdown-link {
  color: rgba(0, 0, 0, 0.85);
}

:deep(.ant-layout-header) {
  padding: 0 24px;
}

:deep(.ant-menu-item a) {
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
}

:deep(.ant-menu-item-selected a) {
  color: #fff;
}
</style>
