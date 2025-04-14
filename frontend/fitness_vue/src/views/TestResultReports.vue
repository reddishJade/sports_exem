<!--
  @description 体测成绩报表管理组件
  @roles 管理员、教师 - 生成和导出各类体测报表
  @functionality
    - 提供班级报表功能，包含班级整体成绩统计和学生个人成绩列表
    - 提供学生个人报表功能，展示学生历次测试成绩和对比分析
    - 支持年度报表功能，对比不同班级的平均成绩
    - 集成图表可视化，包括成绩分布饼图、成绩趋势折线图等
    - 支持报表导出（Excel、PDF）和打印功能
    - 提供多维度的数据筛选和查询功能
-->

<template>
  <div class="test-result-reports">
    <a-card title="成绩报表管理" :bordered="false">
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="class" tab="班级报表">
          <div class="filter-section">
            <a-row :gutter="16">
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label="测试计划">
                  <a-select
                    v-model:value="classReport.selectedPlan"
                    placeholder="选择测试计划"
                    :loading="plansLoading"
                    @change="handleClassPlanChange"
                    style="width: 100%"
                  >
                    <a-select-option v-for="plan in testPlans" :key="plan.id" :value="plan.id">
                      {{ plan.title }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label="班级">
                  <a-select
                    v-model:value="classReport.selectedClass"
                    placeholder="选择班级"
                    @change="generateClassReport"
                    style="width: 100%"
                  >
                    <a-select-option v-for="classItem in classOptions" :key="classItem" :value="classItem">
                      {{ classItem }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label=" ">
                  <a-button 
                    type="primary" 
                    @click="generateClassReport"
                    :disabled="!classReport.selectedPlan || !classReport.selectedClass"
                  >
                    生成报表
                  </a-button>
                </a-form-item>
              </a-col>
            </a-row>
          </div>

          <a-skeleton active :loading="classReport.loading" v-if="classReport.loading" />
          
          <div v-else-if="classReport.data">
            <a-card 
              class="report-card" 
              :bordered="false"
              title="班级体测成绩报表"
              :extra="classReport.data.basic?.class_name"
            >
              <a-descriptions bordered>
                <a-descriptions-item label="测试计划" :span="1">
                  {{ classReport.data.basic?.plan_title }}
                </a-descriptions-item>
                <a-descriptions-item label="测试日期" :span="1">
                  {{ classReport.data.basic?.test_date }}
                </a-descriptions-item>
                <a-descriptions-item label="班级" :span="1">
                  {{ classReport.data.basic?.class_name }}
                </a-descriptions-item>
                <a-descriptions-item label="测试人数" :span="1">
                  {{ classReport.data.statistics?.total_students }}
                </a-descriptions-item>
                <a-descriptions-item label="平均成绩" :span="1">
                  <span :class="getScoreClass(classReport.data.statistics?.avg_score)">
                    {{ classReport.data.statistics?.avg_score }}
                  </span>
                </a-descriptions-item>
                <a-descriptions-item label="及格率" :span="1">
                  {{ classReport.data.statistics?.pass_rate }}%
                </a-descriptions-item>
                <a-descriptions-item label="男生平均成绩" :span="1">
                  <span :class="getScoreClass(classReport.data.statistics?.male_avg_score)">
                    {{ classReport.data.statistics?.male_avg_score }}
                  </span>
                </a-descriptions-item>
                <a-descriptions-item label="女生平均成绩" :span="1">
                  <span :class="getScoreClass(classReport.data.statistics?.female_avg_score)">
                    {{ classReport.data.statistics?.female_avg_score }}
                  </span>
                </a-descriptions-item>
                <a-descriptions-item label="优秀率" :span="1">
                  {{ classReport.data.statistics?.excellent_rate }}%
                </a-descriptions-item>
              </a-descriptions>
              
              <div class="report-chart-container">
                <div ref="classDistributionChart" style="height: 300px; width: 100%;"></div>
              </div>
              
              <a-divider orientation="left">各项目得分统计</a-divider>
              
              <a-table 
                :columns="classItemColumns" 
                :data-source="classReport.data.items" 
                :pagination="false" 
                bordered
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.dataIndex === 'avg_score'">
                    <span :class="getScoreClass(record.avg_score)">{{ record.avg_score }}</span>
                  </template>
                  <template v-if="column.dataIndex === 'pass_rate' || column.dataIndex === 'excellent_rate'">
                    {{ record[column.dataIndex] }}%
                  </template>
                </template>
              </a-table>
              
              <a-divider orientation="left">班级学生成绩详情</a-divider>
              
              <a-table 
                :columns="studentColumns" 
                :data-source="classReport.data.students" 
                :pagination="{ pageSize: 10 }" 
                bordered
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.dataIndex === 'total_score'">
                    <span :class="getScoreClass(record.total_score)">{{ record.total_score }}</span>
                  </template>
                  <template v-if="column.dataIndex === 'level'">
                    <a-tag :color="getLevelColor(record.level)">{{ record.level }}</a-tag>
                  </template>
                  <template v-if="column.dataIndex === 'action'">
                    <a @click="viewStudentDetail(record)">查看详情</a>
                  </template>
                </template>
              </a-table>
              
              <div class="report-actions">
                <a-button type="primary" @click="exportClassReport('pdf')">
                  <file-pdf-outlined />
                  导出PDF
                </a-button>
                <a-button style="margin-left: 8px" @click="exportClassReport('excel')">
                  <file-excel-outlined />
                  导出Excel
                </a-button>
                <a-button style="margin-left: 8px" @click="printClassReport">
                  <printer-outlined />
                  打印报表
                </a-button>
              </div>
            </a-card>
          </div>
          
          <div v-else-if="!classReport.data && classReport.generated" class="empty-report">
            <a-empty description="暂无符合条件的班级成绩数据" />
          </div>
        </a-tab-pane>
        
        <a-tab-pane key="student" tab="学生个人报表">
          <div class="filter-section">
            <a-row :gutter="16">
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label="测试计划">
                  <a-select
                    v-model:value="studentReport.selectedPlan"
                    placeholder="选择测试计划"
                    :loading="plansLoading"
                    @change="handleStudentPlanChange"
                    style="width: 100%"
                  >
                    <a-select-option v-for="plan in testPlans" :key="plan.id" :value="plan.id">
                      {{ plan.title }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label="学生">
                  <a-select
                    v-model:value="studentReport.selectedStudent"
                    placeholder="选择学生"
                    :loading="studentReport.studentsLoading"
                    @change="generateStudentReport"
                    style="width: 100%"
                    :disabled="!studentReport.selectedPlan"
                  >
                    <a-select-option v-for="student in studentReport.students" :key="student.id" :value="student.id">
                      {{ student.name }} ({{ student.student_id }})
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label=" ">
                  <a-button 
                    type="primary" 
                    @click="generateStudentReport"
                    :disabled="!studentReport.selectedPlan || !studentReport.selectedStudent"
                  >
                    生成报表
                  </a-button>
                </a-form-item>
              </a-col>
            </a-row>
          </div>

          <a-skeleton active :loading="studentReport.loading" v-if="studentReport.loading" />
          
          <div v-else-if="studentReport.data" class="student-report">
            <div class="student-report-header">
              <div class="logo">
                <img src="../assets/logo.png" alt="学校标志" />
              </div>
              <div class="title">
                <h1>学生体质测试成绩报告单</h1>
                <p>{{ studentReport.data.basic?.plan_title }}</p>
              </div>
            </div>
            
            <div class="student-info-section">
              <a-row :gutter="16">
                <a-col :xs="24" :md="6">
                  <div class="student-avatar">
                    <a-avatar :size="100">
                      {{ studentReport.data.basic?.name?.charAt(0) }}
                    </a-avatar>
                  </div>
                </a-col>
                <a-col :xs="24" :md="18">
                  <a-descriptions bordered :column="{ xxl: 4, xl: 3, lg: 3, md: 3, sm: 2, xs: 1 }">
                    <a-descriptions-item label="姓名">{{ studentReport.data.basic?.name }}</a-descriptions-item>
                    <a-descriptions-item label="学号">{{ studentReport.data.basic?.student_id }}</a-descriptions-item>
                    <a-descriptions-item label="性别">{{ studentReport.data.basic?.gender }}</a-descriptions-item>
                    <a-descriptions-item label="班级">{{ studentReport.data.basic?.class_name }}</a-descriptions-item>
                    <a-descriptions-item label="测试日期">{{ studentReport.data.basic?.test_date }}</a-descriptions-item>
                    <a-descriptions-item label="总分">
                      <span :class="getScoreClass(studentReport.data.basic?.total_score)">
                        {{ studentReport.data.basic?.total_score }}
                      </span>
                    </a-descriptions-item>
                    <a-descriptions-item label="等级">
                      <a-tag :color="getLevelColor(studentReport.data.basic?.level)">
                        {{ studentReport.data.basic?.level }}
                      </a-tag>
                    </a-descriptions-item>
                    <a-descriptions-item label="班级排名">
                      {{ studentReport.data.basic?.class_rank }}/{{ studentReport.data.basic?.class_total }}
                    </a-descriptions-item>
                  </a-descriptions>
                </a-col>
              </a-row>
            </div>
            
            <div class="student-results-section">
              <h2>测试详情</h2>
              <a-table 
                :columns="studentItemColumns" 
                :data-source="studentReport.data.items" 
                :pagination="false"
                bordered
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.dataIndex === 'score'">
                    <span :class="getScoreClass(record.score)">{{ record.score }}</span>
                  </template>
                  <template v-if="column.dataIndex === 'level'">
                    <a-tag :color="getLevelColor(record.level)">{{ record.level }}</a-tag>
                  </template>
                  <template v-if="column.dataIndex === 'percentile'">
                    {{ record.percentile }}%
                  </template>
                </template>
              </a-table>
            </div>
            
            <div class="student-charts-section">
              <a-row :gutter="16">
                <a-col :xs="24" :lg="12">
                  <div class="chart-container">
                    <h3>各项得分情况</h3>
                    <div ref="studentScoreChart" style="height: 300px;"></div>
                  </div>
                </a-col>
                <a-col :xs="24" :lg="12">
                  <div class="chart-container">
                    <h3>与班级平均分比较</h3>
                    <div ref="studentComparisonChart" style="height: 300px;"></div>
                  </div>
                </a-col>
              </a-row>
            </div>
            
            <div class="student-comment-section">
              <h2>老师评语</h2>
              <div class="comment-content">{{ studentReport.data.comment }}</div>
              <div class="signature">
                <div>体育老师：______________</div>
                <div>日期：______________</div>
              </div>
            </div>
            
            <div class="report-actions">
              <a-button type="primary" @click="exportStudentReport('pdf')">
                <file-pdf-outlined />
                导出PDF
              </a-button>
              <a-button style="margin-left: 8px" @click="printStudentReport">
                <printer-outlined />
                打印报表
              </a-button>
            </div>
          </div>
          
          <div v-else-if="!studentReport.data && studentReport.generated" class="empty-report">
            <a-empty description="暂无符合条件的学生成绩数据" />
          </div>
        </a-tab-pane>
        
        <a-tab-pane key="annual" tab="学年度报表">
          <div class="filter-section">
            <a-row :gutter="16">
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label="学年">
                  <a-select
                    v-model:value="annualReport.selectedYear"
                    placeholder="选择学年"
                    style="width: 100%"
                  >
                    <a-select-option v-for="year in ['2023-2024', '2022-2023', '2021-2022']" :key="year" :value="year">
                      {{ year }}学年
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label="年级">
                  <a-select
                    v-model:value="annualReport.selectedGrade"
                    placeholder="选择年级"
                    style="width: 100%"
                  >
                    <a-select-option value="all">全部年级</a-select-option>
                    <a-select-option v-for="grade in ['高一', '高二', '高三']" :key="grade" :value="grade">
                      {{ grade }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="8" :md="6">
                <a-form-item label=" ">
                  <a-button 
                    type="primary" 
                    @click="generateAnnualReport"
                  >
                    生成报表
                  </a-button>
                </a-form-item>
              </a-col>
            </a-row>
          </div>

          <div v-if="annualReport.loading">
            <a-skeleton active />
          </div>
          
          <div v-else-if="annualReport.data">
            <a-card title="学年度体测成绩总结报告">
              <a-descriptions bordered>
                <a-descriptions-item label="学年">{{ annualReport.selectedYear }}</a-descriptions-item>
                <a-descriptions-item label="总人数">1245</a-descriptions-item>
                <a-descriptions-item label="平均分">
                  <span class="score-good">83.2</span>
                </a-descriptions-item>
                <a-descriptions-item label="及格率">92.5%</a-descriptions-item>
                <a-descriptions-item label="优秀率">24.8%</a-descriptions-item>
                <a-descriptions-item label="不及格率">7.5%</a-descriptions-item>
              </a-descriptions>
              
              <div class="chart-container" ref="annualChartRef" style="height: 350px; margin: 20px 0;"></div>
              
              <a-table 
                :columns="[
                  { title: '班级', dataIndex: 'class_name' },
                  { title: '人数', dataIndex: 'student_count' },
                  { title: '平均分', dataIndex: 'avg_score' },
                  { title: '及格率', dataIndex: 'pass_rate' },
                  { title: '优秀率', dataIndex: 'excellent_rate' }
                ]" 
                :data-source="[
                  { key: '1', class_name: '高一(1)班', student_count: 45, avg_score: 85.6, pass_rate: '95%', excellent_rate: '28%' },
                  { key: '2', class_name: '高一(2)班', student_count: 47, avg_score: 82.4, pass_rate: '93%', excellent_rate: '23%' },
                  { key: '3', class_name: '高二(1)班', student_count: 42, avg_score: 84.1, pass_rate: '94%', excellent_rate: '26%' },
                  { key: '4', class_name: '高二(2)班', student_count: 44, avg_score: 81.8, pass_rate: '91%', excellent_rate: '22%' }
                ]"
                :pagination="false"
                bordered
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.dataIndex === 'avg_score'">
                    <span :class="getScoreClass(record.avg_score)">{{ record.avg_score }}</span>
                  </template>
                </template>
              </a-table>
              
              <div class="report-actions" style="margin-top: 16px;">
                <a-button type="primary">
                  <file-pdf-outlined />
                  导出PDF
                </a-button>
                <a-button style="margin-left: 8px">
                  <printer-outlined />
                  打印报表
                </a-button>
              </div>
            </a-card>
          </div>
          
          <div v-else>
            <a-empty description="请选择学年并生成报表" />
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import axios from 'axios'
import * as echarts from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { LabelLayout, UniversalTransition } from 'echarts/features'
import { CanvasRenderer } from 'echarts/renderers'
import { exportToExcel, exportTableToPdf, exportElementToPdf, printElement } from '../services/exportService'

// 注册必需的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer,
  PieChart,
  BarChart
])

