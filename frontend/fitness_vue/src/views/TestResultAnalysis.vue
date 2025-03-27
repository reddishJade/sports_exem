<template>
  <div class="test-result-analysis">
    <a-card title="成绩分析" :bordered="false">
      <div class="filter-section">
        <a-row :gutter="16">
          <a-col :xs="24" :sm="8" :md="6">
            <a-form-item label="测试计划">
              <a-select
                v-model:value="selectedPlan"
                placeholder="选择测试计划"
                :loading="plansLoading"
                @change="handlePlanChange"
                style="width: 100%"
              >
                <a-select-option value="all">全部计划</a-select-option>
                <a-select-option v-for="plan in testPlans" :key="plan.id" :value="plan.id">
                  {{ plan.title }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="8" :md="6">
            <a-form-item label="班级">
              <a-select
                v-model:value="selectedClass"
                placeholder="选择班级"
                @change="applyFilters"
                style="width: 100%"
              >
                <a-select-option value="all">全部班级</a-select-option>
                <a-select-option v-for="classItem in classOptions" :key="classItem" :value="classItem">
                  {{ classItem }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="8" :md="6">
            <a-form-item label="性别">
              <a-select
                v-model:value="selectedGender"
                placeholder="选择性别"
                @change="applyFilters"
                style="width: 100%"
              >
                <a-select-option value="all">全部</a-select-option>
                <a-select-option value="male">男</a-select-option>
                <a-select-option value="female">女</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="8" :md="6">
            <a-form-item label="项目">
              <a-select
                v-model:value="selectedItem"
                placeholder="选择测试项目"
                @change="updateCharts"
                style="width: 100%"
              >
                <a-select-option value="all">总体成绩</a-select-option>
                <a-select-option value="bmi">BMI</a-select-option>
                <a-select-option value="running_50m">50米跑</a-select-option>
                <a-select-option value="long_jump">立定跳远</a-select-option>
                <a-select-option value="sit_ups">仰卧起坐</a-select-option>
                <a-select-option value="endurance_run">耐力跑</a-select-option>
                <a-select-option value="flexibility">坐位体前屈</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
      </div>

      <a-skeleton active :loading="loading" v-if="loading" />
      
      <div v-else>
        <a-row :gutter="16" class="chart-row">
          <a-col :xs="24" :lg="12">
            <a-card :bordered="false" title="成绩分布">
              <div ref="pieChartRef" style="height: 300px;"></div>
            </a-card>
          </a-col>
          <a-col :xs="24" :lg="12">
            <a-card :bordered="false" title="平均分比较">
              <div ref="avgScoreChartRef" style="height: 300px;"></div>
            </a-card>
          </a-col>
        </a-row>
        
        <a-row :gutter="16" class="chart-row">
          <a-col :span="24">
            <a-card :bordered="false" title="成绩趋势分析">
              <div ref="trendChartRef" style="height: 350px;"></div>
            </a-card>
          </a-col>
        </a-row>
        
        <a-row :gutter="16" class="chart-row">
          <a-col :span="24">
            <a-card :bordered="false" title="成绩分析数据">
              <a-table :columns="columns" :data-source="tableData" :loading="loading" rowKey="id">
                <template #bodyCell="{ column, record }">
                  <template v-if="column.dataIndex === 'score'">
                    <span :class="getScoreClass(record.score)">{{ record.score }}</span>
                  </template>
                  <template v-if="column.dataIndex === 'level'">
                    <a-tag :color="getTagColor(record.level)">{{ record.level }}</a-tag>
                  </template>
                </template>
              </a-table>
            </a-card>
          </a-col>
        </a-row>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent
} from 'echarts/components'
import { LabelLayout, UniversalTransition } from 'echarts/features'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必需的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart
])

const store = useStore()
const token = computed(() => store.state.token)

// 图表容器引用
const pieChartRef = ref(null)
const avgScoreChartRef = ref(null)
const trendChartRef = ref(null)

// 图表实例
let pieChart = null
let avgScoreChart = null
let trendChart = null

// 数据加载状态
const loading = ref(false)
const plansLoading = ref(false)

// 测试计划数据
const testPlans = ref([])
const testResults = ref([])
const classOptions = ref([])

// 筛选条件
const selectedPlan = ref('all')
const selectedClass = ref('all')
const selectedGender = ref('all')
const selectedItem = ref('all')

// 表格列定义
const columns = [
  {
    title: '姓名',
    dataIndex: 'student_name',
    key: 'student_name',
  },
  {
    title: '班级',
    dataIndex: 'class_name',
    key: 'class_name',
  },
  {
    title: '性别',
    dataIndex: 'gender',
    key: 'gender',
    customFilterDropdown: true,
  },
  {
    title: '项目',
    dataIndex: 'item_name',
    key: 'item_name',
  },
  {
    title: '成绩',
    dataIndex: 'score',
    key: 'score',
    sorter: (a, b) => a.score - b.score,
  },
  {
    title: '等级',
    dataIndex: 'level',
    key: 'level',
  },
  {
    title: '测试日期',
    dataIndex: 'test_date',
    key: 'test_date',
    sorter: (a, b) => new Date(a.test_date) - new Date(b.test_date),
  },
]

