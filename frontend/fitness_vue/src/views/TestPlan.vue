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
              <a-space v-if="isAdmin">
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
  EnvironmentOutlined
} from '@ant-design/icons-vue'

export default defineComponent({
  name: 'TestPlan',
  components: {
    CalendarOutlined,
    PlusOutlined,
    SearchOutlined,
    EditOutlined,
    DeleteOutlined,
    EnvironmentOutlined
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const visible = ref(false)
    const confirmLoading = ref(false)
    const modalTitle = ref('添加体测计划')
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
        const response = await axios.get('http://localhost:8000/api/test-plans/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
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

    onMounted(() => {
      fetchPlans()
    })

    return {
      loading,
      visible,
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
      showModal,
      editPlan,
      handleOk,
      handleCancel,
      deletePlan,
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
</style>
