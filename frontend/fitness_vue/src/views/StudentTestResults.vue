<!--
  @description 学生视角的测试结果展示组件
  @author Cascade AI
  @date 2025-03-27
  @version 1.0.0
  @roles 学生 - 查看和分析自己的测试成绩
-->
<template>
  <div class="test-results">
    <a-card title="体测成绩查询" :bordered="false" class="results-card">
      <template #title>
        <div class="card-title">
          <file-text-outlined />
          <span>体测成绩查询</span>
        </div>
      </template>
      
      <a-tabs v-model:activeKey="activeTab" class="results-tabs">
        <a-tab-pane key="list" tab="成绩列表">
          <div class="table-wrapper">
            <a-table 
              :columns="columns" 
              :data-source="testResults" 
              :loading="loading"
              :pagination="{ pageSize: 10, showSizeChanger: true, pageSizeOptions: ['5', '10', '20', '50'] }"
              :row-class-name="getRowClassName"
              class="results-table"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'action'">
                  <a-space>
                    <a @click="showDetail(record)" class="action-link view-link">
                      <eye-outlined /> 查看详情
                    </a>
                    <a 
                      v-if="!record.is_makeup && !record.is_passed" 
                      class="action-link makeup-link"
                    >
                      <warning-outlined /> 需要补考
                    </a>
                  </a-space>
                </template>
                <template v-else-if="column.key === 'total_score'">
                  <a-tag :color="getScoreColor(record.total_score)" class="score-tag">
                    {{ record.total_score }}
                    <span class="score-text">{{ getScoreText(record.total_score) }}</span>
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'is_makeup'">
                  <a-tag :color="record.is_makeup ? 'orange' : 'green'" class="tag-cell">
                    {{ record.is_makeup ? '是' : '否' }}
                  </a-tag>
                </template>
              </template>
            </a-table>
          </div>
        </a-tab-pane>
        
        <a-tab-pane key="chart" tab="成绩趋势">
          <div class="chart-container">
            <div ref="chartRef" class="chart-content"></div>
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <a-modal
      v-model:open="detailVisible"
      title="成绩详情"
      width="800px"
      @ok="detailVisible = false"
      class="detail-modal"
    >
      <template #title>
        <div class="modal-title">
          <trophy-outlined />
          <span>成绩详情</span>
        </div>
      </template>
      
      <div class="detail-content" v-if="currentResult">
        <div class="detail-header">
          <div class="test-plan-info">
            <h3>{{ currentResult.test_plan.title }}</h3>
            <p>{{ formatDate(currentResult.test_date) }}</p>
          </div>
          <div class="score-badge" :class="getScoreBadgeClass(currentResult.total_score)">
            {{ currentResult.total_score }}
            <span class="badge-label">{{ getScoreText(currentResult.total_score) }}</span>
          </div>
        </div>
        
        <a-divider />
        
        <a-row :gutter="[16, 16]">
          <a-col :xs="24" :sm="12">
            <div class="stat-card">
              <div class="stat-icon bmi-icon">
                <user-outlined />
              </div>
              <div class="stat-info">
                <div class="stat-label">BMI指数</div>
                <div class="stat-value">{{ currentResult.bmi }}</div>
              </div>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12">
            <div class="stat-card">
              <div class="stat-icon vital-capacity-icon">
                <dashboard-outlined />
              </div>
              <div class="stat-info">
                <div class="stat-label">肺活量</div>
                <div class="stat-value">{{ currentResult.vital_capacity }} <span class="unit">ml</span></div>
              </div>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12">
            <div class="stat-card">
              <div class="stat-icon run-icon">
                <thunderbolt-outlined />
              </div>
              <div class="stat-info">
                <div class="stat-label">50米跑</div>
                <div class="stat-value">{{ currentResult.run_50m }} <span class="unit">秒</span></div>
              </div>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12">
            <div class="stat-card">
              <div class="stat-icon flexibility-icon">
                <node-expand-outlined />
              </div>
              <div class="stat-info">
                <div class="stat-label">坐位体前屈</div>
                <div class="stat-value">{{ currentResult.sit_and_reach }} <span class="unit">cm</span></div>
              </div>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12">
            <div class="stat-card">
              <div class="stat-icon jump-icon">
                <arrow-up-outlined />
              </div>
              <div class="stat-info">
                <div class="stat-label">立定跳远</div>
                <div class="stat-value">{{ currentResult.standing_jump }} <span class="unit">cm</span></div>
              </div>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12">
            <div class="stat-card">
              <div class="stat-icon endurance-icon">
                <field-time-outlined />
              </div>
              <div class="stat-info">
                <div class="stat-label">800米跑</div>
                <div class="stat-value">{{ currentResult.run_800m }} <span class="unit">秒</span></div>
              </div>
            </div>
          </a-col>
        </a-row>
        
        <a-divider />
        
        <div class="comments-section">
          <h3 class="section-title">我的评论</h3>
          <div class="add-comment">
            <a-textarea 
              v-model:value="newComment" 
              placeholder="添加评论..."
              :rows="3"
              class="comment-textarea"
            />
            <a-button 
              type="primary" 
              @click="submitComment" 
              :loading="commentLoading"
              class="submit-btn"
            >
              发表评论
            </a-button>
          </div>
          
          <a-list
            class="comment-list"
            :loading="commentsLoading"
            :data-source="comments"
            :locale="{ emptyText: comments.length ? '' : '暂无评论' }"
          >
            <template #renderItem="{ item }">
              <a-list-item class="comment-item">
                <a-comment
                  :author="item.student && item.student.name ? item.student.name : '未知用户'"
                  :content="item.content || ''"
                  :datetime="formatCommentDate(item.created_at || new Date().toISOString())"
                >
                  <template #avatar>
                    <a-avatar>{{ item.student && item.student.name ? item.student.name[0] : 'U' }}</a-avatar>
                  </template>
                  <template #actions>
                    <a-tag :color="item.is_approved ? 'green' : 'orange'">
                      {{ item.is_approved ? '已审核' : '待审核' }}
                    </a-tag>
                  </template>
                </a-comment>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { 
  GridComponent, 
  TooltipComponent, 
  TitleComponent, 
  LegendComponent 
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
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
  FieldTimeOutlined
} from '@ant-design/icons-vue'
import { useStore } from 'vuex'