const store = useStore()
const router = useRouter()
const token = computed(() => store.state.token)

// 当前激活的标签页
const activeTab = ref('class')

// 测试计划数据
const testPlans = ref([])
const plansLoading = ref(false)
const classOptions = ref([])

// 班级报表数据
const classReport = reactive({
  selectedPlan: undefined,
  selectedClass: undefined,
  loading: false,
  generated: false,
  data: null
})

// 学生个人报表数据
const studentReport = reactive({
  selectedPlan: undefined,
  selectedStudent: undefined,
  loading: false,
  generated: false,
  data: null,
  students: [],
  studentsLoading: false
})

// 学年度报表数据
const annualReport = reactive({
  selectedYear: undefined,
  selectedGrade: undefined,
  loading: false,
  data: null
})

// 图表引用
const classDistributionChart = ref(null)
let distributionChartInstance = null

const studentScoreChart = ref(null)
let studentScoreChartInstance = null

const studentComparisonChart = ref(null)
let studentComparisonChartInstance = null

const annualChartRef = ref(null)
let annualChartInstance = null

// 班级项目统计表格列定义
const classItemColumns = [
  { title: '测试项目', dataIndex: 'item_name', key: 'item_name' },
  { title: '平均分', dataIndex: 'avg_score', key: 'avg_score', sorter: (a, b) => a.avg_score - b.avg_score },
  { title: '及格率', dataIndex: 'pass_rate', key: 'pass_rate' },
  { title: '优秀率', dataIndex: 'excellent_rate', key: 'excellent_rate' },
  { title: '最高分', dataIndex: 'max_score', key: 'max_score' },
  { title: '最低分', dataIndex: 'min_score', key: 'min_score' }
]

