<template>
  <div class="login-container">
    <a-card class="login-card" :bordered="false">
      <a-tabs v-model:activeKey="activeKey">
        <a-tab-pane key="login" tab="登录">
          <a-form
            :model="loginForm"
            :rules="loginRules"
            ref="loginFormRef"
            @finish="handleLogin"
          >
            <a-form-item name="username">
              <a-input
                v-model:value="loginForm.username"
                placeholder="用户名"
                size="large"
              >
                <template #prefix>
                  <user-outlined />
                </template>
              </a-input>
            </a-form-item>
            <a-form-item name="password">
              <a-input-password
                v-model:value="loginForm.password"
                placeholder="密码"
                size="large"
              >
                <template #prefix>
                  <lock-outlined />
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
          >
            <a-form-item name="username">
              <a-input
                v-model:value="registerForm.username"
                placeholder="用户名"
                size="large"
              >
                <template #prefix>
                  <user-outlined />
                </template>
              </a-input>
            </a-form-item>
            <a-form-item name="email">
              <a-input
                v-model:value="registerForm.email"
                placeholder="邮箱"
                size="large"
              >
                <template #prefix>
                  <mail-outlined />
                </template>
              </a-input>
            </a-form-item>
            <a-form-item name="password">
              <a-input-password
                v-model:value="registerForm.password"
                placeholder="密码"
                size="large"
              >
                <template #prefix>
                  <lock-outlined />
                </template>
              </a-input-password>
            </a-form-item>
            <a-form-item name="confirmPassword">
              <a-input-password
                v-model:value="registerForm.confirmPassword"
                placeholder="确认密码"
                size="large"
              >
                <template #prefix>
                  <lock-outlined />
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
              >
                注册
              </a-button>
            </a-form-item>
          </a-form>
        </a-tab-pane>
      </a-tabs>
    </a-card>
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
    message.error(error.response?.data?.error || '注册失败')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 100%;
  max-width: 400px;
  margin: 0 16px;
}

:deep(.ant-card-body) {
  padding: 32px 24px;
}
</style>
