&lt;template>
  &lt;a-layout class="layout">
    &lt;a-layout-sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="sider"
    >
      &lt;div class="logo">
        &lt;img src="@/assets/logo.png" alt="Logo" />
        &lt;h1 v-show="!collapsed">体测管理系统&lt;/h1>
      &lt;/div>
      &lt;side-menu :collapsed="collapsed" />
    &lt;/a-layout-sider>

    &lt;a-layout>
      &lt;a-layout-header class="header">
        &lt;menu-unfold-outlined
          v-if="collapsed"
          class="trigger"
          @click="() => (collapsed = !collapsed)"
        />
        &lt;menu-fold-outlined
          v-else
          class="trigger"
          @click="() => (collapsed = !collapsed)"
        />
        &lt;div class="header-right">
          &lt;a-dropdown>
            &lt;a class="ant-dropdown-link" @click.prevent>
              {{ username }}
              &lt;down-outlined />
            &lt;/a>
            &lt;template #overlay>
              &lt;a-menu>
                &lt;a-menu-item key="profile" @click="navigateTo('/profile')">
                  个人信息
                &lt;/a-menu-item>
                &lt;a-menu-item key="logout" @click="handleLogout">
                  退出登录
                &lt;/a-menu-item>
              &lt;/a-menu>
            &lt;/template>
          &lt;/a-dropdown>
        &lt;/div>
      &lt;/a-layout-header>

      &lt;a-layout-content class="content">
        &lt;router-view>&lt;/router-view>
      &lt;/a-layout-content>

      &lt;a-layout-footer class="footer">
        体测管理系统 ©2025 Created by Your Name
      &lt;/a-layout-footer>
    &lt;/a-layout>
  &lt;/a-layout>
&lt;/template>

&lt;script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  DownOutlined
} from '@ant-design/icons-vue'
import SideMenu from './SideMenu.vue'

const router = useRouter()
const store = useStore()
const collapsed = ref(false)

const username = computed(() => store.state.user?.username || '未登录')

const navigateTo = (path) => {
  router.push(path)
}

const handleLogout = () => {
  store.dispatch('logout')
  router.push('/login')
}
&lt;/script>

&lt;style scoped>
.layout {
  min-height: 100vh;
}

.sider {
  overflow: auto;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
}

.logo {
  height: 32px;
  margin: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo img {
  height: 32px;
  margin-right: 8px;
}

.logo h1 {
  color: white;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header {
  background: #fff;
  padding: 0;
  position: fixed;
  width: 100%;
  z-index: 1;
}

.trigger {
  padding: 0 24px;
  font-size: 18px;
  line-height: 64px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.header-right {
  float: right;
  margin-right: 24px;
}

.content {
  margin: 64px 16px 0;
  overflow: initial;
  background: #fff;
  padding: 24px;
  min-height: 280px;
}

.footer {
  text-align: center;
  padding: 24px;
}

:deep(.ant-layout-sider-children) {
  display: flex;
  flex-direction: column;
}
&lt;/style>
