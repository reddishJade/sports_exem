&lt;template>
  &lt;div class="test-results">
    &lt;a-card title="体测成绩查询" :bordered="false" class="results-card">
      &lt;template #title>
        &lt;div class="card-title">
          &lt;file-text-outlined />
          &lt;span>体测成绩查询&lt;/span>
        &lt;/div>
      &lt;/template>
      
      &lt;a-tabs v-model:activeKey="activeTab" class="results-tabs">
        &lt;a-tab-pane key="list" tab="成绩列表">
          &lt;div class="table-wrapper">
            &lt;a-table 
              :columns="columns" 
              :data-source="testResults" 
              :loading="loading"
              :pagination="{ pageSize: 10, showSizeChanger: true, pageSizeOptions: ['5', '10', '20', '50'] }"
              :row-class-name="getRowClassName"
              class="results-table"
            >
              &lt;template #bodyCell="{ column, record }">
                &lt;template v-if="column.key === 'action'">
                  &lt;a-space>
                    &lt;a @click="showDetail(record)" class="action-link view-link">
                      &lt;eye-outlined /> 查看详情
                    &lt;/a>
                    &lt;a 
                      v-if="!record.is_makeup && !record.is_passed" 
                      class="action-link makeup-link"
                    >
                      &lt;warning-outlined /> 需要补考
                    &lt;/a>
                  &lt;/a-space>
                &lt;/template>
                &lt;template v-else-if="column.key === 'total_score'">
                  &lt;a-tag :color="getScoreColor(record.total_score)" class="score-tag">
                    {{ record.total_score }}
                    &lt;span class="score-text">{{ getScoreText(record.total_score) }}&lt;/span>
                  &lt;/a-tag>
                &lt;/template>
                &lt;template v-else-if="column.key === 'is_makeup'">
                  &lt;a-tag :color="record.is_makeup ? 'orange' : 'green'" class="tag-cell">
                    {{ record.is_makeup ? '是' : '否' }}
                  &lt;/a-tag>
                &lt;/template>
              &lt;/template>
            &lt;/a-table>
          &lt;/div>
        &lt;/a-tab-pane>
        
        &lt;a-tab-pane key="chart" tab="成绩趋势">
          &lt;div class="chart-container">
            &lt;div ref="chartRef" class="chart-content">&lt;/div>
          &lt;/div>
        &lt;/a-tab-pane>
      &lt;/a-tabs>
    &lt;/a-card>

    &lt;a-modal
      v-model:open="detailVisible"
      title="成绩详情"
      width="800px"
      @ok="detailVisible = false"
      class="detail-modal"
    >
      &lt;template #title>
        &lt;div class="modal-title">
          &lt;trophy-outlined />
          &lt;span>成绩详情&lt;/span>
        &lt;/div>
      &lt;/template>
      
      &lt;div class="detail-content" v-if="currentResult">
        &lt;div class="detail-header">
          &lt;div class="test-plan-info">
            &lt;h3>{{ currentResult.test_plan.title }}&lt;/h3>
            &lt;p>{{ formatDate(currentResult.test_date) }}&lt;/p>
          &lt;/div>
          &lt;div class="score-badge" :class="getScoreBadgeClass(currentResult.total_score)">
            {{ currentResult.total_score }}
            &lt;span class="badge-label">{{ getScoreText(currentResult.total_score) }}&lt;/span>
          &lt;/div>
        &lt;/div>
        
        &lt;a-divider />
        
        &lt;a-row :gutter="[16, 16]">
          &lt;a-col :xs="24" :sm="12">
            &lt;div class="stat-card">
              &lt;div class="stat-icon bmi-icon">
                &lt;user-outlined />
              &lt;/div>
              &lt;div class="stat-info">
                &lt;div class="stat-label">BMI指数&lt;/div>
                &lt;div class="stat-value">{{ currentResult.bmi }}&lt;/div>
              &lt;/div>
            &lt;/div>
          &lt;/a-col>
          &lt;a-col :xs="24" :sm="12">
            &lt;div class="stat-card">
              &lt;div class="stat-icon vital-capacity-icon">
                &lt;dashboard-outlined />
              &lt;/div>
              &lt;div class="stat-info">
                &lt;div class="stat-label">肺活量&lt;/div>
                &lt;div class="stat-value">{{ currentResult.vital_capacity }} &lt;span class="unit">ml&lt;/span>&lt;/div>
              &lt;/div>
            &lt;/div>
          &lt;/a-col>
          &lt;a-col :xs="24" :sm="12">
            &lt;div class="stat-card">
              &lt;div class="stat-icon run-icon">
                &lt;thunderbolt-outlined />
              &lt;/div>
              &lt;div class="stat-info">
                &lt;div class="stat-label">50米跑&lt;/div>
                &lt;div class="stat-value">{{ currentResult.run_50m }} &lt;span class="unit">秒&lt;/span>&lt;/div>
              &lt;/div>
            &lt;/div>
          &lt;/a-col>
          &lt;a-col :xs="24" :sm="12">
            &lt;div class="stat-card">
              &lt;div class="stat-icon flexibility-icon">
                &lt;node-expand-outlined />
              &lt;/div>
              &lt;div class="stat-info">
                &lt;div class="stat-label">坐位体前屈&lt;/div>
                &lt;div class="stat-value">{{ currentResult.sit_and_reach }} &lt;span class="unit">cm&lt;/span>&lt;/div>
              &lt;/div>
            &lt;/div>
          &lt;/a-col>
          &lt;a-col :xs="24" :sm="12">
            &lt;div class="stat-card">
              &lt;div class="stat-icon jump-icon">
                &lt;arrow-up-outlined />
              &lt;/div>
              &lt;div class="stat-info">
                &lt;div class="stat-label">立定跳远&lt;/div>
                &lt;div class="stat-value">{{ currentResult.standing_jump }} &lt;span class="unit">cm&lt;/span>&lt;/div>
              &lt;/div>
            &lt;/div>
          &lt;/a-col>
          &lt;a-col :xs="24" :sm="12">
            &lt;div class="stat-card">
              &lt;div class="stat-icon endurance-icon">
                &lt;field-time-outlined />
              &lt;/div>
              &lt;div class="stat-info">
                &lt;div class="stat-label">800米跑&lt;/div>
                &lt;div class="stat-value">{{ currentResult.run_800m }} &lt;span class="unit">秒&lt;/span>&lt;/div>
              &lt;/div>
            &lt;/div>
          &lt;/a-col>
        &lt;/a-row>

        &lt;template v-if="currentResult?.health_report">
          &lt;a-divider>
            &lt;span class="divider-content">
              &lt;heart-outlined /> 健康报告
            &lt;/span>
          &lt;/a-divider>
          
          &lt;div class="health-report">
            &lt;div class="report-item">
              &lt;h4>总体评估&lt;/h4>
              &lt;p>{{ currentResult.health_report.overall_assessment }}&lt;/p>
            &lt;/div>
            &lt;div class="report-item">
              &lt;h4>健康建议&lt;/h4>
              &lt;p>{{ currentResult.health_report.health_suggestions }}&lt;/p>
            &lt;/div>
          &lt;/div>
        &lt;/template>
        
        &lt;a-divider v-else />
        
        &lt;div class="detail-footer" v-if="!currentResult?.health_report">
          &lt;a-alert type="info" show-icon>
            &lt;template #message>
              该测试成绩暂无健康报告
            &lt;/template>
            &lt;template #description>
              健康报告将在教师评估后生成
            &lt;/template>
          &lt;/a-alert>
        &lt;/div>
      &lt;/div>
    &lt;/a-modal>
  &lt;/div>
