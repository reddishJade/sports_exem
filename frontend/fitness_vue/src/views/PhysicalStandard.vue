<!--
  @description 体测标准视图组件 - 展示和管理体测评分标准
  @roles 所有用户查看，管理员编辑
  @features
    - 按性别分类展示体测标准
    - 管理员可设置和编辑标准
    - 支持不同年龄段和项目的标准设置
    - 提供标准对比和查询
-->
<template>
  <div class="physical-standard">
    <div class="table-operations" style="margin-bottom: 16px">
      <a-button type="primary" @click="showModal" v-if="isAdmin">设置体测标准</a-button>
    </div>

    <a-tabs v-model:activeKey="activeKey">
      <a-tab-pane key="male" tab="男生标准">
        <a-table :columns="columns" :data-source="maleStandards" :loading="loading">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action' && isAdmin">
              <a-space>
                <a @click="editStandard(record)">编辑</a>
                <a-divider type="vertical" />
                <a-popconfirm
                  title="确定要删除这个标准吗？"
                  @confirm="deleteStandard(record.id)"
                >
                  <a>删除</a>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-tab-pane>
      <a-tab-pane key="female" tab="女生标准">
        <a-table :columns="columns" :data-source="femaleStandards" :loading="loading">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action' && isAdmin">
              <a-space>
                <a @click="editStandard(record)">编辑</a>
                <a-divider type="vertical" />
                <a-popconfirm
                  title="确定要删除这个标准吗？"
                  @confirm="deleteStandard(record.id)"
                >
                  <a>删除</a>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>

    <a-modal
      :title="modalTitle"
      :open="visible"
      @ok="handleOk"
      @cancel="handleCancel"
      :confirmLoading="confirmLoading"
    >
      <a-form
        :model="formState"
        :rules="rules"
        ref="formRef"
        :label-col="{ span: 8 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="性别" name="gender">
          <a-select v-model:value="formState.gender">
            <a-select-option value="M">男</a-select-option>
            <a-select-option value="F">女</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="BMI范围" required>
          <a-input-group compact>
            <a-form-item name="bmi_min" style="margin-bottom: 0">
              <a-input-number
                v-model:value="formState.bmi_min"
                placeholder="最小值"
                style="width: 100px"
              />
            </a-form-item>
            <span style="padding: 0 8px">-</span>
            <a-form-item name="bmi_max" style="margin-bottom: 0">
              <a-input-number
                v-model:value="formState.bmi_max"
                placeholder="最大值"
                style="width: 100px"
              />
            </a-form-item>
          </a-input-group>
        </a-form-item>
        <a-form-item label="肺活量(优秀标准)" name="vital_capacity_excellent">
          <a-input-number v-model:value="formState.vital_capacity_excellent" style="width: 100%" />
        </a-form-item>
        <a-form-item label="50米跑(优秀标准)" name="run_50m_excellent">
          <a-input-number v-model:value="formState.run_50m_excellent" :precision="2" style="width: 100%" />
        </a-form-item>
        <a-form-item label="坐位体前屈(优秀标准)" name="sit_and_reach_excellent">
          <a-input-number v-model:value="formState.sit_and_reach_excellent" style="width: 100%" />
        </a-form-item>
        <a-form-item label="立定跳远(优秀标准)" name="standing_jump_excellent">
          <a-input-number v-model:value="formState.standing_jump_excellent" style="width: 100%" />
        </a-form-item>
        <a-form-item label="800米跑(优秀标准)" name="run_800m_excellent">
          <a-input-number v-model:value="formState.run_800m_excellent" style="width: 100%" />
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

