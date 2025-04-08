<template>
  <div class="news-list-container">
    <div class="news-list">
      <div class="page-header">
        <h1 class="page-title">
          <read-outlined /> 体育新闻
        </h1>
        <div class="page-description">了解最新的体育资讯和健康知识</div>
      </div>
      
      <a-spin :spinning="loading">
        <a-row :gutter="[24, 24]">
          <!-- 置顶新闻 -->
          <a-col :span="24" v-if="featuredNews.length > 0">
            <a-card class="featured-news-card" :bordered="false" hoverable>
              <a-row :gutter="24">
                <a-col :span="10" v-if="featuredNews[0].featured_image">
                  <div class="featured-image-container">
                    <a-image 
                      :src="featuredNews[0].featured_image" 
                      class="featured-image" 
                      :preview="false"
                    />
                    <div class="featured-tag">置顶</div>
                  </div>
                </a-col>
                <a-col :span="featuredNews[0].featured_image ? 14 : 24">
                  <div class="featured-content">
                    <h2 @click="viewNews(featuredNews[0].id)" class="news-title featured-news-title">
                      {{ featuredNews[0].title }}
                    </h2>
                    <div class="news-meta">
                      <span v-if="featuredNews[0].source_name"><read-outlined /> {{ featuredNews[0].source_name }}</span>
                      <span><calendar-outlined /> {{ formatDate(featuredNews[0].pub_date) }}</span>
                      <span><eye-outlined /> {{ featuredNews[0].views }} 次阅读</span>
                    </div>
                    <a-button 
                      type="primary" 
                      @click="viewNews(featuredNews[0].id)" 
                      class="read-btn"
                    >
                      阅读全文 <right-outlined />
                    </a-button>
                  </div>
                </a-col>
              </a-row>
            </a-card>
          </a-col>
          
          <!-- 新闻列表 -->
          <template v-if="normalNews.length > 0">
            <a-col :xs="24" :sm="12" :md="8" v-for="news in normalNews" :key="news.id">
              <div class="news-card-container">
                <a-card hoverable @click="viewNews(news.id)" class="news-card">
                  <template #cover v-if="news.featured_image">
                    <div class="card-image-container">
                      <img :src="news.featured_image" class="card-cover-image" />
                    </div>
                  </template>
                  <a-card-meta :title="news.title">
                    <template #description>
                      <div class="news-meta">
                        <span v-if="news.source_name"><read-outlined /> {{ news.source_name }}</span>
                        <span><calendar-outlined /> {{ formatDate(news.pub_date) }}</span>
                        <span><eye-outlined /> {{ news.views }}</span>
                      </div>
                    </template>
                  </a-card-meta>
                </a-card>
              </div>
            </a-col>
          </template>
          
          <!-- 空状态 -->
          <a-col :span="24" v-if="newsList.length === 0 && !loading">
            <a-empty description="暂无新闻" class="empty-container" />
          </a-col>
        </a-row>
        
        <!-- 分页 -->
        <div class="pagination" v-if="newsList.length > 0">
          <a-pagination 
            v-model:current="currentPage" 
            :total="total" 
            show-size-changer 
            :page-size-options="['9', '18', '27']"
            v-model:pageSize="pageSize"
            @change="handlePageChange"
          />
        </div>
      </a-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'
import { 
  ReadOutlined, 
  CalendarOutlined, 
  EyeOutlined, 
  RightOutlined 
} from '@ant-design/icons-vue'

interface NewsItem {
  id: number
  title: string
  pub_date: string
  featured_image: string
  source_name: string
  is_featured: boolean
  views: number
}

const router = useRouter()
const store = useStore()
const loading = ref(false)
const newsList = ref<NewsItem[]>([])
const currentPage = ref(1)
const pageSize = ref(9)
const total = ref(0)

// 将新闻列表分为置顶和普通两部分
const featuredNews = computed(() => {
  return newsList.value.filter(news => news.is_featured)
})

const normalNews = computed(() => {
  return newsList.value.filter(news => !news.is_featured)
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

const fetchNews = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/news/', {
      headers: { Authorization: `Bearer ${store.state.token}` },
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    
    // 如果后端支持分页
    if (response.data.results) {
      newsList.value = response.data.results
      total.value = response.data.count
    } else {
      // 如果后端不支持分页，前端自行处理
      newsList.value = response.data
      total.value = response.data.length
    }
    
  } catch (error) {
    console.error('获取新闻失败:', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = () => {
  fetchNews()
}

const viewNews = (id: number) => {
  router.push(`/news/${id}`)
}

onMounted(() => {
  fetchNews()
})
</script>

<style scoped>
.news-list-container {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 16px;
  max-height: 100vh;
  overflow: auto;
}

.news-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-title {
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
}

.page-description {
  color: #666;
  font-size: 16px;
}

.featured-news-card {
  margin-bottom: 16px;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.featured-news-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.featured-image-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  height: 240px;
}

.featured-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.featured-image-container:hover .featured-image {
  transform: scale(1.05);
}

.featured-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  background-color: #f5222d;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  z-index: 2;
  box-shadow: 0 2px 6px rgba(245, 34, 45, 0.4);
}

.featured-content {
  position: relative;
  padding: 16px 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.news-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  cursor: pointer;
  color: #1a1a1a;
  transition: color 0.3s ease;
  line-height: 1.4;
}

.featured-news-title {
  font-size: 22px;
}

.news-title:hover {
  color: #1890ff;
}

.news-meta {
  color: #888;
  font-size: 13px;
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
}

.news-meta span {
  margin-right: 16px;
  margin-bottom: 8px;
  display: inline-flex;
  align-items: center;
}

.news-meta span :deep(svg) {
  margin-right: 4px;
}

.read-btn {
  margin-top: auto;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  padding: 6px 16px;
  height: auto;
}

.news-card-container {
  height: 100%;
  transition: transform 0.3s ease;
}

.news-card-container:hover {
  transform: translateY(-4px);
}

.news-card {
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-image-container {
  overflow: hidden;
  height: 180px;
}

.card-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.news-card:hover .card-cover-image {
  transform: scale(1.08);
}

.empty-container {
  margin: 60px 0;
  padding: 40px 0;
}

.pagination {
  margin-top: 48px;
  text-align: center;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .news-list {
    padding: 16px;
  }
  
  .featured-news-title {
    font-size: 20px;
  }
  
  .featured-image-container {
    height: 180px;
  }
}
</style>
