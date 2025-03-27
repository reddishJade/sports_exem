<template>
  <div class="student-list">
    <div class="table-operations" style="margin-bottom: 16px">
      <a-button type="primary" @click="showModal">添加学生</a-button>
    </div>

    <a-table :columns="columns" :data-source="students" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="editStudent(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除这个学生吗？"
              @confirm="deleteStudent(record.id)"
            >
              <a>删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

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
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="学号" name="student_id">
          <a-input v-model:value="formState.student_id" />
        </a-form-item>
        <a-form-item label="姓名" name="name">
          <a-input v-model:value="formState.name" />
        </a-form-item>
        <a-form-item label="班级" name="class_name">
          <a-input v-model:value="formState.class_name" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import { useStore } from 'vuex'

export default defineComponent({
  name: 'StudentList',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const visible = ref(false)
    const confirmLoading = ref(false)
    const modalTitle = ref('添加学生')
    const students = ref([])
    const formRef = ref(null)
    
    const formState = ref({
      id: null,
      student_id: '',
      name: '',
      class_name: ''
    })

    const rules = {
      student_id: [{ required: true, message: '请输入学号' }],
      name: [{ required: true, message: '请输入姓名' }],
      class_name: [{ required: true, message: '请输入班级' }]
    }

    const columns = [
      {
        title: '学号',
        dataIndex: 'student_id',
        key: 'student_id'
      },
      {
        title: '姓名',
        dataIndex: 'name',
        key: 'name'
      },
      {
        title: '班级',
        dataIndex: 'class_name',
        key: 'class_name'
      },
      {
        title: '操作',
        key: 'action'
      }
    ]

    const fetchStudents = async () => {
      loading.value = true
      try {
        const response = await axios.get('http://localhost:8000/api/students/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        students.value = response.data
      } catch (error) {
        message.error('获取学生列表失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const showModal = () => {
      modalTitle.value = '添加学生'
      formState.value = {
        id: null,
        student_id: '',
        name: '',
        class_name: ''
      }
      visible.value = true
    }

    const editStudent = (record) => {
      modalTitle.value = '编辑学生'
      formState.value = { ...record }
      visible.value = true
    }

    const handleOk = async () => {
      try {
        await formRef.value.validate()
        confirmLoading.value = true
        
        if (formState.value.id) {
          // 更新学生
          await axios.put(
            `http://localhost:8000/api/students/${formState.value.id}/`,
            formState.value,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('更新成功')
        } else {
          // 添加学生
          await axios.post(
            'http://localhost:8000/api/students/',
            formState.value,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('添加成功')
        }
        
        visible.value = false
        fetchStudents()
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

    const deleteStudent = async (id) => {
      try {
        await axios.delete(`http://localhost:8000/api/students/${id}/`, {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        message.success('删除成功')
        fetchStudents()
      } catch (error) {
        message.error('删除失败')
        console.error(error)
      }
    }

    onMounted(() => {
      fetchStudents()
    })

    return {
      loading,
      visible,
      confirmLoading,
      modalTitle,
      students,
      formState,
      formRef,
      rules,
      columns,
      showModal,
      editStudent,
      handleOk,
      handleCancel,
      deleteStudent
    }
  }
})
</script>

<style scoped>
.student-list {
  padding: 24px;
}
</style>
