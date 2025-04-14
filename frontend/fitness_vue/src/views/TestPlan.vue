<!--
  @description 体测计划视图组件 - 管理体测活动的安排和计划
  @roles 所有用户查看，管理员编辑
  @features
    - 展示体测计划列表和时间安排
    - 管理员可添加、编辑和删除计划
    - 提供计划详情和参与人员查看
    - 支持计划状态管理和通知
-->
<template>
  <div class="test-plan-container">
    <div class="test-plan">
      <div class="page-header">
        <h1 class="page-title">
          <calendar-outlined /> 体测计划
        </h1>
        <p class="page-description">查看和管理体质测试安排</p>
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
              <plus-outlined /> 添加体测计划
            </a-button>
            <a-input-search
              v-model:value="searchValue"
              placeholder="搜索计划标题或地点"
              class="search-input"
              @search="onSearch"
            >
              <template #prefix>
                <search-outlined />
              </template>
            </a-input-search>
          </a-space>
        </div>
        <div class="filter-section" v-if="plans.length > 0">
          <a-radio-group v-model:value="timeFilter" button-style="solid" @change="handleFilterChange" style="margin-bottom: 16px">
            <a-radio-button value="all">全部</a-radio-button>
            <a-radio-button value="upcoming">即将到来</a-radio-button>
            <a-radio-button value="past">已结束</a-radio-button>
          </a-radio-group>
          
          <div v-if="timeFilter === 'upcoming'" class="day-filter">
            <div class="slider-label">筛选未来 <strong>{{ daysRange }}</strong> 天内的计划:</div>
            <div class="slider-container">
              <a-slider 
                v-model:value="daysRange" 
                :min="1" 
                :max="90" 
                :step="1"
                @change="handleDaysRangeChange"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="table-container">
        <a-table 
          :columns="columns" 
          :data-source="filteredPlans" 
          :loading="loading"
          :pagination="{ 
            showSizeChanger: true, 
            pageSizeOptions: ['10', '20', '50'],
            showTotal: total => `共 ${total} 条计划`
          }"
          :rowKey="record => record.id"
          class="plans-table"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-space>
                <a-button type="link" @click="viewPlanDetail(record)" class="action-button">
                  <eye-outlined /> 详情
                </a-button>
                <template v-if="isAdmin">
                  <a-divider type="vertical" />
                  <a-button type="link" @click="editPlan(record)" class="action-button">
                    <edit-outlined /> 编辑
                  </a-button>
                  <a-divider type="vertical" />
                  <a-popconfirm
                    title="确定要删除这个体测计划吗？"
                    @confirm="deletePlan(record.id)"
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
            <template v-else-if="column.key === 'title'">
              <div class="plan-title">
                {{ record.title }}
                <a-tag 
                  :color="isPlanUpcoming(record) ? 'processing' : 'default'" 
                  class="plan-status"
                >
                  {{ isPlanUpcoming(record) ? '即将到来' : '已结束' }}
                </a-tag>
              </div>
            </template>
            <template v-else-if="column.key === 'test_date'">
              <div class="date-display">
                <calendar-outlined class="date-icon" />
                <span>{{ formatDate(record.test_date) }}</span>
              </div>
            </template>
            <template v-else-if="column.key === 'location'">
              <div class="location-display">
                <environment-outlined class="location-icon" />
                <span>{{ record.location }}</span>
              </div>
            </template>
            <template v-else-if="column.key === 'description'">
              <a-tooltip :title="record.description" placement="topLeft">
                <div class="description-preview">
                  {{ truncateText(record.description, 30) }}
                </div>
              </a-tooltip>
            </template>
          </template>
          <template #expandedRowRender="{ record }">
            <div class="expanded-description">
              <div class="description-title">计划详情</div>
              <div class="description-content">{{ record.description || '暂无详细描述' }}</div>
            </div>
          </template>
        </a-table>
      </div>

      <a-modal
        :title="modalTitle"
        :open="visible"
        @ok="handleOk"
        @cancel="handleCancel"
        :confirmLoading="confirmLoading"
        class="plan-modal"
        width="600px"
      >
        <a-form
          :model="formState"
          :rules="rules"
          ref="formRef"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 16 }"
          class="plan-form"
        >
          <a-form-item label="标题" name="title">
            <a-input 
              v-model:value="formState.title" 
              placeholder="请输入体测计划标题"
              class="form-input"
              :maxLength="100"
            />
          </a-form-item>
          <a-form-item label="测试时间" name="test_date">
            <a-date-picker
              v-model:value="formState.test_date"
              show-time
              format="YYYY-MM-DD HH:mm:ss"
              class="form-date-picker"
              placeholder="选择测试日期时间"
            />
          </a-form-item>
          <a-form-item label="地点" name="location">
            <a-input 
              v-model:value="formState.location" 
              placeholder="请输入测试地点"
              class="form-input"
              :maxLength="100"
            />
          </a-form-item>
          <a-form-item label="描述" name="description">
            <a-textarea 
              v-model:value="formState.description" 
              :rows="4" 
              placeholder="请输入计划详细描述"
              class="form-textarea"
              :maxLength="500"
            />
          </a-form-item>
        </a-form>
      </a-modal>

      <!-- 详情模态框 -->
      <a-modal
        title="测试计划详情"
        :open="detailVisible"
        @cancel="closeDetail"
        :footer="null"
        width="700px"
        class="detail-modal"
      >
        <template v-if="currentPlan">
          <div class="detail-container">
            <div class="detail-header">
              <h2 class="detail-title">{{ currentPlan.title }}</h2>
              <a-tag 
                :color="isPlanUpcoming(currentPlan) ? 'processing' : 'default'"
                class="detail-status"
              >
                {{ isPlanUpcoming(currentPlan) ? '即将到来' : '已结束' }}
              </a-tag>
            </div>

            <div class="detail-info">
              <div class="info-item">
                <div class="info-label"><calendar-outlined /> 测试日期</div>
                <div class="info-value">{{ formatDate(currentPlan.test_date) }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label"><environment-outlined /> 测试地点</div>
                <div class="info-value">{{ currentPlan.location }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">计划类型</div>
                <div class="info-value">
                  <a-tag color="blue">{{ currentPlan.plan_type === 'regular' ? '常规测试' : '补考测试' }}</a-tag>
                </div>
              </div>
            </div>

            <div class="detail-description">
              <h3 class="section-title">详细说明</h3>
              <div class="description-content">
                {{ currentPlan.description || '暂无详细描述' }}
              </div>
            </div>
            
            <div class="detail-actions">
              <a-button @click="closeDetail">关闭</a-button>
              <a-button 
                type="primary" 
                @click="editPlan(currentPlan)"
                v-if="isAdmin"
                class="ml-2"
              >
                编辑计划
              </a-button>
            </div>
          </div>
        </template>
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
  CalendarOutlined, 
  PlusOutlined, 
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EnvironmentOutlined,
  EyeOutlined
} from '@ant-design/icons-vue'

export default defineComponent({
  name: 'TestPlan',
  components: {
    CalendarOutlined,
    PlusOutlined,
    SearchOutlined,
    EditOutlined,
    DeleteOutlined,
    EnvironmentOutlined,
    EyeOutlined
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const visible = ref(false)
    const detailVisible = ref(false)
    const confirmLoading = ref(false)
    const modalTitle = ref('添加体测计划')
    const currentPlan = ref(null)
    const searchValue = ref('')
    const timeFilter = ref('all')
    const daysRange = ref(30) // 默认显示30天内的计划
    const plans = ref([])
    const formRef = ref(null)
    
    const isAdmin = computed(() => store.getters.isAdmin)

    const formState = ref({
      id: null,
      title: '',
      test_date: null,
      location: '',
      description: ''
    })

    const rules = {
      title: [{ required: true, message: '请输入标题' }],
      test_date: [{ required: true, message: '请选择测试时间' }],
      location: [{ required: true, message: '请输入地点' }],
      description: [{ required: true, message: '请输入描述' }]
    }

    const columns = [
      {
        title: '标题',
        dataIndex: 'title',
        key: 'title',
        sorter: (a, b) => a.title.localeCompare(b.title)
      },
      {
        title: '测试时间',
        dataIndex: 'test_date',
        key: 'test_date',
        sorter: (a, b) => new Date(a.test_date) - new Date(b.test_date)
      },
      {
        title: '地点',
        dataIndex: 'location',
        key: 'location'
      },
      {
        title: '说明',
        dataIndex: 'description',
        key: 'description'
      },
      {
        title: '操作',
        key: 'action',
        width: '150px'
      }
    ]

    // 判断计划是否即将到来
    const isPlanUpcoming = (plan) => {
      return dayjs(plan.test_date).isAfter(dayjs());
    }

    // 格式化日期
    const formatDate = (date) => {
      return dayjs(date).format('YYYY-MM-DD HH:mm');
    }

    // 截断文本
    const truncateText = (text, maxLength) => {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substr(0, maxLength) + '...';
    }

    // 过滤计划
    const filteredPlans = computed(() => {
      let result = plans.value;
      const today = dayjs().startOf('day');
      
      if (!searchValue.value && timeFilter.value === 'all') {
        return plans.value
      }
      
      return plans.value.filter(plan => {
        // 搜索筛选
        const matchesSearch = !searchValue.value || 
          plan.title.toLowerCase().includes(searchValue.value.toLowerCase()) ||
          plan.location.toLowerCase().includes(searchValue.value.toLowerCase())
        
        // 时间筛选
        let matchesTimeFilter = true
        if (timeFilter.value !== 'all') {
          const planDate = dayjs(plan.test_date)
          
          if (timeFilter.value === 'upcoming') {
            // 判断是否在选定的天数范围内
            const futureDate = today.add(daysRange.value, 'day')
            matchesTimeFilter = (planDate.isAfter(today) && planDate.isBefore(futureDate)) || planDate.isSame(today, 'day')
          } else {
            // 过去的计划
            matchesTimeFilter = planDate.isBefore(today)
          }
        }
        
        return matchesSearch && matchesTimeFilter
      })
    })

    const handleFilterChange = () => {
      console.log('Filter changed:', timeFilter.value);
    }
    
    const handleDaysRangeChange = (value) => {
      console.log('Days range changed:', value);
      // 滑动条值改变后重新过滤计划
      daysRange.value = value;
    }

    const onSearch = (value) => {
      searchValue.value = value;
    }

    const fetchPlans = async () => {
      loading.value = true
      try {
        const params = {}
        
        // 如果不是管理员，只获取当前用户相关的测试计划
        if (!isAdmin.value) {
          // 家长或者学生用户只能看他们相关的计划
          if (store.state.userType === 'parent') {
            params.parent = true; // 家长用户只能查看与其子女相关的计划
          } else if (store.state.userType === 'student') {
            params.student = true; // 学生用户只能查看自己相关的计划
          }
        }
        
        const response = await axios.get('http://localhost:8000/api/test-plans/', {
          headers: { Authorization: `Bearer ${store.state.token}` },
          params: params
        })
        plans.value = response.data
      } catch (error) {
        message.error('获取体测计划失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const showModal = () => {
      modalTitle.value = '添加体测计划'
      formState.value = {
        id: null,
        title: '',
        test_date: null,
        location: '',
        description: ''
      }
      visible.value = true
    }

    const editPlan = (record) => {
      modalTitle.value = '编辑体测计划'
      formState.value = {
        ...record,
        test_date: dayjs(record.test_date)
      }
      visible.value = true
    }

    const handleOk = async () => {
      try {
        await formRef.value.validate()
        confirmLoading.value = true
        
        const data = {
          ...formState.value,
          test_date: formState.value.test_date.format('YYYY-MM-DD HH:mm:ss')
        }
        
        if (formState.value.id) {
          // 更新计划
          await axios.put(
            `http://localhost:8000/api/test-plans/${formState.value.id}/`,
            data,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('更新成功')
        } else {
          // 添加计划
          await axios.post(
            'http://localhost:8000/api/test-plans/',
            data,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('添加成功')
        }
        
        visible.value = false
        fetchPlans()
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

    const deletePlan = async (id) => {
      try {
        await axios.delete(`http://localhost:8000/api/test-plans/${id}/`, {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        message.success('删除成功')
        fetchPlans()
      } catch (error) {
        message.error('删除失败')
        console.error(error)
      }
    }
    
    // 查看测试计划详情
    const viewPlanDetail = (plan) => {
      currentPlan.value = plan
      detailVisible.value = true
    }
    
    // 关闭详情模态框
    const closeDetail = () => {
      detailVisible.value = false
      currentPlan.value = null
    }

    onMounted(() => {
      fetchPlans()
    })

    return {
      loading,
      visible,
      detailVisible,
      confirmLoading,
      modalTitle,
      plans,
      filteredPlans,
      formState,
      formRef,
      rules,
      columns,
      isAdmin,
      searchValue,
      timeFilter,
      daysRange,
      currentPlan,
      showModal,
      editPlan,
      handleOk,
      handleCancel,
      deletePlan,
      viewPlanDetail,
      closeDetail,
      formatDate,
      isPlanUpcoming,
      truncateText,
      onSearch,
      handleFilterChange,
      handleDaysRangeChange
    }
  }
})
</script>

<style scoped>
.test-plan-container {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 16px;
}

.test-plan {
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
  flex-wrap: wrap;
  gap: 16px;
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

.filter-section {
  transition: all 0.3s ease;
}

.table-container {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.plans-table {
  background-color: #fff;
}

.action-button {
  padding: 0 8px;
  display: flex;
  align-items: center;
}

.plan-title {
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.plan-status {
  font-size: 12px;
}

.date-display, .location-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-icon, .location-icon {
  color: #1890ff;
}

.description-preview {
  color: #606266;
  cursor: pointer;
}

.expanded-description {
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 6px;
}

.description-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.description-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-line;
}

/* 表单样式 */
.plan-modal {
  border-radius: 12px;
  overflow: hidden;
}

.plan-form {
  padding: 8px 16px;
}

.form-input, .form-date-picker, .form-textarea {
  border-radius: 6px;
  width: 100%;
}

.form-textarea {
  resize: none;
}

/* 滑动条样式 */
.day-filter {
  background-color: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
  margin-top: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.slider-label {
  margin-bottom: 12px;
  color: #555;
  font-size: 14px;
}

.slider-container {
  padding: 0 10px;
}

/* 详情模态框样式 */
.detail-modal {
  border-radius: 12px;
  overflow: hidden;
}

.detail-container {
  padding: 0 8px;
}

.detail-header {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.detail-title {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.detail-status {
  font-size: 13px;
}

.detail-info {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.info-item {
  flex: 1 1 240px;
  margin-bottom: 4px;
}

.info-label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.detail-description {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
  padding-left: 10px;
  border-left: 3px solid #1890ff;
}

.description-content {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  line-height: 1.6;
  white-space: pre-line;
  color: #606266;
  min-height: 120px;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.ml-2 {
  margin-left: 8px;
}
</style>
