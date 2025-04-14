<!--
  @description 新闻详情视图组件 - 显示单条新闻的完整内容
  @roles 所有用户
  @features
    - 展示新闻标题、来源和发布时间
    - 完整展示新闻正文内容
    - 支持图文混排和富文本格式
    - 提供返回新闻列表功能
-->
<template>
  <div class="news-detail-container">
    <div class="news-detail">
      <a-card v-if="news" :bordered="false" class="news-content-card">
        <template #title>
          <div class="news-header">
            <div class="news-title">
              <h1>{{ news.title }}</h1>
              <div class="news-meta">
                <span v-if="news.source_name"><read-outlined /> {{ news.source_name }}</span>
                <span class="news-date"><calendar-outlined /> {{ formatDate(news.pub_date) }}</span>
                <span class="news-views"><eye-outlined /> {{ news.views }} 次阅读</span>
              </div>
            </div>
            <a-button @click="router.push('/news')" class="back-button">
              <left-outlined /> 返回新闻列表
            </a-button>
          </div>
        </template>
        
        <div class="news-main-content">
          <a-image 
            v-if="news.featured_image" 
            :src="news.featured_image" 
            class="featured-image" 
            alt="特色图片"
            :preview="false"
          />
          
          <div class="news-article" v-html="news.content"></div>
        </div>
        
        <a-divider class="comment-divider">
          <message-outlined /> 评论区
        </a-divider>
        
        <!-- 评论区域 -->
        <div class="comment-section">
          <h3 class="comment-title">评论 ({{ comments.length }})</h3>
          
          <!-- 评论表单 - 仅对学生显示 -->
          <div v-if="userType === 'student'" class="comment-form">
            <a-form :model="commentForm" @finish="submitComment">
              <a-form-item name="content" :rules="[{ required: true, message: '请输入评论内容' }]">
                <a-textarea 
                  v-model:value="commentForm.content" 
                  :rows="4" 
                  placeholder="请输入您的评论..."
                  class="comment-textarea"
                />
              </a-form-item>
              <a-form-item>
                <a-button type="primary" html-type="submit" :loading="submitting" class="submit-btn">
                  <comment-outlined /> 提交评论
                </a-button>
                <a-alert 
                  v-if="submitMessage" 
                  :message="submitMessage" 
                  :type="submitSuccess ? 'success' : 'warning'" 
                  style="margin-top: 16px"
                  class="alert-message"
                />
              </a-form-item>
            </a-form>
          </div>
          
          <!-- 非学生用户提示 -->
          <a-alert 
            v-if="userType !== 'student'" 
            message="只有学生账户可以发表评论" 
            type="info" 
            class="comment-alert"
            show-icon
          />
          
          <!-- 评论列表 -->
          <transition-group name="comment-list" tag="div" class="comments-container">
            <a-list 
              v-if="comments.length > 0" 
              :data-source="comments" 
              item-layout="horizontal"
              class="comment-list"
            >
              <template #renderItem="{ item }">
                <a-list-item class="comment-item">
                  <a-list-item-meta
                    :title="item.student_name || '匿名用户'"
                    :description="formatDate(item.created_at)"
                  >
                    <template #avatar>
                      <a-avatar class="comment-avatar" :style="{ backgroundColor: getAvatarColor(item.student_name) }">
                        {{ item.student_name?.[0] || 'U' }}
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                  <div class="comment-content">{{ item.content }}</div>
                </a-list-item>
              </template>
            </a-list>
  
            <div v-if="comments.length === 0" key="no-comments" class="no-comments">
              <a-empty description="暂无评论，成为第一个评论的人吧！" />
            </div>
          </transition-group>
        </div>
      </a-card>
      
      <a-skeleton v-else :loading="loading" active />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'
import { 
  ReadOutlined, 
  CalendarOutlined, 
  EyeOutlined, 
  LeftOutlined,
  CommentOutlined,
  MessageOutlined
} from '@ant-design/icons-vue'

interface News {
  id: number
  title: string
  content: string
  pub_date: string
  featured_image: string | null
  source_name: string | null
  source_url: string | null
  views: number
}

interface Comment {
  id: number
  student_name: string
  content: string
  created_at: string
  is_approved: boolean
}