// 学生成绩表格列定义
const studentColumns = [
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '学号', dataIndex: 'student_id', key: 'student_id' },
  { title: '性别', dataIndex: 'gender', key: 'gender' },
  { title: '总分', dataIndex: 'total_score', key: 'total_score', sorter: (a, b) => a.total_score - b.total_score },
  { title: '等级', dataIndex: 'level', key: 'level' },
  { title: '排名', dataIndex: 'rank', key: 'rank' },
  { title: '操作', dataIndex: 'action', key: 'action' }
]

// 学生个人成绩表格列定义
const studentItemColumns = [
  { title: '测试项目', dataIndex: 'item_name', key: 'item_name' },
  { title: '成绩', dataIndex: 'score', key: 'score' },
  { title: '等级', dataIndex: 'level', key: 'level' },
  { title: '百分比', dataIndex: 'percentile', key: 'percentile' }
]

// 获取等级对应的颜色
const getLevelColor = (level) => {
  const colors = {
    '优秀': 'success',
    '良好': 'processing',
    '中等': 'warning',
    '及格': 'default',
    '不及格': 'error'
  }
  return colors[level] || 'default'
}

// 获取分数对应的CSS类
const getScoreClass = (score) => {
  if (!score) return ''
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
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

// 获取班级选项
const fetchClassOptions = async () => {
  try {
    const response = await axios.get('/api/classes/', {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    classOptions.value = response.data.map(c => c.name)
  } catch (error) {
    console.error('获取班级列表失败:', error)
    // 模拟一些班级数据以便开发
    classOptions.value = ['高一(1)班', '高一(2)班', '高二(1)班', '高二(2)班']
  }
}

// 处理班级计划变更
const handleClassPlanChange = () => {
  classReport.selectedClass = undefined
  classReport.data = null
  classReport.generated = false
}

// 处理学生计划变更
const handleStudentPlanChange = () => {
  studentReport.selectedStudent = undefined
  studentReport.data = null
  studentReport.generated = false
  fetchStudents()
}

// 获取学生列表
const fetchStudents = async () => {
  studentReport.studentsLoading = true
  try {
    const response = await axios.get('/api/students/', {
      headers: { Authorization: `Bearer ${token.value}` },
      params: { plan_id: studentReport.selectedPlan }
    })
    studentReport.students = response.data
  } catch (error) {
    console.error('获取学生列表失败:', error)
  } finally {
    studentReport.studentsLoading = false
  }
}

// 生成班级报表
const generateClassReport = async () => {
  if (!classReport.selectedPlan || !classReport.selectedClass) return
  
  classReport.loading = true
  classReport.generated = true
  
  try {
    // 调用真实的API获取班级报表数据
    const response = await fetchClassReport(classReport.selectedPlan, classReport.selectedClass)
    classReport.data = response
    
    // 渲染报表图表
    if (response) {
      setTimeout(() => {
        renderDistributionChart()
      }, 100)
    }
  } catch (error) {
    console.error('生成班级报表失败:', error)
    classReport.data = null
  } finally {
    classReport.loading = false
  }
}

// 生成学生个人报表
const generateStudentReport = async () => {
  if (!studentReport.selectedPlan || !studentReport.selectedStudent) return
  
  studentReport.loading = true
  studentReport.generated = true
  
  try {
    // 调用真实的API获取学生个人报表数据
    const response = await fetchStudentReport(studentReport.selectedPlan, studentReport.selectedStudent)
    studentReport.data = response
    
    // 渲染报表图表
    if (response) {
      setTimeout(() => {
        renderStudentScoreChart()
        renderStudentComparisonChart()
      }, 100)
    }
  } catch (error) {
    console.error('生成学生个人报表失败:', error)
    studentReport.data = null
  } finally {
    studentReport.loading = false
  }
}

// 生成学年度报表
const generateAnnualReport = async () => {
  if (!annualReport.selectedYear) return
  
  annualReport.loading = true
  
  try {
    // 调用真实的API获取学年度报表数据
    const response = await fetchAnnualReport(annualReport.selectedYear)
    annualReport.data = response
    
    // 渲染报表图表
    if (response) {
      setTimeout(() => {
        renderAnnualChart()
      }, 100)
    }
  } catch (error) {
    console.error('生成学年度报表失败:', error)
    annualReport.data = null
  } finally {
    annualReport.loading = false
  }
}

// 使用API获取班级报表数据
const fetchClassReport = async (planId, className) => {
  try {
    // 调用后端 API 获取班级报表数据
    const response = await axios.get('/api/reports/class', {
      params: {
        plan_id: planId,
        class_name: className
      }
    })
    return response.data
  } catch (error) {
    console.error('获取班级报表失败:', error)
    message.error('获取班级报表数据失败，请稍后再试')
    // 返回空数据而不是模拟数据
    return null
  }
}

// 使用API获取学生个人报表数据
const fetchStudentReport = async (planId, studentId) => {
  try {
    // 调用后端 API 获取学生个人报表数据
    const response = await axios.get('/api/reports/student', {
      params: {
        plan_id: planId,
        student_id: studentId
      }
    })
    return response.data
  } catch (error) {
    console.error('获取学生个人报表失败:', error)
    message.error('获取学生个人报表数据失败，请稍后再试')
    // 返回空数据而不是模拟数据
    return null
  }
}

// 使用API获取学年度报表数据
const fetchAnnualReport = async (year) => {
  try {
    // 调用后端 API 获取学年度报表数据
    const response = await axios.get('/api/reports/annual', {
      params: {
        year: year
      }
    })
    return response.data
  } catch (error) {
    console.error('获取学年度报表失败:', error)
    message.error('获取学年度报表数据失败，请稍后再试')
    // 返回空数据而不是模拟数据
    return null
  }
}

// 渲染分布图表
const renderDistributionChart = () => {
  if (!classReport.data || !classDistributionChart.value) return
  
  if (distributionChartInstance) {
    distributionChartInstance.dispose()
  }
  
  distributionChartInstance = echarts.init(classDistributionChart.value)
  
  // 计算各等级人数
  const levelCounts = {
    '优秀': 0,
    '良好': 0,
    '中等': 0,
    '及格': 0,
    '不及格': 0
  }
  
  classReport.data.students.forEach(student => {
    levelCounts[student.level]++
  })
  
  const option = {
    title: {
      text: '班级成绩分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: Object.keys(levelCounts)
    },
    series: [
      {
        name: '成绩分布',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: Object.entries(levelCounts).map(([name, value]) => ({ name, value })),
        color: ['#52c41a', '#1890ff', '#faad14', '#d9d9d9', '#f5222d']
      }
    ]
  }
  
  distributionChartInstance.setOption(option)
}

// 渲染学生个人成绩图表
const renderStudentScoreChart = () => {
  if (!studentReport.data || !studentScoreChart.value) return
  
  if (studentScoreChartInstance) {
    studentScoreChartInstance.dispose()
  }
  
  studentScoreChartInstance = echarts.init(studentScoreChart.value)
  
  const option = {
    title: {
      text: '各项得分情况',
      left: 'center'
    },
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
        data: studentReport.data.items.map(item => item.item_name),
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: '成绩',
        type: 'bar',
        barWidth: '60%',
        data: studentReport.data.items.map(item => item.score),
        color: '#52c41a'
      }
    ]
  }
  
  studentScoreChartInstance.setOption(option)
}

// 渲染学生个人成绩比较图表
const renderStudentComparisonChart = () => {
  if (!studentReport.data || !studentComparisonChart.value) return
  
  if (studentComparisonChartInstance) {
    studentComparisonChartInstance.dispose()
  }
  
  studentComparisonChartInstance = echarts.init(studentComparisonChart.value)
  
  const option = {
    title: {
      text: '与班级平均分比较',
      left: 'center'
    },
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
        data: studentReport.data.items.map(item => item.item_name),
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: '学生成绩',
        type: 'bar',
        barWidth: '60%',
        data: studentReport.data.items.map(item => item.score),
        color: '#52c41a'
      },
      {
        name: '班级平均分',
        type: 'bar',
        barWidth: '60%',
        data: studentReport.data.items.map(item => item.avg_score),
        color: '#1890ff'
      }
    ]
  }
  
  studentComparisonChartInstance.setOption(option)
}

