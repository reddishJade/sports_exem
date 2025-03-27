<template>
  <div class="notifications-container">
    <a-page-header
      title="补考通知"
      sub-title="查看您的补考信息和通知"
      :backIcon="false"
    />
    
    <a-card class="notifications-card">
      <template #extra>
        <a-button type="primary" @click="refreshNotifications">
          <reload-outlined />刷新
        </a-button>
      </template>
      
      <a-list
        class="notification-list"
        :data-source="notifications"
        :loading="loading"
        item-layout="horizontal"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #avatar>
                <a-avatar :style="{ backgroundColor: getStatusColor(item.status) }">
                  <template v-if="item.status === 'unread'">
                    <notification-outlined />
                  </template>
                  <template v-else-if="item.status === 'important'">
                    <warning-outlined />
                  </template>
                  <template v-else>
                    <check-circle-outlined />
                  </template>
                </a-avatar>
              </template>
              <template #title>
                <div class="notification-title">
                  <span>{{ item.title }}</span>
                  <a-tag 
                    v-if="item.status === 'unread'" 
                    color="blue"
                  >
                    未读
                  </a-tag>
                  <a-tag 
                    v-else-if="item.status === 'important'" 
                    color="red"
                  >
                    重要
                  </a-tag>
                </div>
              </template>
              <template #description>
                <div class="notification-description">
                  <div class="notification-content">{{ item.content }}</div>
                  <div class="notification-date">{{ formatDate(item.created_at) }}</div>
                </div>
              </template>
            </a-list-item-meta>
            <template #actions>
              <a-button 
                type="link" 
                @click="markAsRead(item)"
                v-if="item.status === 'unread'"
              >
                标为已读
              </a-button>
            </template>
          </a-list-item>
        </template>
        <template #empty>
          <div class="empty-container">
            <inbox-outlined style="font-size: 48px; color: #ccc" />
            <p>暂无补考通知</p>
          </div>
        </template>
      </a-list>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  NotificationOutlined, 
  WarningOutlined, 
  CheckCircleOutlined, 
  InboxOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import store from '../store'

const loading = ref(false)
const notifications = ref([])

const getStatusColor = (status) => {
  switch (status) {
    case 'unread':
      return '#1890ff'
    case 'important':
      return '#ff4d4f'
    default:
      return '#52c41a'
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    // 使用新创建的notifications端点
    const response = await axios.get('http://localhost:8000/api/notifications/', {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    
    // 通知数据格式处理
    notifications.value = response.data.map(notification => ({
      id: notification.id,
      title: '体测补考通知',
      content: `您有一项体测成绩不合格，需要参加补考。补考计划：${notification.test_plan.title}，地点：${notification.test_plan.location}`,
      created_at: notification.sent_at || new Date().toISOString(),
      status: notification.is_read ? 'read' : 'important'
    }))
    
    loading.value = false
  } catch (error) {
    console.error('获取通知失败:', error)
    message.error('获取通知失败，请稍后重试')
    loading.value = false
  }
}

const markAsRead = async (notification) => {
  try {
    // 使用新创建的mark_as_read端点标记为已读
    await axios.post(`http://localhost:8000/api/notifications/${notification.id}/mark_as_read/`, {}, {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    
    // 更新本地状态
    notification.status = 'read'
    message.success('已标记为已读')
  } catch (error) {
    console.error('标记已读失败:', error)
    message.error('操作失败，请稍后重试')
  }
}

const refreshNotifications = () => {
  fetchNotifications()
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notifications-container {
  padding: 24px;
}

.notifications-card {
  margin-top: 24px;
}

.notification-list {
  margin-top: 16px;
}

.notification-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.notification-description {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notification-date {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 0;
  color: #999;
}
</style>