// 表格数据
const tableData = ref([])

// 过滤后的数据
const filteredResults = computed(() => {
  let results = [...testResults.value]
  
  if (selectedPlan.value !== 'all') {
    results = results.filter(result => result.test_plan.id === selectedPlan.value)
  }
  
  if (selectedClass.value !== 'all') {
    results = results.filter(result => result.student.class_name === selectedClass.value)
  }
  
  if (selectedGender.value !== 'all') {
    results = results.filter(result => result.student.gender === selectedGender.value)
  }
  
  return results
})

// 获取分数等级的CSS类
const getScoreClass = (score) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

// 获取标签颜色
const getTagColor = (level) => {
  const colors = {
    '优秀': 'success',
    '良好': 'processing',
    '中等': 'warning',
    '及格': 'default',
    '不及格': 'error'
  }
  return colors[level] || 'default'
}

// 窗口大小变化处理
const handleResize = () => {
  pieChart?.resize()
  avgScoreChart?.resize()
  trendChart?.resize()
}

// 获取测试计划
const fetchTestPlans = async () => {
  plansLoading.value = true
  try {
    const response = await axios.get('/api/test-plans/', {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    testPlans.value = response.data
  } catch (error) {
    console.error('获取测试计划失败:', error)
  } finally {
    plansLoading.value = false
  }
}

// 获取测试结果
const fetchTestResults = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/test-results/', {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    testResults.value = response.data
    
    // 提取班级选项
    const classes = new Set()
    testResults.value.forEach(result => {
      if (result.student?.class_name) {
        classes.add(result.student.class_name)
      }
    })
    classOptions.value = [...classes]
    
    // 更新表格数据
    updateTableData()
    
    // 初始化图表
    initCharts()
  } catch (error) {
    console.error('获取测试结果失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理计划变更
const handlePlanChange = () => {
  applyFilters()
}

// 应用筛选器
const applyFilters = () => {
  updateTableData()
  updateCharts()
}

// 更新表格数据
const updateTableData = () => {
  tableData.value = filteredResults.value.map(result => {
    // 转换项目数据为表格行
    const common = {
      id: result.id,
      student_name: result.student.user.username,
      class_name: result.student.class_name,
      gender: result.student.gender === 'male' ? '男' : '女',
      test_date: result.test_date,
    }
    
    const getLevel = (score) => {
      if (score >= 90) return '优秀'
      if (score >= 80) return '良好'
      if (score >= 70) return '中等'
      if (score >= 60) return '及格'
      return '不及格'
    }
    
    // 基于选择的项目创建表格行
    if (selectedItem.value === 'all' || selectedItem.value === 'total_score') {
      return {
        ...common,
        item_name: '总分',
        score: result.total_score,
        level: getLevel(result.total_score)
      }
    } else {
      // 返回特定项目
      const itemMap = {
        'bmi': { name: 'BMI', value: result.bmi, score: result.bmi_score },
        'running_50m': { name: '50米跑', value: result.running_50m, score: result.running_score },
        'long_jump': { name: '立定跳远', value: result.long_jump, score: result.jump_score },
        'sit_ups': { name: '仰卧起坐', value: result.sit_ups, score: result.situp_score },
        'endurance_run': { name: '耐力跑', value: result.endurance_run, score: result.endurance_score },
        'flexibility': { name: '坐位体前屈', value: result.flexibility, score: result.flexibility_score }
      }
      
      const item = itemMap[selectedItem.value]
      return {
        ...common,
        item_name: item.name,
        raw_value: item.value,
        score: item.score,
        level: getLevel(item.score)
      }
    }
  })
}

// 初始化图表
const initCharts = () => {
  // 初始化饼图
  pieChart = echarts.init(pieChartRef.value)
  
  // 初始化平均分柱状图
  avgScoreChart = echarts.init(avgScoreChartRef.value)
  
  // 初始化趋势图
  trendChart = echarts.init(trendChartRef.value)
  
  // 更新图表数据
  updateCharts()
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize)
}

// 更新图表
const updateCharts = () => {
  updatePieChart()
  updateAvgScoreChart()
  updateTrendChart()
}

// 更新饼图
const updatePieChart = () => {
  const data = filteredResults.value
  const levelCounts = {
    '优秀': 0,
    '良好': 0,
    '中等': 0,
    '及格': 0,
    '不及格': 0
  }
  
  // 计算各等级数量
  data.forEach(item => {
    let score
    
    if (selectedItem.value === 'all' || selectedItem.value === 'total_score') {
      score = item.total_score
    } else {
      const scoreMap = {
        'bmi': item.bmi_score,
        'running_50m': item.running_score,
        'long_jump': item.jump_score,
        'sit_ups': item.situp_score,
        'endurance_run': item.endurance_score,
        'flexibility': item.flexibility_score
      }
      score = scoreMap[selectedItem.value]
    }
    
    if (score >= 90) levelCounts['优秀']++
    else if (score >= 80) levelCounts['良好']++
    else if (score >= 70) levelCounts['中等']++
    else if (score >= 60) levelCounts['及格']++
    else levelCounts['不及格']++
  })
  
  // 准备饼图数据
  const pieData = Object.entries(levelCounts).map(([name, value]) => ({ name, value }))
  
  // 饼图配置
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: Object.keys(levelCounts)
    },
    series: [
      {
        name: '成绩分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 40,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: pieData,
        color: ['#52c41a', '#1890ff', '#faad14', '#d9d9d9', '#f5222d']
      }
    ]
  }
  
  pieChart.setOption(option)
}