// 注册必要的组件
echarts.use([
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  CanvasRenderer
])

// 数据和状态
const store = useStore() // 将store定义到顶层作用域
const activeTab = ref('list')
const loading = ref(false)
const testResults = ref([])
const detailVisible = ref(false)
const currentResult = ref(null)
const chartRef = ref(null)
let chart = null
const commentsLoading = ref(false)
const comments = ref([])
const newComment = ref('')
const commentLoading = ref(false)

// 表格列定义
const columns = [
  {
    title: '测试计划',
    dataIndex: ['test_plan', 'title'],
    key: 'test_plan',
    width: '25%'
  },
  {
    title: '测试日期',
    dataIndex: 'test_date',
    key: 'test_date',
    width: '20%',
    customRender: ({ text }) => formatDate(text)
  },
  {
    title: '总分',
    dataIndex: 'total_score',
    key: 'total_score',
    width: '15%',
    sorter: (a, b) => a.total_score - b.total_score
  },
  {
    title: '是否补考',
    dataIndex: 'is_makeup',
    key: 'is_makeup',
    width: '15%',
    filters: [
      { text: '是', value: true },
      { text: '否', value: false }
    ],
    onFilter: (value, record) => record.is_makeup === value
  },
  {
    title: '操作',
    key: 'action',
    width: '25%'
  }
]

// 获取测试结果
const fetchTestResults = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/test-results/')
    testResults.value = response.data
    loading.value = false
    
    // 如果在图表标签，初始化图表
    if (activeTab.value === 'chart') {
      initChart()
    }
  } catch (error) {
    console.error('获取测试结果失败:', error)
    message.error('获取测试结果失败')
    loading.value = false
  }
}

// 显示详情
const showDetail = (record) => {
  currentResult.value = record
  detailVisible.value = true
  fetchComments(record.id)
}

