<template>
  <div class="home">
    <a-row :gutter="24">
      <a-col :xs="24" :sm="24" :md="8" class="dashboard-card-col">
        <a-card 
          class="dashboard-card" 
          :bordered="false"
          :loading="loading"
        >
          <template #title>
            <div class="card-title">
              <calendar-outlined />
              <span>待测试计划</span>
            </div>
          </template>
          <template #extra>
            <a @click="router.push('/test-plans')" class="more-link">
              更多
              <right-outlined />
            </a>
          </template>
          <a-list :data-source="upcomingTests" :loading="loading" class="dashboard-list">
            <template #renderItem="{ item }">
              <a-list-item class="dashboard-list-item">
                <a @click="viewTestPlan(item)" style="display: block; width: 100%;">
                  <a-list-item-meta
                    :title="item.title"
                    :description="item.test_date"
                  >
                    <template #avatar>
                      <a-avatar shape="square" class="list-avatar" style="background-color: var(--primary-color)">
                        <form-outlined />
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                </a>
              </a-list-item>
            </template>
            <template #empty>
              <div class="empty-placeholder">
                <inbox-outlined />
                <p>暂无待测试计划</p>
              </div>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="24" :md="8" class="dashboard-card-col">
        <a-card 
          class="dashboard-card" 
          :bordered="false"
          :loading="loading"
        >
          <template #title>
            <div class="card-title">
              <trophy-outlined />
              <span>最近成绩</span>
            </div>
          </template>
          <template #extra>
            <a @click="router.push('/test-results')" class="more-link">
              更多
              <right-outlined />
            </a>
          </template>
          <a-list :data-source="recentResults" :loading="loading" class="dashboard-list">
            <template #renderItem="{ item }">
              <a-list-item class="dashboard-list-item">
                <a @click="viewTestResult(item)" style="display: block; width: 100%;">
                  <a-list-item-meta
                    :title="item.total_score ? `总分: ${item.total_score}` : '暂无成绩'"
                    :description="item.test_date"
                  >
                    <template #avatar>
                      <a-avatar shape="square" class="list-avatar" :style="{backgroundColor: getScoreColor(item.total_score || 0)}">
                        <line-chart-outlined />
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                  <div v-if="item.total_score" class="score-badge" :class="getScoreClass(item.total_score)">
                    {{ getScoreText(item.total_score) }}
                  </div>
                </a>
              </a-list-item>
            </template>
            <template #empty>
              <div class="empty-placeholder">
                <file-unknown-outlined />
                <p>暂无成绩记录</p>
              </div>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="24" :md="8" class="dashboard-card-col">
        <a-card 
          class="dashboard-card" 
          :bordered="false"
          :loading="loading"
        >
          <template #title>
            <div class="card-title">
              <heart-outlined />
              <span>健康建议</span>
            </div>
          </template>
          <template #extra>
            <a @click="router.push('/health-reports')" class="more-link">
              更多
              <right-outlined />
            </a>
          </template>
          <a-list :data-source="healthTips" :loading="loading" class="dashboard-list">
            <template #renderItem="{ item }">
              <a-list-item class="dashboard-list-item">
                <a @click="viewHealthTip(item)" style="display: block; width: 100%;">
                  <a-list-item-meta
                    :title="item.title"
                    :description="item.description"
                  >
                    <template #avatar>
                      <a-avatar shape="square" class="list-avatar" style="background-color: #52c41a">
                        <medicine-box-outlined />
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                </a>
              </a-list-item>
            </template>
            <template #empty>
              <div class="empty-placeholder">
                <smile-outlined />
                <p>暂无健康建议</p>
              </div>
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="24" class="chart-row">
      <a-col :span="24">
        <a-card 
          title="体质健康趋势" 
          :bordered="false"
          class="chart-card"
        >
          <template #title>
            <div class="card-title">
              <bar-chart-outlined />
              <span>体质健康趋势</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="chartRef" style="width: 100%; height: 300px;"></div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="24" class="chart-row">
      <a-col :span="24">
        <a-card 
          :bordered="false" 
          class="news-card"
        >
          <template #title>
            <div class="card-title">
              <read-outlined />
              <span>每日体育新闻</span>
            </div>
          </template>
          <template #extra>
            <a @click="router.push('/news')" class="more-link">
              更多
              <right-outlined />
            </a>
          </template>
          <a-spin :spinning="newsLoading">
            <a-list itemLayout="horizontal" :dataSource="newsList" class="news-list">
              <template #renderItem="{ item }">
                <a-list-item class="news-item" @click="router.push(`/news/${item.id}`)">
                  <a-list-item-meta
                    :title="item.title"
                    :description="formatDate(item.pub_date)"
                  >
                    <template #avatar v-if="item.featured_image">
                      <a-avatar shape="square" :size="64" :src="item.featured_image" class="news-avatar" />
                    </template>
                    <template #avatar v-else>
                      <a-avatar shape="square" :size="64" class="news-avatar">
                        <picture-outlined />
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                  <a-button type="primary" ghost @click.stop="router.push(`/news/${item.id}`)" class="read-more-btn">阅读全文</a-button>
                </a-list-item>
              </template>
              <template #empty>
                <div class="empty-placeholder">
                  <read-outlined />
                  <p>暂无新闻</p>
                </div>
              </template>
            </a-list>
          </a-spin>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Store, useStore } from 'vuex'