// 更新平均分柱状图
const updateAvgScoreChart = () => {
  // 按班级分组数据
  const classByClass = {}
  
  filteredResults.value.forEach(item => {
    const className = item.student.class_name || '未知班级'
    if (!classByClass[className]) {
      classByClass[className] = []
    }
    classByClass[className].push(item)
  })
  
  // 计算每个班级的平均分
  const classNames = []
  const avgScores = []
  
  for (const [className, items] of Object.entries(classByClass)) {
    classNames.push(className)
    
    let totalScore = 0
    items.forEach(item => {
      if (selectedItem.value === 'all' || selectedItem.value === 'total_score') {
        totalScore += item.total_score
      } else {
        const scoreMap = {
          'bmi': item.bmi_score,
          'running_50m': item.running_score,
          'long_jump': item.jump_score,
          'sit_ups': item.situp_score,
          'endurance_run': item.endurance_score,
          'flexibility': item.flexibility_score
        }
        totalScore += scoreMap[selectedItem.value] || 0
      }
    })
    
    avgScores.push((totalScore / items.length).toFixed(2))
  }
  
  // 柱状图配置
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: classNames,
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        min: 0,
        max: 100,
        interval: 10
      }
    ],
    series: [
      {
        name: '平均分',
        type: 'bar',
        barWidth: '60%',
        data: avgScores,
        itemStyle: {
          color: function(params) {
            const score = parseFloat(params.data)
            if (score >= 90) return '#52c41a'
            if (score >= 80) return '#1890ff'
            if (score >= 70) return '#faad14'
            if (score >= 60) return '#d9d9d9'
            return '#f5222d'
          }
        }
      }
    ]
  }
  
  avgScoreChart.setOption(option)
}

// 更新趋势图
const updateTrendChart = () => {
  // 按测试日期分组数据
  const resultsByDate = {}
  
  filteredResults.value.forEach(item => {
    const testDate = item.test_date
    if (!resultsByDate[testDate]) {
      resultsByDate[testDate] = []
    }
    resultsByDate[testDate].push(item)
  })
  
  // 计算每个日期的平均分
  const dates = Object.keys(resultsByDate).sort()
  const avgScores = []
  
  dates.forEach(date => {
    const items = resultsByDate[date]
    let totalScore = 0
    
    items.forEach(item => {
      if (selectedItem.value === 'all' || selectedItem.value === 'total_score') {
        totalScore += item.total_score
      } else {
        const scoreMap = {
          'bmi': item.bmi_score,
          'running_50m': item.running_score,
          'long_jump': item.jump_score,
          'sit_ups': item.situp_score,
          'endurance_run': item.endurance_score,
          'flexibility': item.flexibility_score
        }
        totalScore += scoreMap[selectedItem.value] || 0
      }
    })
    
    avgScores.push((totalScore / items.length).toFixed(2))
  })
  
  // 趋势图配置
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      interval: 10
    },
    series: [
      {
        name: '平均分',
        type: 'line',
        data: avgScores,
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#1890ff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(24, 144, 255, 0.5)'
            },
            {
              offset: 1,
              color: 'rgba(24, 144, 255, 0.1)'
            }
          ])
        }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 生命周期钩子
onMounted(() => {
  fetchTestPlans()
  fetchTestResults()
})

// 清理工作
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  pieChart?.dispose()
  avgScoreChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.test-result-analysis {
  padding: 24px;
}

.filter-section {
  margin-bottom: 24px;
}

.chart-row {
  margin-bottom: 24px;
}

.score-excellent {
  color: #52c41a;
  font-weight: bold;
}

.score-good {
  color: #1890ff;
  font-weight: bold;
}

.score-average {
  color: #faad14;
}

.score-pass {
  color: #d9d9d9;
}

.score-fail {
  color: #f5222d;
}
</style>