&lt;/template>

&lt;script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { formatDate } from '@/utils/format'
import { 
  FileTextOutlined, 
  EyeOutlined, 
  WarningOutlined, 
  TrophyOutlined,
  UserOutlined,
  DashboardOutlined,
  ThunderboltOutlined,
  NodeExpandOutlined,
  ArrowUpOutlined,
  FieldTimeOutlined,
  HeartOutlined
} from '@ant-design/icons-vue'

const activeTab = ref('list')
const loading = ref(false)
const testResults = ref([])
const detailVisible = ref(false)
const currentResult = ref(null)
const chartRef = ref(null)
let chart = null

const columns = [
  {
    title: '测试计划',
    dataIndex: ['test_plan', 'title'],
    key: 'test_plan',
  },
  {
    title: '测试时间',
    dataIndex: 'test_date',
    key: 'test_date',
    customRender: ({ text }) => formatDate(text),
    sorter: (a, b) => new Date(a.test_date) - new Date(b.test_date),
  },
  {
    title: '总分',
    dataIndex: 'total_score',
    key: 'total_score',
    sorter: (a, b) => a.total_score - b.total_score,
  },
  {
    title: '是否补考',
    dataIndex: 'is_makeup',
    key: 'is_makeup',
    filters: [
      { text: '是', value: true },
      { text: '否', value: false },
    ],
    onFilter: (value, record) => record.is_makeup === value,
  },
  {
    title: '操作',
    key: 'action',
  },
]