import axios from 'axios'
import * as echarts from 'echarts'
import { 
  CalendarOutlined, 
  TrophyOutlined, 
  HeartOutlined, 
  BarChartOutlined, 
  ReadOutlined, 
  LineChartOutlined,
  MedicineBoxOutlined,
  FormOutlined,
  InboxOutlined,
  FileUnknownOutlined,
  SmileOutlined,
  PictureOutlined,
  RightOutlined
} from '@ant-design/icons-vue'

interface HealthReport {
  health_suggestions: string
}

interface TestPlan {
  id: number
  title: string
  date: string
}

interface TestResult {
  id: number
  score: number
  date: string
}

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
const newsLoading = ref(false)
const upcomingTests = ref([])
const recentResults = ref([])
const healthTips = ref([])
const newsList = ref([])
const chartRef = ref<HTMLDivElement | null>(null)
let chart: any = null

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getScoreColor = (score: number): string => {
  if (score >= 90) return '#52c41a'
  if (score >= 80) return '#1890ff'
  if (score >= 70) return '#faad14'
  if (score >= 60) return '#fa8c16'
  return '#f5222d'
}

const getScoreClass = (score: number): string => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

const getScoreText = (score: number): string => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

const initChart = () => {
  // Make sure chartRef.value exists before initializing
  if (!chartRef.value) return

  // Dispose of previous chart instance if it exists
  if (chart) {
    chart.dispose()
  }

  // Initialize ECharts instance
  chart = echarts.init(chartRef.value as HTMLDivElement)
  
  // 模拟数据，后续可以替换为真实数据
  const option: any = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['BMI', '肺活量', '50米跑', '立定跳远', '总分']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [{
      type: 'category',
      boundaryGap: false,
      data: ['2024春季', '2024秋季', '2025春季']
    }],
    yAxis: [{
      type: 'value'
    }],
    series: [
      {
        name: 'BMI',
        type: 'line',
        stack: 'Total',
        data: [22, 21.5, 21.8],
        smooth: true,
        lineStyle: {
          width: 2
        }
      },
      {
        name: '肺活量',
        type: 'line',
        stack: 'Total',
        data: [70, 75, 80],
        smooth: true,
        lineStyle: {
          width: 2
        }
      },
      {
        name: '50米跑',
        type: 'line',
        stack: 'Total',
        data: [65, 70, 75],
        smooth: true,
        lineStyle: {
          width: 2
        }
      },
      {
        name: '立定跳远',
        type: 'line',
        stack: 'Total',
        data: [75, 80, 80],
        smooth: true,
        lineStyle: {
          width: 2
        }
      },
      {
        name: '总分',
        type: 'line',
        stack: 'Total',
        data: [72, 76, 80],
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        lineStyle: {
          width: 4,
          shadowColor: 'rgba(0,0,0,0.3)',
          shadowBlur: 10,
          shadowOffsetY: 10
        },
        itemStyle: {
          borderWidth: 3
        }
      }
    ]
  };
  
  chart.setOption(option);
}

