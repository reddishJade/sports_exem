<template>
  <div class="health-report-container">
    <div class="health-report">
      <div class="page-header">
        <h1 class="page-title">
          <medicine-box-outlined /> 体质健康报告
        </h1>
        <p class="page-description">查看及管理体质健康评估报告</p>
      </div>
      
      <div class="table-actions-container">
        <div class="table-operations">
          <a-space>
            <a-button 
              type="primary" 
              @click="showModal" 
              v-if="isAdmin"
              class="create-button"
            >
              <plus-outlined /> 生成体质报告
            </a-button>
            <a-input-search
              v-model:value="searchValue"
              placeholder="搜索学生姓名"
              class="search-input"
              @search="onSearch"
            >
              <template #prefix>
                <search-outlined />
              </template>
            </a-input-search>
          </a-space>
        </div>
      </div>

      <div class="table-container">
        <a-table 
          :columns="columns" 
          :data-source="reports" 
          :loading="loading" 
          :pagination="{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            pageSizeOptions: ['10', '20', '50'],
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: handlePageChange,
            onShowSizeChange: handlePageSizeChange
          }"
          @change="handlePageChange"
          :rowKey="record => record.id"
          class="reports-table"
          :row-class-name="record => record._hasError ? (record._errorType === 'missing' ? 'row-warning' : 'row-error') : ''"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-space>
                <a-button type="link" @click="viewReport(record)" class="action-button">
                  <eye-outlined /> 查看
                </a-button>
                <template v-if="isAdmin">
                  <a-button type="link" @click="editReport(record)" class="action-button">
                    <edit-outlined /> 编辑
                  </a-button>
                  <a-popconfirm
                    title="确定要删除这个体质报告吗？"
                    @confirm="deleteReport(record)"
                    ok-text="是"
                    cancel-text="否"
                  >
                    <a-button type="link" danger class="action-button">
                      <delete-outlined /> 删除
                    </a-button>
                  </a-popconfirm>
                </template>
              </a-space>
            </template>
            <template v-else-if="column.key === 'student_name'">
              <span v-if="record._hasError">
                {{ record.student_name }}
                <a-tag v-if="record._errorType === 'missing'" color="orange" style="margin-left: 8px">数据缺失</a-tag>
                <a-tag v-else color="red" style="margin-left: 8px">加载错误</a-tag>
              </span>
              <span v-else>{{ record.student_name }}</span>
            </template>
            <template v-else-if="column.key === 'test_date'">
              <span v-if="record._hasError" style="color: #faad14">{{ record.test_date }}</span>
              <span v-else>{{ record.test_date }}</span>
            </template>
            <template v-else-if="column.key === 'total_score'">
              <span v-if="record._hasError" :style="{ color: record._errorType === 'missing' ? '#faad14' : '#ff4d4f' }">{{ record.total_score }}</span>
              <span v-else>{{ record.total_score }}</span>
            </template>
          </template>
        </a-table>
      </div>

      <!-- 报告编辑模态框 -->
      <a-modal
        :title="modalTitle"
        :open="visible"
        @ok="handleOk"
        @cancel="handleCancel"
        :confirmLoading="confirmLoading"
        width="800px"
        class="report-modal"
      >
        <a-form
          :model="formState"
          :rules="rules"
          ref="formRef"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 18 }"
          class="report-form"
        >
          <a-form-item label="测试结果" name="test_result" v-if="!formState.id">
            <a-select
              v-model:value="formState.test_result"
              show-search
              placeholder="选择测试结果"
              :options="testResults"
              :field-names="{ label: 'display_name', value: 'id' }"
              class="form-select"
            />
          </a-form-item>
          <a-form-item label="总体评估" name="overall_assessment">
            <a-textarea 
              v-model:value="formState.overall_assessment" 
              :rows="4" 
              placeholder="请输入对学生体质的总体评估"
              class="form-textarea"
            />
          </a-form-item>
          <a-form-item label="健康建议" name="health_suggestions">
            <a-textarea 
              v-model:value="formState.health_suggestions" 
              :rows="6" 
              placeholder="请输入针对学生的健康建议"
              class="form-textarea"
            />
          </a-form-item>
        </a-form>
      </a-modal>

      <!-- 报告详情模态框 -->
      <a-modal
        :title="null"
        :open="detailVisible"
        @ok="closeDetail"
        @cancel="closeDetail"
        width="800px"
        class="detail-modal"
        :footer="null"
        :closable="false"
        :bodyStyle="{ maxHeight: '80vh', overflow: 'auto' }"
      >
        <div class="report-detail-header">
          <h2 class="report-title">
            <medicine-box-outlined /> 体质评估报告
          </h2>
        </div>
        
        <a-divider class="divider-light" />
        
        <div class="report-detail-content" v-if="currentDetail">
          <div class="student-info-section">
            <a-row :gutter="24">
              <a-col :xs="24" :md="12">
                <div class="info-item">
                  <div class="info-label">学生姓名</div>
                  <div class="info-value">{{ currentDetail?.test_result?.student?.name }}</div>
                </div>
              </a-col>
              <a-col :xs="24" :md="12">
                <div class="info-item">
                  <div class="info-label">测试日期</div>
                  <div class="info-value">{{ formatDate(currentDetail?.test_result?.test_date) }}</div>
                </div>
              </a-col>
            </a-row>
            
            <a-row :gutter="24">
              <a-col :xs="24" :md="12">
                <div class="info-item">
                  <div class="info-label">BMI指数</div>
                  <div class="info-value">{{ currentDetail?.test_result?.bmi }}</div>
                </div>
              </a-col>
              <a-col :xs="24" :md="12">
                <div class="info-item">
                  <div class="info-label">总分</div>
                  <div class="info-value">
                    <a-tag :color="getScoreTagColor(currentDetail?.test_result?.total_score)" class="score-tag large">
                      {{ currentDetail?.test_result?.total_score }}
                    </a-tag>
                  </div>
                </div>
              </a-col>
            </a-row>
          </div>

          <!-- 显示错误提示 -->
          <div v-if="currentDetail.test_result && currentDetail.test_result._error" class="error-alert">
            <a-alert
              :type="currentDetail.test_result._errorType === 'missing' ? 'info' : 'warning'"
              :message="currentDetail.test_result._errorType === 'missing' ? '测试结果数据缺失' : '测试结果数据加载错误'"
              :description="currentDetail.test_result._errorMessage || '无法加载测试结果数据'"
              show-icon
            >
              <template #icon>
                <ExclamationCircleOutlined v-if="currentDetail.test_result._errorType !== 'missing'" />
                <InfoCircleOutlined v-else />
              </template>
            </a-alert>
          </div>
          
          <div class="report-content-section">
            <div class="section-card">
              <div class="section-title">
                <safety-outlined /> 总体评估
              </div>
              <div class="section-content">
                {{ currentDetail?.overall_assessment }}
              </div>
            </div>

            <div class="section-card">
              <div class="section-title">
                <bulb-outlined /> 健康建议
              </div>
              <div class="section-content">
                {{ currentDetail?.health_suggestions }}
              </div>
            </div>

            <div class="section-card">
              <div class="section-title">
                <bar-chart-outlined /> 各项指标详情
              </div>
              <div class="section-content">
                <!-- 显示无数据提示 -->
                <div v-if="currentDetail.test_result && currentDetail.test_result._error" class="no-data-container">
                  <a-empty
                    :description="'测试结果数据不可用'"
                    :image="Empty.PRESENTED_IMAGE_SIMPLE"
                  >
                    <template #description>
                      <span>{{ currentDetail.test_result._errorMessage || '测试结果数据不可用' }}</span>
                    </template>
                    <template #extra>
                      <p v-if="currentDetail.test_result._errorType === 'missing'" class="missing-data-hint">
                        您仍然可以查看报告的总体评估和健康建议
                      </p>
                    </template>
                  </a-empty>
                </div>
                
                <!-- 显示正常数据 -->
                <a-row v-else :gutter="[24, 24]">
                  <a-col :xs="24" :sm="12" :md="8">
                    <div class="indicator-card">
                      <a-statistic 
                        title="肺活量(ml)" 
                        :value="currentDetail?.test_result?.vital_capacity"
                        :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.vital_capacity, 'vital_capacity') }"
                        class="indicator-statistic"
                      />
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12" :md="8">
                    <div class="indicator-card">
                      <a-statistic 
                        title="50米跑(秒)" 
                        :value="currentDetail?.test_result?.run_50m"
                        :precision="2"
                        :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.run_50m, 'run_50m') }"
                        class="indicator-statistic"
                      />
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12" :md="8">
                    <div class="indicator-card">
                      <a-statistic 
                        title="坐位体前屈(cm)" 
                        :value="currentDetail?.test_result?.sit_and_reach"
                        :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.sit_and_reach, 'sit_and_reach') }"
                        class="indicator-statistic"
                      />
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12" :md="8">
                    <div class="indicator-card">
                      <a-statistic 
                        title="立定跳远(cm)" 
                        :value="currentDetail?.test_result?.standing_jump"
                        :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.standing_jump, 'standing_jump') }"
                        class="indicator-statistic"
                      />
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12" :md="8">
                    <div class="indicator-card">
                      <a-statistic 
                        title="800米跑(秒)" 
                        :value="currentDetail?.test_result?.run_800m"
                        :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.run_800m, 'run_800m') }"
                        class="indicator-statistic"
                      />
                    </div>
                  </a-col>
                </a-row>
              </div>
            </div>
          </div>
          
          <div class="report-footer">
            <a-button type="primary" @click="closeDetail" class="close-detail-btn">关闭报告</a-button>
          </div>
        </div>
      </a-modal>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import { message, Empty } from 'ant-design-vue'