const getRowClassName = (record) => {
  if (!record.is_passed) {
    return 'failed-row'
  }
  return ''
}

const getScoreColor = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'processing'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'warning'
  return 'error'
}

const getScoreText = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

const getScoreBadgeClass = (score) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

const fetchTestResults = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/test-results/')
    testResults.value = response.data
  } catch (error) {
    message.error('获取成绩数据失败')
  } finally {
    loading.value = false
  }
}

const showDetail = (record) => {
  currentResult.value = record
  detailVisible.value = true
}

const initChart = () => {
  if (!chartRef.value) return
  
  if (chart) {
    chart.dispose()
  }
  
  chart = echarts.init(chartRef.value)
  const dates = testResults.value.map(result => formatDate(result.test_date))
  const scores = testResults.value.map(result => result.total_score)
  
  // 添加其他指标数据
  const bmiData = testResults.value.map(result => result.bmi || 0)
  const vitalCapacityData = testResults.value.map(result => parseFloat(result.vital_capacity) / 100 || 0)
  const run50mData = testResults.value.map(result => 100 - parseFloat(result.run_50m) * 5 || 0)
  
  const option = {
    title: {
      text: '体测成绩趋势分析',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#ccc',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      formatter: function(params) {
        let result = `<div style="font-weight:bold;margin-bottom:5px;">${params[0].axisValue}</div>`
        params.forEach(param => {
          const colorSpan = `<span style="display:inline-block;margin-right:5px;border-radius:50%;width:10px;height:10px;background-color:${param.color};"></span>`
          let value = param.value
          let unit = ''
          
          if (param.seriesName === 'BMI') {
            unit = ' BMI'
          } else if (param.seriesName === '肺活量') {
            value = value * 100
            unit = ' ml'
          } else if (param.seriesName === '50米跑') {
            value = (100 - value) / 5
            unit = ' 秒'
          } else if (param.seriesName === '总分') {
            unit = ' 分'
          }
          
          result += `<div>${colorSpan}${param.seriesName}: ${value}${unit}</div>`
        })
        return result
      }
    },
    legend: {
      data: ['总分', 'BMI', '肺活量', '50米跑'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: 60,
      top: 60,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: {
        lineStyle: {
          color: '#ccc'
        }
      },
      axisLabel: {
        rotate: 30,
        margin: 15
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: [
      {
        name: '总分',
        type: 'line',
        data: scores,
        symbolSize: 8,
        lineStyle: {
          width: 4,
          shadowColor: 'rgba(0,0,0,0.2)',
          shadowBlur: 10
        },
        markLine: {
          data: [
            {
              name: '及格线',
              yAxis: 60,
              lineStyle: {
                color: '#ff4d4f',
                type: 'dashed',
                width: 2
              },
              label: {
                formatter: '及格线',
                position: 'start'
              }
            }
          ]
        }
      },
      {
        name: 'BMI',
        type: 'line',
        data: bmiData,
        symbolSize: 6
      },
      {
        name: '肺活量',
        type: 'line',
        data: vitalCapacityData,
        symbolSize: 6
      },
      {
        name: '50米跑',
        type: 'line',
        data: run50mData,
        symbolSize: 6
      }
    ],
    color: ['#1890ff', '#52c41a', '#faad14', '#ff4d4f']
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  chart?.resize()
}

watch(activeTab, (newVal) => {
  if (newVal === 'chart' && testResults.value.length > 0) {
    setTimeout(initChart, 0)
  }
})

watch(testResults, () => {
  if (activeTab.value === 'chart' && testResults.value.length > 0) {
    setTimeout(initChart, 0)
  }
})

onMounted(() => {
  fetchTestResults()
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    window.removeEventListener('resize', handleResize)
  }
})
&lt;/script>

&lt;style scoped>
.test-results {
  width: 100%;
}

.results-card {
  border-radius: 8px;
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16),
              0 3px 6px 0 rgba(0, 0, 0, 0.12),
              0 5px 12px 4px rgba(0, 0, 0, 0.09);
  margin-bottom: 24px;
}

.card-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.card-title :deep(svg) {
  margin-right: 8px;
  font-size: 18px;
  color: var(--primary-color);
}

.results-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 24px;
}