// 获取评论
const fetchComments = async (resultId) => {
  commentsLoading.value = true
  try {
    const token = store.state.token
    const response = await axios.get(`/api/comments/?test_result=${resultId}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    // 确保每个评论对象都有必要的属性，防止渲染错误
    comments.value = response.data.map(comment => ({
      ...comment,
      student: comment.student || { name: '未知用户' },
      content: comment.content || '',
      created_at: comment.created_at || new Date().toISOString(),
      is_approved: !!comment.is_approved
    }))
    commentsLoading.value = false
  } catch (error) {
    console.error('获取评论失败:', error)
    message.error('获取评论失败')
    comments.value = []
    commentsLoading.value = false
  }
}

// 提交评论
const submitComment = async () => {
  if (!newComment.value.trim()) {
    message.warning('评论内容不能为空')
    return
  }
  
  // 验证用户权限
  if (!store.state.user) {
    message.error('请先登录')
    return
  }
  
  if (store.state.user.user_type !== 'student') {
    message.error('只有学生可以发表评论')
    return
  }
  
  // 验证学生档案
  if (!store.state.user.student_profile) {
    message.error('未找到学生资料，请先完善个人资料，创建学生档案才能发表评论')
    return
  }
  
  commentLoading.value = true
  try {
    const token = store.state.token
    await axios.post(`/api/comments/`, {
      content: newComment.value.trim(),
      test_result: currentResult.value.id
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    message.success('评论提交成功，等待审核')
    newComment.value = ''
    fetchComments(currentResult.value.id)
    commentLoading.value = false
  } catch (error) {
    console.error('提交评论失败:', error)
    message.error('提交评论失败')
    commentLoading.value = false
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  if (chart) {
    chart.dispose()
    chart = null
  }
  
  const chartInstance = echarts.init(chartRef.value)
  chart = chartInstance
  
  // 准备图表数据
  const dates = []
  const scores = []
  
  // 按日期排序的结果
  const sortedResults = [...testResults.value].sort((a, b) => {
    return new Date(a.test_date) - new Date(b.test_date)
  })
  
  sortedResults.forEach(result => {
    dates.push(formatDate(result.test_date))
    scores.push(result.total_score)
  })
  
  const option = {
    title: {
      text: '体测成绩趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br />总分: {c}'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      interval: 10
    },
    series: [
      {
        name: '总分',
        type: 'line',
        data: scores,
        markLine: {
          data: [
            {
              name: '及格线',
              yAxis: 60,
              lineStyle: {
                color: '#ff4d4f'
              },
              label: {
                formatter: '及格线 (60分)',
                position: 'start'
              }
            }
          ]
        },
        itemStyle: {
          color: '#1890ff'
        },
        lineStyle: {
          width: 3
        },
        symbolSize: 8,
        emphasis: {
          itemStyle: {
            color: '#ff7875',
            borderWidth: 2,
            borderColor: '#ff7875'
          }
        }
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    }
  }
  
  chartInstance.setOption(option)
}

// 创建一个resize事件处理函数，以便可以在卸载时移除
const handleResize = () => {
  if (chart) {
    chart.resize()
  }
}

// 添加resize事件监听
const addResizeListener = () => {
  window.addEventListener('resize', handleResize)
}

// 移除resize事件监听
const removeResizeListener = () => {
  window.removeEventListener('resize', handleResize)
}

// 处理标签切换
watch(activeTab, (newValue) => {
  if (newValue === 'chart' && testResults.value.length > 0) {
    // 使用setTimeout确保DOM已更新
    setTimeout(() => {
      initChart()
      addResizeListener()
    }, 0)
  }
})

// 组件卸载时清理图表实例和事件监听器
onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
  removeResizeListener()
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 格式化评论日期
const formatCommentDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 获取行样式
const getRowClassName = (record) => {
  return record.total_score < 60 ? 'failed-row' : ''
}

// 获取分数颜色
const getScoreColor = (score) => {
  if (score >= 90) return 'green'
  if (score >= 80) return 'cyan'
  if (score >= 70) return 'blue'
  if (score >= 60) return 'orange'
  return 'red'
}

// 获取分数文本
const getScoreText = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

// 获取分数徽章样式类
const getScoreBadgeClass = (score) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

// 组件挂载时获取数据
onMounted(() => {
  fetchTestResults()
})
</script>

<style scoped>
.test-results {
  padding: 20px;
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
  font-size: 18px;
  font-weight: 500;
}

.card-title span {
  margin-left: 8px;
}

.results-tabs {
  margin-top: -16px;
}

.table-wrapper {
  margin-top: 16px;
  padding: 8px;
  background-color: #fff;
  border-radius: 8px;
}

.results-table {
  overflow: hidden;
}

.results-table :deep(.ant-table-thead > tr > th) {
  background-color: #f5f5f5;
  color: rgba(0, 0, 0, 0.85);
  font-weight: 500;
  text-align: center;
}

.results-table :deep(.ant-table-tbody > tr > td) {
  text-align: center;
}

.results-table :deep(.ant-table-tbody > tr.failed-row > td) {
  background-color: rgba(255, 77, 79, 0.05);
}

.results-table :deep(.ant-table-tbody > tr.failed-row:hover > td) {
  background-color: rgba(255, 77, 79, 0.1) !important;
}

.score-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 70px;
}

.score-text {
  font-size: 12px;
  margin-left: 4px;
  opacity: 0.8;
}

.action-link {
  display: inline-flex;
  align-items: center;
  transition: all 0.3s;
}

.action-link:hover {
  color: #1890ff;
  transform: scale(1.05);
}

.makeup-link {
  color: #ff4d4f;
}

.makeup-link:hover {
  color: #ff7875;
}

.tag-cell {
  min-width: 40px;
  text-align: center;
}

.chart-container {
  margin-top: 16px;
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.chart-content {
  height: 400px;
  width: 100%;
}

/* 详情模态框 */
.modal-title {
  display: flex;
  align-items: center;
  font-size: 16px;
}

.modal-title span {
  margin-left: 8px;
}

.detail-content {
  padding: 16px 8px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.test-plan-info h3 {
  margin-bottom: 4px;
  font-size: 18px;
  font-weight: 500;
}

.test-plan-info p {
  color: rgba(0, 0, 0, 0.45);
  margin: 0;
}

.score-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  font-size: 24px;
  font-weight: bold;
  color: white;
  position: relative;
}

.badge-label {
  font-size: 12px;
  font-weight: normal;
  margin-top: 4px;
}

.score-excellent {
  background: linear-gradient(135deg, #52c41a, #389e0d);
  box-shadow: 0 4px 10px rgba(82, 196, 26, 0.4);
}

.score-good {
  background: linear-gradient(135deg, #13c2c2, #08979c);
  box-shadow: 0 4px 10px rgba(19, 194, 194, 0.4);
}

.score-average {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  box-shadow: 0 4px 10px rgba(24, 144, 255, 0.4);
}

.score-pass {
  background: linear-gradient(135deg, #faad14, #d48806);
  box-shadow: 0 4px 10px rgba(250, 173, 20, 0.4);
}

.score-fail {
  background: linear-gradient(135deg, #ff4d4f, #cf1322);
  box-shadow: 0 4px 10px rgba(255, 77, 79, 0.4);
}

.stat-card {
  display: flex;
  align-items: center;
  background-color: #fafafa;
  padding: 16px;
  border-radius: 8px;
  height: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  margin-right: 16px;
}

.bmi-icon {
  background: linear-gradient(135deg, #ff9800, #ff5722);
}

.vital-capacity-icon {
  background: linear-gradient(135deg, #2196f3, #03a9f4);
}

.run-icon {
  background: linear-gradient(135deg, #f44336, #e91e63);
}

.flexibility-icon {
  background: linear-gradient(135deg, #9c27b0, #673ab7);
}

.jump-icon {
  background: linear-gradient(135deg, #4caf50, #8bc34a);
}

.endurance-icon {
  background: linear-gradient(135deg, #795548, #a1887f);
}

.stat-info {
  flex: 1;
}

.stat-label {
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 500;
}

.unit {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  margin-left: 4px;
}

/* 评论部分 */
.comments-section {
  margin-top: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
  color: rgba(0, 0, 0, 0.85);
}

.add-comment {
  margin-bottom: 20px;
}

.comment-textarea {
  margin-bottom: 12px;
  border-radius: 4px;
}

.submit-btn {
  float: right;
}

.comment-list {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.comment-item {
  transition: background-color 0.3s;
  border-radius: 4px;
  padding: 8px;
}

.comment-item:hover {
  background-color: #f0f0f0;
}
</style>