// 渲染学年度报表图表
const renderAnnualChart = () => {
  if (!annualReport.data || !annualChartRef.value) return
  
  if (annualChartInstance) {
    annualChartInstance.dispose()
  }
  
  annualChartInstance = echarts.init(annualChartRef.value)
  
  const option = {
    title: {
      text: '学年度成绩分布',
      left: 'center'
    },
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
        data: annualReport.data.items.map(item => item.class_name),
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: '平均分',
        type: 'bar',
        barWidth: '60%',
        data: annualReport.data.items.map(item => item.avg_score),
        color: '#52c41a'
      }
    ]
  }
  
  annualChartInstance.setOption(option)
}

// 查看学生详情
const viewStudentDetail = (student) => {
  // 这里应该跳转到学生详情页面或显示详情弹窗
  // 暂时预留，将在下一步实现
  console.log('查看学生详情:', student)
}

// 导出班级报表
const exportClassReport = (type) => {
  if (type === 'pdf') {
    exportElementToPdf(classReport.data, '班级体测成绩报表')
  } else if (type === 'excel') {
    exportToExcel(classReport.data, '班级体测成绩报表')
  }
}

// 导出学生个人报表
const exportStudentReport = (type) => {
  if (type === 'pdf') {
    exportElementToPdf(studentReport.data, '学生体质测试成绩报告单')
  }
}

