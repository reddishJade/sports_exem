<!--
  @description 健康报告详情视图组件 - 显示学生体质健康报告的详细信息
  @roles 学生、家长、管理员
  @features
    - 展示学生健康报告的详细指标
    - 提供健康评估和分析图表
    - 包含个性化健康建议
    - 支持导出和打印报告
-->
<template>
  <div class="health-report-detail">
    <a-page-header
      title="健康报告详情"
      :subtitle="`学生: ${healthReport.student_name || '未知'}`"
      @back="$router.go(-1)"
    />

    <a-row :gutter="16">
      <a-col :span="16">
        <a-card :loading="loading" class="report-card">
          <a-descriptions title="基本信息" bordered>
            <a-descriptions-item label="报告编号">
              {{ healthReport.report_id }}
            </a-descriptions-item>
            <a-descriptions-item label="报告日期">
              {{ healthReport.report_date }}
            </a-descriptions-item>
            <a-descriptions-item label="报告类型">
              {{ healthReport.report_type }}
            </a-descriptions-item>
            <a-descriptions-item label="学生姓名">
              {{ healthReport.student_name }}
            </a-descriptions-item>
            <a-descriptions-item label="学号">
              {{ healthReport.student_id }}
            </a-descriptions-item>
            <a-descriptions-item label="班级">
              {{ healthReport.class_name }}
            </a-descriptions-item>
          </a-descriptions>

          <a-divider />

          <h3>健康指标</h3>
          <a-row :gutter="16" class="health-metrics">
            <a-col :span="8">
              <a-statistic 
                title="BMI指数" 
                :value="healthReport.bmi" 
                :value-style="{ color: getBMIColor(healthReport.bmi) }" 
              >
                <template #suffix>
                  <a-tag :color="getBMIStatus(healthReport.bmi).color">
                    {{ getBMIStatus(healthReport.bmi).text }}
                  </a-tag>
                </template>
              </a-statistic>
            </a-col>
            <a-col :span="8">
              <a-statistic 
                title="体重" 
                :value="healthReport.weight" 
                suffix="kg" 
              />
            </a-col>
            <a-col :span="8">
              <a-statistic 
                title="身高" 
                :value="healthReport.height" 
                suffix="cm" 
              />
            </a-col>
          </a-row>

          <a-divider />

          <div class="health-analysis">
            <h3>健康分析</h3>
            <div class="analysis-content">
              {{ healthReport.health_analysis || '暂无健康分析内容' }}
            </div>
          </div>

          <a-divider />

          <div class="health-suggestions">
            <h3>健康建议</h3>
            <div class="suggestions-content">
              <a-list 
                :data-source="healthReport.health_suggestions ? healthReport.health_suggestions.split('\n').filter(item => item.trim()) : []" 
                :bordered="false"
              >
                <template #renderItem="{ item }">
                  <a-list-item>
                    <check-circle-outlined style="color: #52c41a; margin-right: 8px;" />
                    {{ item }}
                  </a-list-item>
                </template>
                <template #empty>
                  <div>暂无健康建议</div>
                </template>
              </a-list>
            </div>
          </div>

          <a-divider />

          <div v-if="isStudent || isAdmin" class="comments-section">
            <h3>评论交流</h3>
            <a-list
              class="comment-list"
              :header="`${healthReport.comments?.length || 0} 条评论`"
              :data-source="healthReport.comments || []"
              :loading="commentsLoading"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-comment
                    :author="item.author"
                    :avatar="item.avatar || 'https://joeschmoe.io/api/v1/random'"
                    :content="item.content"
                    :datetime="item.datetime"
                  />
                </a-list-item>
              </template>
              <template #empty>
                <div>暂无评论</div>
              </template>
            </a-list>

            <a-divider />

            <!-- 学生身份才能发表评论 -->
            <div v-if="isStudent" class="comment-editor">
              <a-comment>
                <template #avatar>
                  <a-avatar :src="userAvatar" :alt="userName" />
                </template>
                <template #content>
                  <a-form-item>
                    <a-textarea v-model:value="commentValue" :rows="4" />
                  </a-form-item>
                  <a-form-item>
                    <a-button 
                      type="primary" 
                      :loading="submitting" 
                      @click="handleSubmitComment"
                    >
                      添加评论
                    </a-button>
                  </a-form-item>
                </template>
              </a-comment>
            </div>
          </div>

          <div class="action-buttons" style="margin-top: 24px; display: flex; justify-content: flex-end;">
            <a-button type="primary" style="margin-right: 8px;" @click="printReport">
              打印健康报告
            </a-button>
            <a-button @click="$router.go(-1)">
              返回
            </a-button>
          </div>
        </a-card>
      </a-col>
      
      <a-col :span="8">
        <a-card title="历史趋势" :loading="loading" class="trends-card">
          <div class="chart-container" ref="trendChartRef" style="height: 250px;"></div>
          
          <a-divider />
          
          <h4>体重变化</h4>
          <div ref="weightChartRef" style="height: 200px;"></div>
          
          <a-divider />
          
          <h4>相关建议</h4>
          <a-timeline>
            <a-timeline-item color="green">保持良好的饮食习惯</a-timeline-item>
            <a-timeline-item color="green">每天至少30分钟有氧运动</a-timeline-item>
            <a-timeline-item color="blue">确保充足睡眠，每晚7-8小时</a-timeline-item>
            <a-timeline-item color="blue">避免久坐，每小时起身活动5分钟</a-timeline-item>
          </a-timeline>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useStore } from 'vuex'