// Define resize handler as a separate function for proper cleanup
const handleResize = () => {
  chart?.resize()
}

const fetchData = async () => {
  loading.value = true
  try {
    // 获取待测试计划
    const testPlansResponse = await axios.get('http://localhost:8000/api/test-plans/', {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    upcomingTests.value = testPlansResponse.data.slice(0, 5)

    // 获取最近成绩
    const resultsResponse = await axios.get('http://localhost:8000/api/test-results/', {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    recentResults.value = resultsResponse.data.slice(0, 5)

    // 获取健康建议
    const reportsResponse = await axios.get('http://localhost:8000/api/health-reports/', {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    healthTips.value = reportsResponse.data.slice(0, 5).map((report: any) => ({
      title: '健康建议',
      description: report.health_suggestions.slice(0, 50) + '...'
    }))

  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchNews = async () => {
  newsLoading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/news/', {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    newsList.value = response.data.slice(0, 5)
  } catch (error) {
    console.error('获取新闻失败:', error)
  } finally {
    newsLoading.value = false
  }
}

const viewTestResult = (result: any) => {
  router.push(`/test-results/${result.id}`)
}

const viewTestPlan = (plan: any) => {
  router.push(`/test-plans/${plan.id}`)
}

const viewHealthTip = (tip: any) => {
  router.push(`/health-reports/${tip.id}`)
}

onMounted(() => {
  fetchData()
  fetchNews()
  setTimeout(initChart, 500)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.home {
  padding: 0;
}

.dashboard-card-col {
  margin-bottom: 24px;
}

.dashboard-card {
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16),
              0 3px 6px 0 rgba(0, 0, 0, 0.12),
              0 5px 12px 4px rgba(0, 0, 0, 0.09);
}

.dashboard-card:hover {
  box-shadow: 0 3px 6px -4px rgba(0, 0, 0, 0.16),
              0 6px 16px 0 rgba(0, 0, 0, 0.12),
              0 9px 28px 8px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.card-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: var(--text-color);
}

.card-title :deep(svg) {
  margin-right: 8px;
  font-size: 18px;
  color: var(--primary-color);
}

.more-link {
  display: flex;
  align-items: center;
  color: var(--primary-color);
  font-size: 14px;
  transition: all 0.3s;
}

.more-link:hover {
  color: var(--dark-primary-color);
}

.more-link :deep(svg) {
  margin-left: 4px;
  font-size: 12px;
}

.dashboard-list {
  margin-top: 8px;
}

.dashboard-list-item {
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.dashboard-list-item:hover {
  background-color: var(--light-primary-color);
  padding-left: 8px;
}

.dashboard-list-item:last-child {
  border-bottom: none;
}

.list-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  color: white;
}

.score-excellent {
  background-color: #52c41a;
}

.score-good {
  background-color: #1890ff;
}

.score-average {
  background-color: #faad14;
}

.score-pass {
  background-color: #fa8c16;
}

.score-fail {
  background-color: #f5222d;
}

.chart-row {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16),
              0 3px 6px 0 rgba(0, 0, 0, 0.12),
              0 5px 12px 4px rgba(0, 0, 0, 0.09);
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 0;
}

.news-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16),
              0 3px 6px 0 rgba(0, 0, 0, 0.12),
              0 5px 12px 4px rgba(0, 0, 0, 0.09);
}

.news-list {
  margin-top: 8px;
}

.news-item {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.3s;
  cursor: pointer;
}

.news-item:hover {
  background-color: var(--light-primary-color);
}

.news-avatar {
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.read-more-btn {
  transition: all 0.3s;
}

.empty-placeholder {
  padding: 32px 0;
  text-align: center;
  color: rgba(0, 0, 0, 0.25);
}

.empty-placeholder :deep(svg) {
  font-size: 32px;
  margin-bottom: 8px;
}

.empty-placeholder p {
  font-size: 14px;
  margin: 0;
}
</style>
