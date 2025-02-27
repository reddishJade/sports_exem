<template>
  <div class="login-container">
    <a-card title="体测管理系统登录" style="width: 400px">
      <a-form
        :model="formState"
        name="basic"
        :label-col="{ span: 8 }"
        :wrapper-col="{ span: 16 }"
        autocomplete="off"
        @finish="onFinish"
      >
        <a-form-item
          label="用户名"
          name="username"
          :rules="[{ required: true, message: '请输入用户名!' }]"
        >
          <a-input v-model:value="formState.username" />
        </a-form-item>

        <a-form-item
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码!' }]"
        >
          <a-input-password v-model:value="formState.password" />
        </a-form-item>

        <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
          <a-button type="primary" html-type="submit">登录</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script>
import { defineComponent, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'

export default defineComponent({
  name: 'LoginView',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const formState = reactive({
      username: '',
      password: ''
    })

    const onFinish = async (values) => {
      const success = await store.dispatch('login', values)
      if (success) {
        message.success('登录成功')
        router.push('/')
      } else {
        message.error('登录失败，请检查用户名和密码')
      }
    }

    return {
      formState,
      onFinish
    }
  }
})
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
}
</style>