import { 
  EyeOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  MedicineBoxOutlined, 
  SafetyOutlined, 
  BulbOutlined, 
  BarChartOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  PlusOutlined,
  SearchOutlined,
  CloseOutlined,
  WarningOutlined
} from '@ant-design/icons-vue'
import axios from 'axios'
import dayjs from 'dayjs'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'HealthReport',
  components: {
    MedicineBoxOutlined,
    PlusOutlined,
    SearchOutlined,
    EyeOutlined,
    EditOutlined,
    DeleteOutlined,
    CloseOutlined,
    SafetyOutlined,
    BulbOutlined,
    BarChartOutlined,
    WarningOutlined,
    ExclamationCircleOutlined,
    InfoCircleOutlined
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const visible = ref(false)
    const detailVisible = ref(false)
    const confirmLoading = ref(false)
    const modalTitle = ref('生成体质报告')
    const reports = ref([])
    const testResults = ref([])
    const formRef = ref(null)
    const currentDetail = ref(null)
    const searchValue = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    
    const isAdmin = computed(() => store.getters.isAdmin)

    const formState = ref({
      id: null,
      test_result: null,
      overall_assessment: '',
      health_suggestions: ''
    })

    const rules = {
      test_result: [{ required: true, message: '请选择测试结果' }],
      overall_assessment: [{ required: true, message: '请输入总体评估' }],
      health_suggestions: [{ required: true, message: '请输入健康建议' }]
    }

    const columns = [
      {
        title: '学生姓名',
        dataIndex: 'student_name',
        key: 'student_name'
      },
      {
        title: '测试日期',
        dataIndex: 'test_date',
        key: 'test_date'
      },
      {
        title: '总分',
        dataIndex: 'total_score',
        key: 'total_score'
      },
      {
        title: '操作',
        key: 'action'
      }
    ]

    const formatDate = (date) => {
      return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : ''
    }

    const getScoreColor = (score) => {
      if (!score) return '#000000'
      if (score >= 90) return '#52c41a'
      if (score >= 80) return '#1890ff'
      if (score >= 70) return '#13c2c2'
      if (score >= 60) return '#faad14'
      return '#ff4d4f'
    }
    
    const getScoreTagColor = (score) => {
      if (!score) return ''
      if (score >= 90) return 'success'
      if (score >= 80) return 'processing'
      if (score >= 70) return 'cyan'
      if (score >= 60) return 'warning'
      return 'error'
    }

    const getIndicatorColor = (value, type) => {
      if (!value) return '#000000'
      
      // 根据不同指标类型返回不同颜色
      switch(type) {
        case 'vital_capacity': // 肺活量，越高越好
          if (value >= 4000) return '#52c41a'
          if (value >= 3000) return '#1890ff'
          if (value >= 2000) return '#faad14'
          return '#ff4d4f'
        
        case 'run_50m': // 50米跑，越低越好
          if (value <= 7) return '#52c41a'
          if (value <= 8) return '#1890ff'
          if (value <= 9) return '#faad14'
          return '#ff4d4f'
          
        case 'sit_and_reach': // 坐位体前屈，越高越好
          if (value >= 20) return '#52c41a'
          if (value >= 15) return '#1890ff'
          if (value >= 10) return '#faad14'
          return '#ff4d4f'
          
        case 'standing_jump': // 立定跳远，越高越好
          if (value >= 230) return '#52c41a'
          if (value >= 200) return '#1890ff'
          if (value >= 170) return '#faad14'
          return '#ff4d4f'
          
        case 'run_800m': // 800米跑，越低越好
          if (value <= 200) return '#52c41a'
          if (value <= 230) return '#1890ff'
          if (value <= 260) return '#faad14'
          return '#ff4d4f'
          
        default:
          return '#1890ff'
      }
    }

    const fetchReports = async (page = 1) => {
      loading.value = true
      try {
        // 启用控制台日志跟踪问题
        console.log('Fetching health reports...')
        
        // 获取健康报告数据
        const response = await axios.get('http://localhost:8000/api/health-reports/', {
          headers: { Authorization: `Bearer ${store.state.token}` },
          params: {
            page,
            page_size: pageSize.value,
            search: searchValue.value ? searchValue.value.trim() : undefined
          }
        })
        
        console.log('API Response:', response.data)
        
        let rawData = []
        
        // 检查是否是分页响应
        if (response.data && Array.isArray(response.data.results)) {
          rawData = response.data.results
          total.value = response.data.count || rawData.length
        } else if (Array.isArray(response.data)) {
          rawData = response.data
          total.value = rawData.length
        } else {
          console.error('Unexpected API response format:', response.data)
          rawData = []
          total.value = 0
          loading.value = false
          return
        }
        
        if (rawData.length === 0) {
          message.info('没有找到体质报告数据')
          reports.value = []
          loading.value = false
          return
        }
        
        console.log('原始健康报告数据:', rawData[0])
        
        // 创建一个映射来跟踪所有需要加载的测试结果 ID
        const testResultIdsToFetch = new Set()
        
        // 首先将原始数据复制到报告中，并收集所有需要加载的 ID
        const initialReports = rawData.map(report => {
          const transformedReport = { ...report }
          
          // 如果 test_result 是一个 ID，将其添加到要获取的列表中
          if (report.test_result && typeof report.test_result === 'number') {
            testResultIdsToFetch.add(report.test_result)
            transformedReport.test_result_id = report.test_result
            transformedReport.test_date = '加载中...'
            transformedReport.total_score = '加载中...'
            transformedReport.student_name = '加载中...'
          } else if (report.test_result && typeof report.test_result === 'object') {
            transformedReport.test_date = report.test_result.test_date 
              ? dayjs(report.test_result.test_date).format('YYYY-MM-DD') 
              : '未知'
            transformedReport.total_score = report.test_result.total_score ?? '未知'
            
            if (report.test_result.student) {
              if (typeof report.test_result.student === 'object') {
                transformedReport.student_name = report.test_result.student.name || '未知'
              } else {
                // 如果 student 是 ID，我们需要稍后获取
                transformedReport.student_id = report.test_result.student
                transformedReport.student_name = '加载中...'
              }
            } else {
              transformedReport.student_name = '未知'
            }
          } else {
            transformedReport.test_date = '未知'
            transformedReport.total_score = '未知'
            transformedReport.student_name = '未知'
          }
          
          return transformedReport
        })
        
        // 首先将初始数据显示到表格上
        reports.value = initialReports
        
        // 现在加载所有测试结果
        if (testResultIdsToFetch.size > 0) {
          console.log(`需要加载 ${testResultIdsToFetch.size} 个测试结果`)
          
          // 为每个测试结果 ID 单独回去服务器获取数据
          const testResultPromises = Array.from(testResultIdsToFetch).map(async testResultId => {
            try {
              const response = await axios.get(`http://localhost:8000/api/test-results/${testResultId}/`, {
                headers: { Authorization: `Bearer ${store.state.token}` }
              })
              return { id: testResultId, data: response.data }
            } catch (error) {
              console.error(`获取测试结果 ID ${testResultId} 失败:`, error)
              return { id: testResultId, data: null, error, errorStatus: error.response?.status || 'unknown' }
            }
          })
          
          // 等待所有测试结果加载完成
          const testResultsData = await Promise.all(testResultPromises)
          
          // 创建一个映射以快速访问测试结果
          const testResultsMap = {}
          const studentIdsToFetch = new Set()
          
          testResultsData.forEach(result => {
            if (result.data) {
              testResultsMap[result.id] = result.data
              
              // 如果还需要获取学生数据
              if (result.data.student && typeof result.data.student === 'number') {
                studentIdsToFetch.add(result.data.student)
              }
            } else {
              // 创建一个虚拟的测试结果对象，用于显示错误信息
              testResultsMap[result.id] = {
                id: result.id,
                test_date: null,
                total_score: result.errorStatus === 404 ? '数据缺失' : '加载错误',
                student: null,
                _error: true,
                _errorStatus: result.errorStatus,
                _errorMessage: result.errorStatus === 404 
                  ? '测试结果数据不存在或已被删除' 
                  : `加载测试结果失败 (${result.errorStatus})`
              }
            }
          })
          
          // 需要更新的学生数据
          let studentsMap = {}
          
          // 如果有学生 ID 需要加载
          if (studentIdsToFetch.size > 0) {
            console.log(`需要加载 ${studentIdsToFetch.size} 个学生信息`)
            
            const studentPromises = Array.from(studentIdsToFetch).map(async studentId => {
              try {
                const response = await axios.get(`http://localhost:8000/api/students/${studentId}/`, {
                  headers: { Authorization: `Bearer ${store.state.token}` }
                })
                return { id: studentId, data: response.data }
              } catch (error) {
                console.error(`获取学生 ID ${studentId} 失败:`, error)
                return { id: studentId, data: null, error }
              }
            })
            
            const studentsData = await Promise.all(studentPromises)
            
            // 构建学生映射
            studentsData.forEach(student => {
              if (student.data) {
                studentsMap[student.id] = student.data
              }
            })
          }
          
          // 现在更新所有报告中的测试结果和学生数据
          reports.value = reports.value.map(report => {
            // 如果有测试结果 ID，更新相关数据
            if (report.test_result_id && testResultsMap[report.test_result_id]) {
              const testResult = testResultsMap[report.test_result_id]
              
              // 在报告中存储完整的测试结果
              report.testResult = testResult

              // 如果测试结果是错误状态
              if (testResult._error) {
                report.test_date = '未知'
                report.total_score = testResult.total_score || '错误'
                report.student_name = '未知'
                report.errorStatus = testResult._errorStatus
                report.errorMessage = testResult._errorMessage
                // 添加可视化标记，使UI能够清晰显示错误状态
                report._hasError = true
                report._errorType = testResult._errorStatus === 404 ? 'missing' : 'error'
              } else {
                // 正常更新测试日期和总分
                report.test_date = testResult.test_date 
                  ? dayjs(testResult.test_date).format('YYYY-MM-DD') 
                  : '未知'
                report.total_score = testResult.total_score ?? '未知'
                
                // 更新学生信息
                if (testResult.student) {
                  if (typeof testResult.student === 'object') {
                    report.student_name = testResult.student.name || '未知'
                    report.student = testResult.student
                  } else if (typeof testResult.student === 'number' && studentsMap[testResult.student]) {
                    report.student_name = studentsMap[testResult.student].name || '未知'
                    report.student = studentsMap[testResult.student]
                  } else {
                    report.student_name = '未知'
                  }
                } else {
                  report.student_name = '未知'
                }
              }
            }
            
            return report
          })
          
          console.log('所有数据加载完成，更新后的报告:', reports.value[0])
        }
        
        console.log('Transformed data for table:', reports.value)

        if (reports.value.length === 0) {
          message.info('没有找到体质报告数据')
        }
      } catch (error) {
        console.error('获取体质报告错误:', error)
        if (error.isAxiosError) {
          console.log('Axios Error Config:', error.config)
          console.log('Error Response Status:', error.response?.status)
          console.log('Error Response Data:', error.response?.data)
          
          if (error.response?.status === 401) {
            message.error('认证失败，请重新登录')
            // 清除token并重定向到登录页
            store.commit('setToken', null)
            store.commit('setUser', null)
            router.push('/login')
          } else {
            message.error('获取体质报告失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
          }
        } else {
          message.error('获取体质报告失败')
        }
      } finally {
        loading.value = false
      }
    }

    const fetchTestResults = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/test-results/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        testResults.value = response.data.map(result => ({
          ...result,
          display_name: `${result.student.name} - ${dayjs(result.test_date).format('YYYY-MM-DD')}`
        }))
      } catch (error) {
        message.error('获取测试结果失败')
        console.error(error)
      }
    }

    const showModal = () => {
      modalTitle.value = '生成体质报告'
      formState.value = {
        id: null,
        test_result: null,
        overall_assessment: '',
        health_suggestions: ''
      }
      visible.value = true
    }

    const editReport = (record) => {
      modalTitle.value = '编辑体质报告'
      formState.value = { ...record }
      visible.value = true
    }

    const handleOk = async () => {
      try {
        await formRef.value.validate()
        confirmLoading.value = true
        
        if (formState.value.id) {
          // 更新报告
          await axios.put(
            `http://localhost:8000/api/health-reports/${formState.value.id}/`,
            formState.value,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('更新成功')
        } else {
          // 添加报告
          await axios.post(
            'http://localhost:8000/api/health-reports/',
            formState.value,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('添加成功')
        }
        
        visible.value = false
        fetchReports()
      } catch (error) {
        if (error.isAxiosError) {
          message.error('操作失败：' + (error.response?.data?.message || '未知错误'))
        }
        console.error(error)
      } finally {
        confirmLoading.value = false
      }
    }

    const handleCancel = () => {
      visible.value = false
    }

    const deleteReport = async (id) => {
      try {
        await axios.delete(`http://localhost:8000/api/health-reports/${id}/`, {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        message.success('删除成功')
        fetchReports()
      } catch (error) {
        message.error('删除失败')
        console.error(error)
      }
    }

    const viewReport = (record) => {
      console.log('Viewing report details:', record)
      try {
        if (!record) {
          console.error('记录不存在')
          message.error('无法查看详情：记录不存在')
          return
        }
        
        // 检查是否有错误信息
        if (record.errorStatus) {
          let errorMessage = '无法加载测试结果';
          let errorType = 'error';
          
          if (record.errorStatus === 404) {
            errorMessage = '测试结果数据不存在，可能已被删除';
            errorType = 'missing';
          } else if (record.errorMessage) {
            errorMessage = record.errorMessage;
          }
          
          // 显示警告但不阻止用户查看报告
          message.warning(errorMessage);
          
          // 仍然显示报告，但会标记测试结果数据有问题
          record.test_result = {
            _error: true,
            _errorType: errorType,
            _errorMessage: errorMessage,
            _errorStatus: record.errorStatus
          };
        }
        
        // 如果没有测试结果，创建一个空的测试结果对象
        if (!record.test_result) {
          record.test_result = {
            _error: true,
            _errorType: 'missing',
            _errorMessage: '测试结果数据不存在',
            _errorStatus: 404
          };
          message.warning('测试结果数据不存在');
        }
        
        currentDetail.value = record;
        console.log('Current detail set to:', currentDetail.value);
        detailVisible.value = true;
      } catch (error) {
        console.error('查看报告详情时出错:', error)
        message.error('无法查看详情')
      }
    }

    const closeDetail = () => {
      detailVisible.value = false
      currentDetail.value = null
    }

    const onSearch = (value) => {
      searchValue.value = value.trim()
      fetchReports()
    }

    const handlePageChange = (page) => {
      currentPage.value = page
      fetchReports(page)
    }

    const handlePageSizeChange = (current, size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchReports(1)
    }

    onMounted(() => {
      fetchReports()
      if (isAdmin.value) {
        fetchTestResults()
      }
    })

    return {
      loading,
      visible,
      detailVisible,
      confirmLoading,
      modalTitle,
      reports,
      testResults,
      formState,
      formRef,
      rules,
      columns,
      currentDetail,
      searchValue,
      isAdmin,
      formatDate,
      getScoreColor,
      getScoreTagColor,
      getIndicatorColor,
      showModal,
      editReport,
      handleOk,
      handleCancel,
      deleteReport,
      viewReport,
      closeDetail,
      onSearch,
      currentPage,
      pageSize,
      total,
      handlePageChange,
      handlePageSizeChange,
      Empty
    }
  }
})
</script>

<style scoped>
.health-report-container {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 16px;
}

.health-report {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1a1a1a;
}

.page-description {
  color: #666;
  font-size: 16px;
}

.table-actions-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.create-button {
  display: flex;
  align-items: center;
  border-radius: 6px;
}

.search-input {
  width: 250px;
  border-radius: 6px;
}

.table-container {
  border-radius: 8px;
  overflow: auto;
  max-height: 70vh;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.reports-table {
  background-color: #fff;
}

.action-button {
  padding: 0 8px;
  display: flex;
  align-items: center;
}

.score-tag {
  font-weight: 500;
  border-radius: 4px;
}

.score-tag.large {
  font-size: 16px;
  padding: 4px 12px;
  height: auto;
}

/* 报告详情样式 */
.detail-modal {
  border-radius: 12px;
  overflow: hidden;
}

.report-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 0 8px;
}

.report-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.report-title :deep(svg) {
  margin-right: 8px;
}

.close-button {
  border: none;
  background: transparent;
}

.divider-light {
  margin: 12px 0 24px;
}

.student-info-section {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.info-item {
  margin-bottom: 16px;
}

.info-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
  color: #1a1a1a;
}

.report-content-section {
  margin-bottom: 24px;
}

.section-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.section-title :deep(svg) {
  margin-right: 8px;
  color: #1890ff;
}

.section-content {
  color: #333;
  line-height: 1.6;
}

.indicator-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 16px;
  height: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.indicator-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.indicator-statistic :deep(.ant-statistic-title) {
  color: #666;
  font-size: 14px;
}

.indicator-statistic :deep(.ant-statistic-content) {
  font-size: 24px;
  font-weight: 600;
}

.report-footer {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.close-detail-btn {
  padding: 0 24px;
  height: 36px;
  font-size: 15px;
  border-radius: 6px;
}

/* 错误提示样式 */
.error-alert {
  margin-bottom: 24px;
}

.no-data-container {
  padding: 48px 0;
  text-align: center;
  background-color: #fafafa;
  border-radius: 8px;
}

/* 表单样式 */
.report-form {
  max-width: 650px;
  margin: 0 auto;
}

.form-select, .form-textarea {
  border-radius: 6px;
}

.form-textarea {
  resize: none;
}
</style>
