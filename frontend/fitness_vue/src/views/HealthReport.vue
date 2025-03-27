<template>
  <div class="health-report">
    <div class="table-operations" style="margin-bottom: 16px">
      <a-space>
        <a-button type="primary" @click="showModal" v-if="isAdmin">生成体质报告</a-button>
        <a-input-search
          v-model:value="searchValue"
          placeholder="搜索学生姓名"
          style="width: 200px"
          @search="onSearch"
        />
      </a-space>
    </div>

    <a-table :columns="columns" :data-source="reports" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="viewReport(record)">查看报告</a>
            <template v-if="isAdmin">
              <a-divider type="vertical" />
              <a @click="editReport(record)">编辑</a>
              <a-divider type="vertical" />
              <a-popconfirm
                title="确定要删除这个报告吗？"
                @confirm="deleteReport(record.id)"
              >
                <a>删除</a>
              </a-popconfirm>
            </template>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 报告编辑模态框 -->
    <a-modal
      :title="modalTitle"
      :open="visible"
      @ok="handleOk"
      @cancel="handleCancel"
      :confirmLoading="confirmLoading"
      width="800px"
    >
      <a-form
        :model="formState"
        :rules="rules"
        ref="formRef"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item label="测试结果" name="test_result" v-if="!formState.id">
          <a-select
            v-model:value="formState.test_result"
            show-search
            placeholder="选择测试结果"
            :options="testResults"
            :field-names="{ label: 'display_name', value: 'id' }"
          />
        </a-form-item>
        <a-form-item label="总体评估" name="overall_assessment">
          <a-textarea v-model:value="formState.overall_assessment" :rows="4" />
        </a-form-item>
        <a-form-item label="健康建议" name="health_suggestions">
          <a-textarea v-model:value="formState.health_suggestions" :rows="6" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 报告详情模态框 -->
    <a-modal
      title="体质评估报告"
      :open="detailVisible"
      @ok="closeDetail"
      @cancel="closeDetail"
      width="800px"
    >
      <a-descriptions bordered>
        <a-descriptions-item label="学生姓名" :span="3">
          {{ currentDetail?.test_result?.student?.name }}
        </a-descriptions-item>
        <a-descriptions-item label="测试日期" :span="3">
          {{ formatDate(currentDetail?.test_result?.test_date) }}
        </a-descriptions-item>
        <a-descriptions-item label="BMI指数" :span="1">
          {{ currentDetail?.test_result?.bmi }}
        </a-descriptions-item>
        <a-descriptions-item label="总分" :span="2">
          <span :style="{ color: getScoreColor(currentDetail?.test_result?.total_score) }">
            {{ currentDetail?.test_result?.total_score }}
          </span>
        </a-descriptions-item>
      </a-descriptions>

      <a-divider>详细评估</a-divider>
      
      <div class="report-section">
        <h3>总体评估</h3>
        <p>{{ currentDetail?.overall_assessment }}</p>
      </div>

      <div class="report-section">
        <h3>健康建议</h3>
        <p>{{ currentDetail?.health_suggestions }}</p>
      </div>

      <div class="report-section">
        <h3>各项指标详情</h3>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-statistic 
              title="肺活量(ml)" 
              :value="currentDetail?.test_result?.vital_capacity"
              :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.vital_capacity, 'vital_capacity') }"
            />
          </a-col>
          <a-col :span="8">
            <a-statistic 
              title="50米跑(秒)" 
              :value="currentDetail?.test_result?.run_50m"
              :precision="2"
              :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.run_50m, 'run_50m') }"
            />
          </a-col>
          <a-col :span="8">
            <a-statistic 
              title="坐位体前屈(cm)" 
              :value="currentDetail?.test_result?.sit_and_reach"
              :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.sit_and_reach, 'sit_and_reach') }"
            />
          </a-col>
        </a-row>
        <a-row :gutter="16" style="margin-top: 16px">
          <a-col :span="8">
            <a-statistic 
              title="立定跳远(cm)" 
              :value="currentDetail?.test_result?.standing_jump"
              :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.standing_jump, 'standing_jump') }"
            />
          </a-col>
          <a-col :span="8">
            <a-statistic 
              title="800米跑(秒)" 
              :value="currentDetail?.test_result?.run_800m"
              :value-style="{ color: getIndicatorColor(currentDetail?.test_result?.run_800m, 'run_800m') }"
            />
          </a-col>
        </a-row>
      </div>
    </a-modal>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import { useStore } from 'vuex'
import dayjs from 'dayjs'

export default defineComponent({
  name: 'HealthReport',
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
        key: 'total_score',
        render: (score) => ({
          props: {
            style: {
              color: getScoreColor(score)
            }
          },
          children: score
        })
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
      if (score >= 60) return '#1890ff'
      return '#ff4d4f'
    }

    const getIndicatorColor = (value, type) => {
      // 这里可以根据不同指标的标准来判断颜色
      return '#1890ff'
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
.health-report {
  padding: 24px;
}

.report-section {
  margin: 24px 0;
}

.report-section h3 {
  margin-bottom: 16px;
  color: #1890ff;
}

.report-section p {
  margin-bottom: 16px;
  line-height: 1.6;
}
</style>