export default defineComponent({
  name: 'PhysicalStandard',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const visible = ref(false)
    const confirmLoading = ref(false)
    const modalTitle = ref('添加体测标准')
    const activeKey = ref('male')
    const standards = ref([])
    const formRef = ref(null)
    
    const isAdmin = computed(() => store.getters.isAdmin)
    const maleStandards = computed(() => standards.value.filter(s => s.gender === 'M'))
    const femaleStandards = computed(() => standards.value.filter(s => s.gender === 'F'))

    const formState = ref({
      id: null,
      gender: 'M',
      bmi_min: null,
      bmi_max: null,
      vital_capacity_excellent: null,
      run_50m_excellent: null,
      sit_and_reach_excellent: null,
      standing_jump_excellent: null,
      run_800m_excellent: null
    })

    const rules = {
      gender: [{ required: true, message: '请选择性别' }],
      bmi_min: [{ required: true, message: '请输入BMI最小值' }],
      bmi_max: [{ required: true, message: '请输入BMI最大值' }],
      vital_capacity_excellent: [{ required: true, message: '请输入肺活量优秀标准' }],
      run_50m_excellent: [{ required: true, message: '请输入50米跑优秀标准' }],
      sit_and_reach_excellent: [{ required: true, message: '请输入体前屈优秀标准' }],
      standing_jump_excellent: [{ required: true, message: '请输入立定跳远优秀标准' }],
      run_800m_excellent: [{ required: true, message: '请输入800米跑优秀标准' }]
    }

    const columns = [
      {
        title: 'BMI范围',
        key: 'bmi_range',
        render: (_, record) => `${record.bmi_min} - ${record.bmi_max}`
      },
      {
        title: '肺活量(ml)',
        dataIndex: 'vital_capacity_excellent',
        key: 'vital_capacity_excellent'
      },
      {
        title: '50米跑(秒)',
        dataIndex: 'run_50m_excellent',
        key: 'run_50m_excellent'
      },
      {
        title: '坐位体前屈(cm)',
        dataIndex: 'sit_and_reach_excellent',
        key: 'sit_and_reach_excellent'
      },
      {
        title: '立定跳远(cm)',
        dataIndex: 'standing_jump_excellent',
        key: 'standing_jump_excellent'
      },
      {
        title: '800米跑(秒)',
        dataIndex: 'run_800m_excellent',
        key: 'run_800m_excellent'
      },
      {
        title: '操作',
        key: 'action'
      }
    ]

    const fetchStandards = async () => {
      loading.value = true
      try {
        const response = await axios.get('http://localhost:8000/api/physical-standards/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        standards.value = response.data
      } catch (error) {
        message.error('获取体测标准失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const showModal = () => {
      modalTitle.value = '添加体测标准'
      formState.value = {
        id: null,
        gender: activeKey.value === 'male' ? 'M' : 'F',
        bmi_min: null,
        bmi_max: null,
        vital_capacity_excellent: null,
        run_50m_excellent: null,
        sit_and_reach_excellent: null,
        standing_jump_excellent: null,
        run_800m_excellent: null
      }
      visible.value = true
    }

    const editStandard = (record) => {
      modalTitle.value = '编辑体测标准'
      formState.value = { ...record }
      visible.value = true
    }

    const handleOk = async () => {
      try {
        await formRef.value.validate()
        confirmLoading.value = true
        
        if (formState.value.id) {
          // 更新标准
          await axios.put(
            `http://localhost:8000/api/physical-standards/${formState.value.id}/`,
            formState.value,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('更新成功')
        } else {
          // 添加标准
          await axios.post(
            'http://localhost:8000/api/physical-standards/',
            formState.value,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('添加成功')
        }
        
        visible.value = false
        fetchStandards()
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

    const deleteStandard = async (id) => {
      try {
        await axios.delete(`http://localhost:8000/api/physical-standards/${id}/`, {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        message.success('删除成功')
        fetchStandards()
      } catch (error) {
        message.error('删除失败')
        console.error(error)
      }
    }

    onMounted(() => {
      fetchStandards()
    })

    return {
      loading,
      visible,
      confirmLoading,
      modalTitle,
      activeKey,
      standards,
      maleStandards,
      femaleStandards,
      formState,
      formRef,
      rules,
      columns,
      isAdmin,
      showModal,
      editStandard,
      handleOk,
      handleCancel,
      deleteStandard
    }
  }
})
</script>

<style scoped>
.physical-standard {
  padding: 24px;
}
</style>
