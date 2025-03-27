<template>
  <div class="news-list">
    <h1 class="page-title">体育新闻</h1>
    
    <a-spin :spinning="loading">
      <a-row :gutter="[16, 16]">
        <!-- 置顶新闻 -->
        <a-col :span="24" v-if="featuredNews.length > 0">
          <a-card class="featured-news-card" :bordered="false">
            <a-row :gutter="16">
              <a-col :span="8" v-if="featuredNews[0].featured_image">
                <a-image 
                  :src="featuredNews[0].featured_image" 
                  class="featured-image" 
                  :preview="false"
                />
              </a-col>
              <a-col :span="featuredNews[0].featured_image ? 16 : 24">
                <div class="featured-content">
                  <div class="featured-tag">置顶</div>
                  <h2 @click="viewNews(featuredNews[0].id)" class="news-title">
                    {{ featuredNews[0].title }}
                  </h2>
                  <div class="news-meta">
                    <span v-if="featuredNews[0].source_name">来源: {{ featuredNews[0].source_name }}</span>
                    <span>{{ formatDate(featuredNews[0].pub_date) }}</span>
                    <span>{{ featuredNews[0].views }} 次阅读</span>
                  </div>
                  <a-button 
                    type="primary" 
                    @click="viewNews(featuredNews[0].id)" 
                    class="read-btn"
                  >
                    阅读全文
                  </a-button>
                </div>
              </a-col>
            </a-row>
          </a-card>
        </a-col>
        
        <!-- 新闻列表 -->
        <template v-if="normalNews.length > 0">
          <a-col :span="8" v-for="news in normalNews" :key="news.id">
            <a-card hoverable @click="viewNews(news.id)">
              <template #cover v-if="news.featured_image">
                <img :src="news.featured_image" class="card-cover-image" />
              </template>
              <a-card-meta :title="news.title">
                <template #description>
                  <div class="news-meta">
                    <span v-if="news.source_name">来源: {{ news.source_name }}</span>
                    <span>{{ formatDate(news.pub_date) }}</span>
                    <span>{{ news.views }} 次浏览</span>
                  </div>
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
        </template>
        
        <!-- 空状态 -->
        <a-col :span="24" v-if="newsList.length === 0 && !loading">
          <a-empty description="暂无新闻" />
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'

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
  return date.toLocaleString('zh-CN')
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
.news-list {
  padding: 24px;
}

.page-title {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 600;
}

.featured-news-card {
  margin-bottom: 16px;
  background-color: #fafafa;
}

.featured-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.featured-content {
  position: relative;
  padding: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.featured-tag {
  display: inline-block;
  background-color: #f5222d;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  font-size: 12px;
}

.news-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  cursor: pointer;
}

.news-title:hover {
  color: #1890ff;
}

.news-meta {
  color: #999;
  font-size: 12px;
  margin-bottom: 16px;
}

.news-meta span {
  margin-right: 16px;
}

.read-btn {
  margin-top: auto;
}

.card-cover-image {
  height: 160px;
  object-fit: cover;
}

.pagination {
  margin-top: 32px;
  text-align: center;
}
</style>