import api from '@/services/api'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { CheckCircleOutlined } from '@ant-design/icons-vue'

// 注册必需的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  LineChart,
  CanvasRenderer
])

const route = useRoute()
const router = useRouter()
const store = useStore()
const healthReportId = route.params.id
const healthReport = ref({})
const loading = ref(true)
const commentsLoading = ref(false)
const trendChartRef = ref(null)
const weightChartRef = ref(null)
let trendChartInstance = null
let weightChartInstance = null

// 用户类型判断
const userType = computed(() => store.state.user?.user_type || '')
const isAdmin = computed(() => userType.value === 'admin')
const isStudent = computed(() => userType.value === 'student')
const userId = computed(() => store.state.user?.id)
const userName = computed(() => store.state.user?.username || '用户')
const userAvatar = computed(() => store.state.user?.avatar || 'https://joeschmoe.io/api/v1/random')

// 评论相关状态
const commentValue = ref('')
const submitting = ref(false)

const fetchHealthReport = async () => {
  loading.value = true
  try {
    console.log('获取健康报告详情，ID:', healthReportId)
    const response = await api.get(`/health-reports/${healthReportId}/`)
    
    // 记录原始响应
    console.log('健康报告API响应:', response.data)
    
    // 创建完整的健康报告对象
    const report = { ...response.data }
    
    // 如果test_result是ID而不是对象，我们需要获取完整的测试结果
    if (report.test_result && typeof report.test_result === 'number') {
      try {
        console.log('正在获取测试结果详情...')
        const testResultResponse = await api.get(`/test-results/${report.test_result}/`)
        report.test_result = testResultResponse.data
        console.log('测试结果详情:', report.test_result)
        
        // 如果学生是ID，需要获取学生详情
        if (report.test_result.student && typeof report.test_result.student === 'number') {
          try {
            const studentResponse = await api.get(`/students/${report.test_result.student}/`)
            report.test_result.student = studentResponse.data
            console.log('学生详情:', report.test_result.student)
          } catch (studentError) {
            console.error('获取学生信息失败:', studentError)
          }
        }
      } catch (testResultError) {
        console.error('获取测试结果详情失败:', testResultError)
      }
    }
    
    // 现在构建必要的字段
    report.student_name = report.test_result?.student?.name || '未知'
    report.student_id = report.test_result?.student?.student_id || '未知'
    report.class_name = report.test_result?.student?.class_name || '未知'
    report.report_id = `HR-${report.id}`
    report.report_date = report.created_at ? new Date(report.created_at).toLocaleDateString() : '未知'
    report.report_type = '体测健康报告'
    report.bmi = report.test_result?.bmi || 0
    report.weight = report.test_result?.weight || 0
    report.height = report.test_result?.height || 0
    report.health_analysis = report.overall_assessment || '暂无健康分析'
    
    // 准备测试指标数据
    if (report.test_result) {
      report.metrics = [
        { name: '肺活量(ml)', value: report.test_result.vital_capacity || 0 },
        { name: '50米跑(秒)', value: report.test_result.run_50m || 0 },
        { name: '坐位体前屈(cm)', value: report.test_result.sit_and_reach || 0 },
        { name: '立定跳远(cm)', value: report.test_result.standing_long_jump || 0 },
        { name: '800米跑(秒)', value: report.test_result.run_800m || 0 }
      ]
    } else {
      report.metrics = []
    }
    
    healthReport.value = report
    console.log('处理后的健康报告详情:', healthReport.value)
  } catch (error) {
    console.error('获取健康报告失败:', error)
    message.error('获取健康报告详情失败，请稍后再试')
    // 使用空对象避免界面报错
    healthReport.value = {
      id: healthReportId,
      report_id: 'HR-' + healthReportId,
      report_date: '未知',
      report_type: '体测健康报告',
      student_name: '未知',
      student_id: '未知',
      class_name: '未知',
      height: 0,
      weight: 0,
      bmi: 0,
      health_analysis: '获取报告失败，请检查网络或联系管理员。',
      health_suggestions: '',
      comments: [],
      history_data: []
    }
  } finally {
    loading.value = false
    nextTick(() => {
      renderTrendChart()
      renderWeightChart()
    })
  }
}