.table-wrapper {
  margin-bottom: 24px;
}

.results-table {
  border-radius: 4px;
  overflow: hidden;
}

.results-table :deep(.ant-table-tbody > tr.failed-row) {
  background-color: rgba(255, 77, 79, 0.06);
}

.results-table :deep(.ant-table-tbody > tr.failed-row:hover > td) {
  background-color: rgba(255, 77, 79, 0.1) !important;
}

.score-tag {
  min-width: 80px;
  text-align: center;
  padding: 4px 8px;
  border-radius: 4px;
}

.score-text {
  margin-left: 4px;
  opacity: 0.8;
  font-size: 12px;
}

.tag-cell {
  min-width: 50px;
  text-align: center;
}

.action-link {
  display: inline-flex;
  align-items: center;
  margin-right: 12px;
  transition: all 0.3s;
}

.action-link :deep(svg) {
  margin-right: 4px;
}

.view-link {
  color: var(--primary-color);
}

.view-link:hover {
  color: var(--dark-primary-color);
}

.makeup-link {
  color: #ff4d4f;
}

.makeup-link:hover {
  color: #ff7875;
}

.chart-container {
  width: 100%;
  margin-top: 16px;
  padding: 16px;
  background-color: #fff;
  border-radius: 4px;
}

.chart-content {
  width: 100%;
  height: 500px;
}

/* 详情模态框样式 */
.detail-modal :deep(.ant-modal-content) {
  border-radius: 8px;
  overflow: hidden;
}

.modal-title {
  display: flex;
  align-items: center;
  font-weight: 600;
}

.modal-title :deep(svg) {
  margin-right: 8px;
  font-size: 18px;
  color: var(--primary-color);
}

.detail-content {
  padding: 0 16px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.test-plan-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
}

.test-plan-info p {
  margin: 0;
  color: var(--text-secondary);
}

.score-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 24px;
  font-weight: 700;
  color: white;
  min-width: 80px;
}

.badge-label {
  font-size: 14px;
  font-weight: 400;
  margin-top: 4px;
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

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  border-radius: 8px;
  background-color: #f9f9f9;
  transition: all 0.3s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  margin-right: 16px;
  color: white;
  font-size: 24px;
}

.bmi-icon {
  background-color: #1890ff;
}

.vital-capacity-icon {
  background-color: #52c41a;
}

.run-icon {
  background-color: #faad14;
}

.flexibility-icon {
  background-color: #13c2c2;
}

.jump-icon {
  background-color: #722ed1;
}

.endurance-icon {
  background-color: #eb2f96;
}

.stat-info {
  flex: 1;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
}

.unit {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 400;
}

.divider-content {
  display: flex;
  align-items: center;
  color: var(--text-secondary);
}

.divider-content :deep(svg) {
  margin-right: 8px;
  color: #f5222d;
}

.health-report {
  margin-top: 16px;
}

.report-item {
  margin-bottom: 16px;
}

.report-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.report-item p {
  margin: 0;
  line-height: 1.6;
  color: var(--text-secondary);
}

.detail-footer {
  margin-top: 24px;
}

@media (max-width: 768px) {
  .score-badge {
    padding: 8px 12px;
    font-size: 20px;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .score-badge {
    margin-top: 16px;
    align-self: flex-start;
  }
}
&lt;/style>
