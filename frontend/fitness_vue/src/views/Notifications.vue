<template>
  <div class="notifications-container">
    <a-page-header
      title="补考通知中心"
      sub-title="查看您的补考信息和通知"
      :backIcon="false"
    />
    
    <a-card class="notifications-card">
      <template #title>
        <div class="card-header">
          <div class="card-title">
            <bell-outlined /> 
            <span>通知列表</span>
          </div>
        </div>
      </template>

      <div class="notification-filters">
        <a-row :gutter="16" align="middle">
          <a-col :xs="24" :sm="6">
            <a-input-search 
              placeholder="搜索通知..." 
              v-model:value="searchQuery"
              @search="handleSearch" 
              allow-clear
            />
          </a-col>
          <a-col :xs="24" :sm="5">
            <a-select 
              v-model:value="filterStatus" 
              placeholder="按状态筛选" 
              style="width: 100%" 
              @change="handleFilterChange"
            >
              <a-select-option value="all">全部</a-select-option>
              <a-select-option value="unread">未读</a-select-option>
              <a-select-option value="important">重要</a-select-option>
              <a-select-option value="read">已读</a-select-option>
            </a-select>
          </a-col>
          <a-col :xs="24" :sm="5">
            <a-select 
              v-model:value="sortBy" 
              placeholder="排序方式" 
              style="width: 100%" 
              @change="handleSortChange"
            >
              <a-select-option value="date-desc">最新优先</a-select-option>
              <a-select-option value="date-asc">最早优先</a-select-option>
              <a-select-option value="importance">按重要性</a-select-option>
            </a-select>
          </a-col>
          <a-col :xs="24" :sm="8" class="text-right">
            <a-button type="primary" @click="refreshNotifications" class="action-button">
              <reload-outlined /> 刷新
            </a-button>
            <a-button @click="markAllAsRead" class="action-button" :disabled="!hasUnreadNotifications">
              <check-outlined /> 全部标为已读
            </a-button>
          </a-col>
        </a-row>
      </div>
      
      <a-list
        class="notification-list"
        :data-source="filteredNotifications"
        :loading="loading"
        item-layout="horizontal"
        :pagination="{ pageSize: 5, showSizeChanger: true, pageSizeOptions: ['5', '10', '20'] }"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta class="notification-meta">
              <template #avatar>
                <a-avatar :style="{ backgroundColor: getStatusColor(item.status) }" class="notification-avatar">
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
                <div class="notification-content">
                  <p>
                    {{ formatNotificationContent(item) }}
                  </p>
                  <div v-if="item.related_test_result" class="related-links">
                    <a-button type="link" size="small" @click="viewTestDetail(item.related_test_result)" class="view-link">
                      <eye-outlined /> 查看测试详情
                    </a-button>
                  </div>
                  <div class="notification-time">{{ formatDate(item.created_at) }}</div>
                </div>
              </template>
            </a-list-item-meta>
            
            <template #actions>
              <a-space>
                <a-button 
                  type="text" 
                  size="small" 
                  @click="markAsRead(item)" 
                  v-if="item.status !== 'read'"
                  class="action-btn"
                >
                  <check-outlined /> 标为已读
                </a-button>
                <a-button 
                  type="text" 
                  size="small" 
                  @click="deleteNotification(item)" 
                  class="delete-btn"
                >
                  <delete-outlined /> 删除
                </a-button>
              </a-space>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NotificationOutlined, 
  WarningOutlined, 
  CheckCircleOutlined, 
  InboxOutlined,
  ReloadOutlined,
  DeleteOutlined,
  CheckOutlined,
  EyeOutlined,
  BellOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import store from '../store'

const loading = ref(false)
const notifications = ref([])
const searchQuery = ref('')
const filterStatus = ref('all')
const sortBy = ref('date-desc')

// 计算属性：过滤后的通知列表
const filteredNotifications = computed(() => {
  // 先过滤
  let filtered = notifications.value.filter(item => {
    // 按状态过滤
    if (filterStatus.value !== 'all' && item.status !== filterStatus.value) {
      return false
    }
    
    // 按搜索词过滤
    if (searchQuery.value) {
      const title = item.title || ''
      const content = item.content || ''
      if (!title.toLowerCase().includes(searchQuery.value.toLowerCase()) && 
          !content.toLowerCase().includes(searchQuery.value.toLowerCase())) {
        return false
      }
    }
    
    return true
  })
  
  // 再排序
  return [...filtered].sort((a, b) => {
    if (sortBy.value === 'date-desc') {
      return new Date(b.created_at) - new Date(a.created_at)
    } else if (sortBy.value === 'date-asc') {
      return new Date(a.created_at) - new Date(b.created_at)
    } else if (sortBy.value === 'importance') {
      // 重要 > 未读 > 已读
      const priorityMap = { 'important': 2, 'unread': 1, 'read': 0 }
      return priorityMap[b.status] - priorityMap[a.status]
    }
    return 0
  })
})