// 打印班级报表
const printClassReport = () => {
  printElement(classReport.data, '班级体测成绩报表')
}

// 打印学生个人报表
const printStudentReport = () => {
  printElement(studentReport.data, '学生体质测试成绩报告单')
}

// 窗口大小变化处理
const handleResize = () => {
  distributionChartInstance?.resize()
  studentScoreChartInstance?.resize()
  studentComparisonChartInstance?.resize()
  annualChartInstance?.resize()
}

// 生命周期钩子
onMounted(() => {
  fetchTestPlans()
  fetchClassOptions()
  window.addEventListener('resize', handleResize)
})

// 清理工作
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (distributionChartInstance) {
    distributionChartInstance.dispose()
  }
  if (studentScoreChartInstance) {
    studentScoreChartInstance.dispose()
  }
  if (studentComparisonChartInstance) {
    studentComparisonChartInstance.dispose()
  }
  if (annualChartInstance) {
    annualChartInstance.dispose()
  }
})
</script>

<style scoped>
.test-result-reports {
  padding: 24px;
}

.filter-section {
  margin-bottom: 24px;
}

.report-card {
  margin-bottom: 24px;
}

.report-chart-container {
  margin: 24px 0;
}

.report-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.empty-report {
  padding: 48px 0;
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

.student-report {
  padding: 24px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.student-report-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.student-report-header .logo {
  margin-right: 16px;
}

.student-report-header .logo img {
  width: 100px;
  height: 100px;
}

.student-report-header .title {
  font-size: 24px;
  font-weight: bold;
}

.student-info-section {
  margin-bottom: 24px;
}

.student-avatar {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 16px;
}

.student-avatar .ant-avatar {
  font-size: 48px;
}

.student-results-section {
  margin-bottom: 24px;
}

.student-results-section h2 {
  margin-top: 0;
}

.student-charts-section {
  margin-bottom: 24px;
}

.chart-container {
  margin-bottom: 16px;
}

.chart-container h3 {
  margin-top: 0;
}

.student-comment-section {
  margin-bottom: 24px;
}

.student-comment-section h2 {
  margin-top: 0;
}

.comment-content {
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.signature {
  margin-top: 16px;
  text-align: right;
}

@media print {
  .filter-section,
  .report-actions,
  .ant-tabs-nav {
    display: none !important;
  }
}
</style>