const route = useRoute()
const router = useRouter()
const store = useStore()
const loading = ref(true)
const submitting = ref(false)
const submitSuccess = ref(false)
const submitMessage = ref('')
const news = ref<News | null>(null)
const comments = ref<Comment[]>([])
const userType = ref(store.getters.userType || '')
const commentForm = ref({
  content: '',
  news: null as number | null
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getAvatarColor = (name: string) => {
  const colors = ['#1890ff', '#ff69b4', '#ff9900', '#33cc33', '#6666cc']
  const index = Math.abs(name.charCodeAt(0)) % colors.length
  return colors[index]
}

const fetchNews = async () => {
  loading.value = true
  try {
    const newsId = route.params.id
    // 获取新闻详情
    const newsResponse = await axios.get(`http://localhost:8000/api/news/${newsId}/`, {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    news.value = newsResponse.data
    commentForm.value.news = newsResponse.data.id
    
    // 增加浏览次数
    await axios.post(`http://localhost:8000/api/news/${newsId}/increment_views/`, {}, {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    
    // 获取评论
    await fetchComments(newsId)
  } catch (error) {
    console.error('获取新闻详情失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchComments = async (newsId: string | string[]) => {
  try {
    const response = await axios.get(`http://localhost:8000/api/news/${newsId}/comments/`, {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    comments.value = response.data
  } catch (error) {
    console.error('获取评论失败:', error)
  }
}

const submitComment = async () => {
  submitting.value = true
  submitMessage.value = ''
  try {
    // 确保用户类型是学生
    if (userType.value !== 'student') {
      submitMessage.value = '只有学生账户可以发表评论'
      submitSuccess.value = false
      return
    }
    
    const response = await axios.post('http://localhost:8000/api/news-comments/', {
      news: commentForm.value.news,
      content: commentForm.value.content
    }, {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    
    submitMessage.value = '评论已提交，等待管理员审核后显示'
    submitSuccess.value = true
    commentForm.value.content = ''
    
  } catch (error: any) {
    submitMessage.value = error.response?.data?.detail || '提交评论失败'
    submitSuccess.value = false
    console.error('提交评论失败:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchNews()
})
</script>

<style scoped>
.news-detail-container {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 16px;
}

.news-detail {
  max-width: 1000px;
  margin: 0 auto;
}

.news-content-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.news-title {
  flex: 1;
  min-width: 0;
}

.news-title h1 {
  margin-bottom: 12px;
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.4;
}

.news-meta {
  display: flex;
  flex-wrap: wrap;
  color: #888;
  font-size: 14px;
  margin-bottom: 8px;
}

.news-meta span {
  margin-right: 18px;
  margin-bottom: 8px;
  display: inline-flex;
  align-items: center;
}

.news-meta span :deep(svg) {
  margin-right: 6px;
}

.back-button {
  margin-left: 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  margin-top: 4px;
}

.featured-image {
  width: 100%;
  max-height: 500px;
  object-fit: cover;
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.news-main-content {
  padding: 0 8px;
}

.news-article {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.news-article :deep(p) {
  margin-bottom: 1.2em;
}

.news-article :deep(h2) {
  font-size: 1.5em;
  margin: 1.2em 0 0.8em;
  font-weight: 600;
  color: #1a1a1a;
}

.news-article :deep(h3) {
  font-size: 1.3em;
  margin: 1em 0 0.7em;
  font-weight: 600;
  color: #1a1a1a;
}

.news-article :deep(img) {
  max-width: 100%;
  border-radius: 6px;
  margin: 1em 0;
}

.comment-divider {
  margin: 40px 0 24px;
  color: #1a1a1a;
  font-weight: 600;
}

.comment-divider :deep(.ant-divider-inner-text) {
  display: flex;
  align-items: center;
}

.comment-divider :deep(svg) {
  margin-right: 8px;
}

.comment-section {
  padding: 0 8px;
  margin-top: 30px;
}

.comment-title {
  font-size: 18px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  color: var(--primary-color);
}

.comment-form {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
}

.comment-textarea {
  resize: none;
  min-height: 100px;
  border-radius: 4px;
  transition: all 0.3s;
}

.comment-textarea:focus, .comment-textarea:hover {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.submit-btn {
  margin-top: 10px;
}

.comment-alert {
  margin-bottom: 20px;
  border-radius: 4px;
}

.comments-container {
  margin-top: 20px;
}

.comment-list {
  width: 100%;
}

.comment-item {
  padding: 16px !important;
  border-radius: 8px;
  margin-bottom: 12px;
  background-color: #ffffff;
  transition: all 0.3s;
  border: 1px solid #f0f0f0;
}

.comment-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.comment-avatar {
  background-color: var(--primary-color);
}

.comment-content {
  margin-top: 8px;
  color: #333;
  line-height: 1.6;
}

.alert-message {
  margin-top: 16px;
}

.no-comments {
  padding: 40px 0;
  text-align: center;
  width: 100%;
}

/* 评论列表过渡效果 */
.comment-list-enter-active,
.comment-list-leave-active {
  transition: all 0.5s;
}

.comment-list-enter-from,
.comment-list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .news-title h1 {
    font-size: 22px;
  }
  
  .back-button {
    margin-left: 0;
    margin-top: 12px;
  }
  
  .news-header {
    flex-direction: column;
  }
  
  .featured-image {
    max-height: 300px;
  }
}
</style>