// 计算属性：是否有未读通知
const hasUnreadNotifications = computed(() => {
  return notifications.value.some(item => item.status !== 'read')
})

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
    
    // 通知数据格式处理 - 与体测结果相关联
    notifications.value = response.data.map(notification => {
      // 安全获取test_plan数据，避免undefined
      const testPlan = notification.test_plan || {}
      const testResult = notification.test_result || {}
      
      return {
        id: notification.id,
        title: '体测补考通知',
        content: `您有一项体测成绩不合格，需要参加补考。补考计划：${testPlan.title || '待定'}，地点：${testPlan.location || '待定'}`,
        created_at: notification.sent_at || new Date().toISOString(),
        status: notification.is_read ? 'read' : 'important',
        test_plan: testPlan,  // 保存完整的计划对象以供后续使用
        related_test_result: testResult.id  // 保存测试结果ID用于跳转
      }
    })
    
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

// 格式化通知内容，处理undefined问题
const formatNotificationContent = (notification) => {
  if (!notification) return ''
  
  // 处理test_plan可能不存在的情况
  const testPlan = notification.test_plan || {}
  const title = testPlan.title || '待定'
  const location = testPlan.location || '待定'
  const testDate = testPlan.test_date ? formatDate(testPlan.test_date) : '待定'
  
  if (notification.content) {
    // 替换content中的undefined字符串，使用正则表达式确保所有出现都被替换
    let formattedContent = notification.content
    formattedContent = formattedContent.replace(/undefined/g, title)
    formattedContent = formattedContent.replace(/undefined/g, location)
    return formattedContent
  }
  
  // 如果没有预设的content，生成一个默认的
  return `您有一项体测成绩不合格，需要参加补考。补考计划：${title}，时间：${testDate}，地点：${location}`
}

// 查看测试详情
const router = useRouter()
const viewTestDetail = (testResultId) => {
  if (!testResultId) {
    message.warning('无法找到相关测试记录')
    return
  }
  
  // 跳转到学生测试结果页面
  router.push({
    name: 'student-test-results',
    query: { highlight: testResultId }  // 添加查询参数以高亮显示特定测试
  })
}

// 删除通知
const deleteNotification = async (notification) => {
  try {
    await axios.delete(`http://localhost:8000/api/notifications/${notification.id}/`, {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    
    // 从列表中移除
    notifications.value = notifications.value.filter(item => item.id !== notification.id)
    message.success('已删除通知')
  } catch (error) {
    console.error('删除通知失败:', error)
    message.error('删除失败，请稍后重试')
  }
}

// 全部标为已读
const markAllAsRead = async () => {
  try {
    // 发送批量标记请求
    await axios.post('http://localhost:8000/api/notifications/mark_all_as_read/', {}, {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    
    // 更新本地状态
    notifications.value = notifications.value.map(item => ({...item, status: 'read'}))
    message.success('全部标记为已读')
  } catch (error) {
    console.error('标记全部已读失败:', error)
    message.error('操作失败，请稍后重试')
  }
}

// 处理搜索
const handleSearch = (value) => {
  searchQuery.value = value
}

// 处理过滤状态变化
const handleFilterChange = (value) => {
  filterStatus.value = value
}

// 处理排序方式变化
const handleSortChange = (value) => {
  sortBy.value = value
}

const refreshNotifications = () => {
  fetchNotifications()
  message.success('已刷新通知')
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notifications-container {
  padding: 24px;
  max-height: 100vh;
  overflow: auto;
  background-color: #f5f7fa;
}

.notifications-card {
  margin-top: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.notification-filters {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 6px;
}

.text-right {
  text-align: right;
}

.action-button {
  margin-left: 8px;
}

.notification-list {
  margin-top: 16px;
}

.notification-meta {
  width: 100%;
}

.notification-avatar {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.notification-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.status-tag {
  margin-left: auto;
}

.notification-content {
  margin-top: 8px;
  line-height: 1.6;
}

.notification-time {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  margin-top: 8px;
}

.related-links {
  margin-top: 8px;
  display: flex;
  gap: 12px;
}

.view-link {
  padding: 0;
  height: auto;
  font-size: 13px;
}

.action-btn, .delete-btn {
  opacity: 0.7;
  transition: all 0.2s;
}

.action-btn:hover, .delete-btn:hover {
  opacity: 1;
}

.delete-btn:hover {
  color: #ff4d4f;
}

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
  color: #999;
  background-color: #fafafa;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .action-button {
    margin: 8px 0 0 0;
    width: 100%;
  }
  
  .notification-filters a-col {
    margin-bottom: 12px;
  }
}
</style>
