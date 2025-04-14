import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

import App from './App.vue'
import router from './router'
import store from './store'

// 注意：不再使用全局axios配置
// 所有API请求都应通过 @/services/api.js 进行

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(store)
app.use(Antd)

app.mount('#app')