const printReport = () => {
  const printContent = document.querySelector('.health-report-detail').cloneNode(true);
  
  // 移除不需要打印的元素
  const actionsToRemove = printContent.querySelectorAll('.action-buttons, .comment-editor');
  actionsToRemove.forEach(el => el.remove());
  
  // 创建打印样式
  const style = document.createElement('style');
  style.textContent = `
    body {
      font-family: Arial, sans-serif;
      color: #333;
    }
    .health-report-detail {
      padding: 20px;
      max-width: 100%;
    }
    @media print {
      .ant-layout-sider, .site-header, .ant-menu {
        display: none !important;
      }
    }
  `;
  
  // 创建打印窗口
  const printWindow = window.open('', '_blank');
  printWindow.document.body.appendChild(style);
  printWindow.document.body.appendChild(printContent);
  
  // 等待图表和样式加载完成
  setTimeout(() => {
    printWindow.print();
    printWindow.close();
  }, 500);
}

const getBMIColor = (bmi) => {
  if (!bmi) return '#666'
  if (bmi < 18.5) return '#faad14' // 偏瘦
  if (bmi <= 24.9) return '#52c41a' // 正常
  if (bmi <= 29.9) return '#faad14' // 过重
  return '#f5222d' // 肥胖
}

const getBMIStatus = (bmi) => {
  if (!bmi) return { text: '未知', color: 'default' }
  if (bmi < 18.5) return { text: '偏瘦', color: 'warning' }
  if (bmi <= 24.9) return { text: '正常', color: 'success' }
  if (bmi <= 29.9) return { text: '过重', color: 'warning' }
  return { text: '肥胖', color: 'error' }
}

const renderTrendChart = () => {
  if (!healthReport.value.history_data || !trendChartRef.value) return
  
  if (trendChartInstance) {
    trendChartInstance.dispose()
  }
  
  trendChartInstance = echarts.init(trendChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: healthReport.value.history_data.map(item => item.date)
    },
    yAxis: {
      type: 'value',
      name: 'BMI'
    },
    series: [
      {
        name: 'BMI指数',
        type: 'line',
        data: healthReport.value.history_data.map(item => item.bmi),
        markLine: {
          data: [
            { yAxis: 18.5, name: '偏瘦', lineStyle: { color: '#faad14' } },
            { yAxis: 24.9, name: '正常上限', lineStyle: { color: '#52c41a' } }
          ]
        },
        itemStyle: {
          color: '#1890ff'
        }
      }
    ]
  }
  
  trendChartInstance.setOption(option)
}

const renderWeightChart = () => {
  if (!healthReport.value.history_data || !weightChartRef.value) return
  
  if (weightChartInstance) {
    weightChartInstance.dispose()
  }
  
  weightChartInstance = echarts.init(weightChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: healthReport.value.history_data.map(item => item.date)
    },
    yAxis: {
      type: 'value',
      name: '体重(kg)'
    },
    series: [
      {
        name: '体重',
        type: 'line',
        data: healthReport.value.history_data.map(item => item.weight),
        itemStyle: {
          color: '#13c2c2'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(19, 194, 194, 0.4)'
              },
              {
                offset: 1,
                color: 'rgba(19, 194, 194, 0.1)'
              }
            ]
          }
        }
      }
    ]
  }
  
  weightChartInstance.setOption(option)
}

const handleSubmitComment = async () => {
  if (!commentValue.value.trim()) {
    message.warning('评论内容不能为空')
    return
  }
  
  submitting.value = true
  
  try {
    // 检查用户权限
    if (!isStudent.value) {
      message.error('只有学生可以添加评论')
      return
    }

    // 使用真实的API调用发送评论
    const response = await axios.post(`/api/health-reports/${healthReportId}/comments/`, {
      content: commentValue.value
    })
    
    const newComment = response.data
    
    // 更新评论列表
    if (!healthReport.value.comments) {
      healthReport.value.comments = []
    }
    
    healthReport.value.comments.push(newComment)
    commentValue.value = ''
    message.success('评论已添加')
    
  } catch (error) {
    console.error('添加评论失败:', error)
    message.error('添加评论失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchHealthReport()
  window.addEventListener('resize', () => {
    trendChartInstance?.resize()
    weightChartInstance?.resize()
  })
})
</script>

<style scoped>
.health-report-detail {
  padding: 0 24px;
  max-width: 100%;
  overflow-x: hidden;
  height: 100%;
}

.report-card,
.trends-card {
  margin-bottom: 20px;
}

.health-metrics {
  padding: 16px 0;
}

.analysis-content,
.suggestions-content {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  margin-top: 8px;
}

.comments-section {
  margin-top: 24px;
}

.comment-list {
  max-height: 300px;
  overflow-y: auto;
}

.comment-editor {
  margin-top: 16px;
}

/* 确保整体布局可滚动 */
.trends-card, .report-card {
  margin-bottom: 20px;
  overflow: visible;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .health-report-detail {
    padding: 0 16px;
  }
  
  .report-card,
  .trends-card {
    margin-bottom: 16px;
  }
}
</style>
