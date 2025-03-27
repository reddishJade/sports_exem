<template>
  <div class="news-detail">
    <a-card v-if="news" :bordered="false">
      <template #title>
        <div class="news-title">
          <h1>{{ news.title }}</h1>
          <div class="news-meta">
            <span v-if="news.source_name">来源: {{ news.source_name }}</span>
            <span class="news-date">{{ formatDate(news.pub_date) }}</span>
            <span class="news-views">{{ news.views }} 次阅读</span>
          </div>
        </div>
      </template>
      
      <a-image 
        v-if="news.featured_image" 
        :src="news.featured_image" 
        class="featured-image" 
        alt="特色图片"
        :preview="false"
      />
      
      <div class="news-content" v-html="news.content"></div>
      
      <a-divider />
      
      <!-- 评论区域 -->
      <div class="comment-section">
        <h3>评论 ({{ comments.length }})</h3>
        
        <!-- 评论表单 - 仅对学生显示 -->
        <div v-if="userType === 'student'" class="comment-form">
          <a-form :model="commentForm" @finish="submitComment">
            <a-form-item name="content" :rules="[{ required: true, message: '请输入评论内容' }]">
              <a-textarea 
                v-model:value="commentForm.content" 
                :rows="4" 
                placeholder="请输入您的评论..."
              />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="submitting">
                提交评论
              </a-button>
              <a-alert 
                v-if="submitMessage" 
                :message="submitMessage" 
                :type="submitSuccess ? 'success' : 'warning'" 
                style="margin-top: 16px"
              />
            </a-form-item>
          </a-form>
        </div>
        
        <!-- 非学生用户提示 -->
        <a-alert 
          v-if="userType !== 'student'" 
          message="只有学生账户可以发表评论" 
          type="info" 
          style="margin-bottom: 16px"
        />
        
        <!-- 评论列表 -->
        <a-list 
          v-if="comments.length > 0" 
          :data-source="comments" 
          item-layout="horizontal"
        >
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta
                :title="item.student_name"
                :description="formatDate(item.created_at)"
              >
                <template #avatar>
                  <a-avatar>{{ item.student_name?.[0] || 'U' }}</a-avatar>
                </template>
              </a-list-item-meta>
              <div class="comment-content">{{ item.content }}</div>
            </a-list-item>
          </template>
        </a-list>
        
        <div v-else class="no-comments">
          <p>暂无评论，成为第一个评论的人吧！</p>
        </div>
      </div>
    </a-card>
    
    <a-skeleton v-else :loading="loading" active />
    
    <div class="actions">
      <a-button @click="router.push('/news')" style="margin-top: 16px">
        返回新闻列表
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'

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
const userType = ref(store.state.userType || '')
const commentForm = ref({
  content: '',
  news: null as number | null
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
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
.news-detail {
  padding: 24px;
}

.news-title {
  margin-bottom: 16px;
}

.news-title h1 {
  margin-bottom: 8px;
  font-size: 24px;
}

.news-meta {
  color: #999;
  font-size: 14px;
}

.news-meta span {
  margin-right: 16px;
}

.featured-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  margin-bottom: 16px;
  border-radius: 4px;
}

.news-content {
  font-size: 16px;
  line-height: 1.8;
  margin-top: 24px;
}

.comment-section {
  margin-top: 32px;
}

.comment-form {
  margin-bottom: 24px;
  border: 1px solid #f0f0f0;
  padding: 16px;
  border-radius: 4px;
  background-color: #fafafa;
}

.comment-content {
  margin: 0 16px;
}

.no-comments {
  text-align: center;
  color: #999;
  padding: 32px 0;
}

.actions {
  display: flex;
  justify-content: center;
}
</style>
