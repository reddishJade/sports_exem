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
            showSizeChanger: true, 
            pageSizeOptions: ['10', '20', '50'],
            showTotal: total => `共 ${total} 条记录`
          }"
          :rowKey="record => record.id"
          class="reports-table"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-space>
                <a-button type="link" @click="viewReport(record)" class="action-button">
                  <eye-outlined /> 查看
                </a-button>
                <template v-if="isAdmin">
                  <a-divider type="vertical" />
                  <a-button type="link" @click="editReport(record)" class="action-button">
                    <edit-outlined /> 编辑
                  </a-button>
                  <a-divider type="vertical" />
                  <a-popconfirm
                    title="确定要删除这个报告吗？"
                    @confirm="deleteReport(record.id)"
                    placement="topRight"
                    ok-text="确定"
                    cancel-text="取消"
                  >
                    <a-button type="link" danger class="action-button">
                      <delete-outlined /> 删除
                    </a-button>
                  </a-popconfirm>
                </template>
              </a-space>
            </template>
            <template v-else-if="column.key === 'total_score'">
              <a-tag :color="getScoreTagColor(record.test_result.total_score)" class="score-tag">
                {{ record.test_result.total_score }}
              </a-tag>
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
      >
        <div class="report-detail-header">
          <h2 class="report-title">
            <medicine-box-outlined /> 体质评估报告
          </h2>
          <a-button @click="closeDetail" class="close-button">
            <close-outlined />
          </a-button>
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
                <a-row :gutter="[24, 24]">
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
import { message } from 'ant-design-vue'
import axios from 'axios'
import { useStore } from 'vuex'
import dayjs from 'dayjs'
import { 
  MedicineBoxOutlined, 
  PlusOutlined, 
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  CloseOutlined,
  SafetyOutlined,
  BulbOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue'

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
    BarChartOutlined
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
        title: '学生',
        dataIndex: ['test_result', 'student', 'name'],
        key: 'student_name'
      },
      {
        title: '测试日期',
        dataIndex: ['test_result', 'test_date'],
        key: 'test_date',
        render: (text) => dayjs(text).format('YYYY-MM-DD')
      },
      {
        title: '总分',
        dataIndex: ['test_result', 'total_score'],
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

    const fetchReports = async () => {
      loading.value = true
      try {
        const response = await axios.get('http://localhost:8000/api/health-reports/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        reports.value = response.data
      } catch (error) {
        message.error('获取体质报告失败')
        console.error(error)
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
      currentDetail.value = record
      detailVisible.value = true
    }

    const closeDetail = () => {
      detailVisible.value = false
      currentDetail.value = null
    }

    const onSearch = (value) => {
      // 实现搜索功能
      console.log('search:', value)
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
      onSearch
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
  overflow: hidden;
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
