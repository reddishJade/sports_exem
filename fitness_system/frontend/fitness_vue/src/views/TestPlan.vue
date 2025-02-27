<template>
  <div class="test-plan">
    <div class="table-operations" style="margin-bottom: 16px">
      <a-button type="primary" @click="showModal" v-if="isAdmin">添加体测计划</a-button>
    </div>

    <a-table :columns="columns" :data-source="plans" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space v-if="isAdmin">
            <a @click="editPlan(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除这个体测计划吗？"
              @confirm="deletePlan(record.id)"
            >
              <a>删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      :title="modalTitle"
      :visible="visible"
      @ok="handleOk"
      @cancel="handleCancel"
      :confirmLoading="confirmLoading"
    >
      <a-form
        :model="formState"
        :rules="rules"
        ref="formRef"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="标题" name="title">
          <a-input v-model:value="formState.title" />
        </a-form-item>
        <a-form-item label="测试时间" name="test_date">
          <a-date-picker
            v-model:value="formState.test_date"
            show-time
            format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="地点" name="location">
          <a-input v-model:value="formState.location" />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="formState.description" :rows="4" />
        </a-form-item>
      </a-form>
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
  name: 'TestPlan',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const visible = ref(false)
    const confirmLoading = ref(false)
    const modalTitle = ref('添加体测计划')
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
        key: 'title'
      },
      {
        title: '测试时间',
        dataIndex: 'test_date',
        key: 'test_date',
        render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
      },
      {
        title: '地点',
        dataIndex: 'location',
        key: 'location'
      },
      {
        title: '操作',
        key: 'action'
      }
    ]

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
      formState,
      formRef,
      rules,
      columns,
      isAdmin,
      showModal,
      editPlan,
      handleOk,
      handleCancel,
      deletePlan
    }
  }
})
</script>

<style scoped>
.test-plan {
  padding: 24px;
}
</style>
