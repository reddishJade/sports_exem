<template>
  <div class="login-container">
    <div class="login-background">
      <div class="login-overlay"></div>
    </div>
    <div class="login-content">
      <div class="login-header">
        <h1 class="system-title">体测管理系统</h1>
        <p class="system-subtitle">专业的体育测试管理平台</p>
      </div>
      <a-card class="login-card" :bordered="false">
        <a-tabs v-model:activeKey="activeKey" class="login-tabs">
          <a-tab-pane key="login" tab="登录">
            <a-form
              :model="loginForm"
              :rules="loginRules"
              ref="loginFormRef"
              @finish="handleLogin"
              class="login-form"
            >
              <a-form-item name="username">
                <a-input
                  v-model:value="loginForm.username"
                  placeholder="用户名"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <user-outlined class="input-icon" />
                  </template>
                </a-input>
              </a-form-item>
              <a-form-item name="password">
                <a-input-password
                  v-model:value="loginForm.password"
                  placeholder="密码"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <lock-outlined class="input-icon" />
                  </template>
                </a-input-password>
              </a-form-item>
              <a-form-item>
                <a-button
                  type="primary"
                  html-type="submit"
                  :loading="loading"
                  block
                  size="large"
                  class="submit-button"
                >
                  登录
                </a-button>
              </a-form-item>
            </a-form>
          </a-tab-pane>
          
          <a-tab-pane key="register" tab="注册">
            <a-form
              :model="registerForm"
              :rules="registerRules"
              ref="registerFormRef"
              @finish="handleRegister"
              class="login-form"
            >
              <a-form-item name="username">
                <a-input
                  v-model:value="registerForm.username"
                  placeholder="用户名"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <user-outlined class="input-icon" />
                  </template>
                </a-input>
              </a-form-item>
              <a-form-item name="email">
                <a-input
                  v-model:value="registerForm.email"
                  placeholder="邮箱"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <mail-outlined class="input-icon" />
                  </template>
                </a-input>
              </a-form-item>
              <a-form-item name="password">
                <a-input-password
                  v-model:value="registerForm.password"
                  placeholder="密码"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <lock-outlined class="input-icon" />
                  </template>
                </a-input-password>
              </a-form-item>
              <a-form-item name="confirmPassword">
                <a-input-password
                  v-model:value="registerForm.confirmPassword"
                  placeholder="确认密码"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <lock-outlined class="input-icon" />
                  </template>
                </a-input-password>
              </a-form-item>
              <a-form-item>
                <a-button
                  type="primary"
                  html-type="submit"
                  :loading="loading"
                  block
                  size="large"
                  class="submit-button"
                >
                  注册
                </a-button>
              </a-form-item>
            </a-form>
          </a-tab-pane>
        </a-tabs>
      </a-card>
      <div class="login-footer">
        <p> 2025 体测管理系统 · 版权所有</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

const store = useStore()
const router = useRouter()
const route = useRoute()
const activeKey = ref('login')
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loading = computed(() => store.getters.isLoading)

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value) => {
        if (value !== registerForm.value.password) {
          return Promise.reject('两次输入的密码不一致')
        }
        return Promise.resolve()
      },
      trigger: 'blur'
    }
  ]
}

const handleLogin = async () => {
  try {
    await store.dispatch('login', loginForm.value)
    message.success('登录成功')
    const redirect = route.query.redirect || '/'
    await router.push(redirect)
  } catch (error) {
    console.error('Login error:', error)
    message.error(error.response?.data?.detail || '登录失败')
  }
}

const handleRegister = async () => {
  try {
    await store.dispatch('register', {
      username: registerForm.value.username,
      password: registerForm.value.password,
      email: registerForm.value.email
    })
    message.success('注册成功')
    router.push('/')
  } catch (error) {
    console.error('Register error:', error)
    message.error(error.response?.data?.detail || '注册失败')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('https://images.unsplash.com/photo-1517649763962-0c623066013b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1920&q=80');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: -2;
}

.login-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  z-index: -1;
}

.login-content {
  width: 100%;
  max-width: 420px;
  padding: 20px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
  animation: fadeInDown 1s;
}

.system-title {
  color: #fff;
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.system-subtitle {
  color: #e6f7ff;
  font-size: 16px;
  font-weight: 400;
  margin: 0;
  opacity: 0.8;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.login-card {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: fadeInUp 1s;
  background: rgba(255, 255, 255, 0.95);
}

.login-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 24px;
}

.login-tabs :deep(.ant-tabs-tab) {
  padding: 12px 16px;
  font-size: 16px;
}

.login-form {
  padding: 8px 4px;
}

.form-input {
  height: 48px;
  border-radius: 4px;
}

.input-icon {
  color: #bfbfbf;
}

.submit-button {
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 4px;
  margin-top: 8px;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.35);
  transition: all 0.3s;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.5);
}

.login-footer {
  margin-top: 24px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  font-size: 14px;
  animation: fadeInUp 1.5s;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 576px) {
  .login-content {
    padding: 16px;
  }
  
  .system-title {
    font-size: 28px;
  }
  
  .system-subtitle {
    font-size: 14px;
  }
}
</style>
