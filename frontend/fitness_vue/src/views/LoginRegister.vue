<!--
  @description 带有登录和注册功能的组合组件
  @author Cascade AI
  @date 2025-03-27
  @version 1.0.0
  @roles 所有用户 - 主要登录入口
-->
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
    await loginFormRef.value.validate()
    const success = await store.dispatch('login', loginForm.value)
    if (success) {
      message.success('登录成功')
      const redirectPath = route.query.redirect || '/'
      router.push(redirectPath)
    } else {
      message.error('登录失败，请检查用户名和密码')
    }
  } catch (error) {
    console.error('Login validation failed:', error)
  }
}

const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    const success = await store.dispatch('register', registerForm.value)
    if (success) {
      message.success('注册成功，请登录')
      activeKey.value = 'login'
      registerForm.value = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    } else {
      message.error('注册失败，请稍后再试')
    }
  } catch (error) {
    console.error('Register validation failed:', error)
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: relative;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/src/assets/login-bg.jpg');
  background-size: cover;
  background-position: center;
  z-index: -1;
}

.login-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 0;
}

.login-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.system-title {
  font-size: 2.5rem;
  font-weight: bold;
  letter-spacing: 2px;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.system-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  letter-spacing: 1px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
}

.login-tabs {
  margin-top: -16px;
}

.login-form {
  padding: 1rem 0.5rem;
}

.form-input {
  height: 50px;
  border-radius: 4px;
}

.input-icon {
  color: rgba(0, 0, 0, 0.45);
}

.submit-button {
  height: 50px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 4px;
  margin-top: 8px;
}

.login-footer {
  margin-top: 2rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .login-card {
    max-width: 90%;
  }
  
  .system-title {
    font-size: 2rem;
  }
  
  .system-subtitle {
    font-size: 1rem;
  }
}
</style>
