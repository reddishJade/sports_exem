<!--
  @description 学生管理视图组件 - 管理学生基本信息
  @roles 管理员
  @features
    - 学生信息列表展示和管理
    - 支持添加、编辑和删除学生
    - 提供学生信息搜索和筛选
    - 查看学生详细信息和成绩
-->
<template>
  <div class="student-list-container">
    <div class="student-list">
      <div class="page-header">
        <h1 class="page-title">
          <team-outlined /> 学生管理
        </h1>
        <p class="page-description">管理学生基本信息</p>
      </div>

      <div class="table-actions-container">
        <div class="table-operations">
          <a-space>
            <a-button 
              type="primary" 
              @click="showModal" 
              class="create-button"
            >
              <user-add-outlined /> 添加学生
            </a-button>
            <a-input-search
              v-model:value="searchValue"
              placeholder="搜索学生姓名或学号"
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
          :data-source="filteredStudents" 
          :loading="loading"
          :pagination="{ 
            showSizeChanger: true, 
            pageSizeOptions: ['10', '20', '50'],
            showTotal: total => `共 ${total} 名学生`
          }"
          :rowKey="record => record.id"
          class="students-table"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-space>
                <a-button type="link" @click="editStudent(record)" class="action-button">
                  <edit-outlined /> 编辑
                </a-button>
                <a-divider type="vertical" />
                <a-popconfirm
                  title="确定要删除这个学生吗？"
                  @confirm="deleteStudent(record.id)"
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
            <template v-else-if="column.key === 'student_id'">
              <span class="student-id">{{ record.student_id }}</span>
            </template>
            <template v-else-if="column.key === 'name'">
              <span class="student-name">{{ record.name }}</span>
            </template>
            <template v-else-if="column.key === 'class_name'">
              <a-tag color="processing" class="class-tag">{{ record.class_name }}</a-tag>
            </template>
          </template>
        </a-table>
      </div>

      <a-modal
        :title="modalTitle"
        :open="visible"
        @ok="handleOk"
        @cancel="handleCancel"
        :confirmLoading="confirmLoading"
        class="student-modal"
        width="500px"
      >
        <a-form
          :model="formState"
          :rules="rules"
          ref="formRef"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 16 }"
          class="student-form"
        >
          <a-form-item label="学号" name="student_id">
            <a-input 
              v-model:value="formState.student_id" 
              placeholder="请输入学生学号"
              class="form-input"
              :maxLength="20"
            />
          </a-form-item>
          <a-form-item label="姓名" name="name">
            <a-input 
              v-model:value="formState.name" 
              placeholder="请输入学生姓名"
              class="form-input"
              :maxLength="50"
            />
          </a-form-item>
          <a-form-item label="班级" name="class_name">
            <a-input 
              v-model:value="formState.class_name" 
              placeholder="请输入学生班级"
              class="form-input"
              :maxLength="50"
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
import { 
  TeamOutlined, 
  UserAddOutlined, 
  SearchOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'

export default defineComponent({
  name: 'StudentList',
  components: {
    TeamOutlined,
    UserAddOutlined,
    SearchOutlined,
    EditOutlined,
    DeleteOutlined
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const visible = ref(false)
    const confirmLoading = ref(false)
    const modalTitle = ref('添加学生')
    const students = ref([])
    const formRef = ref(null)
    const searchValue = ref('')
    
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
        key: 'student_id',
        sorter: (a, b) => a.student_id.localeCompare(b.student_id)
      },
      {
        title: '姓名',
        dataIndex: 'name',
        key: 'name',
        sorter: (a, b) => a.name.localeCompare(b.name)
      },
      {
        title: '班级',
        dataIndex: 'class_name',
        key: 'class_name',
        sorter: (a, b) => a.class_name.localeCompare(b.class_name),
        filters: computed(() => {
          const classes = [...new Set(students.value.map(s => s.class_name))];
          return classes.map(c => ({ text: c, value: c }));
        }),
        onFilter: (value, record) => record.class_name === value
      },
      {
        title: '操作',
        key: 'action',
        width: '150px'
      }
    ]

    const filteredStudents = computed(() => {
      if (!searchValue.value) return students.value;
      
      const search = searchValue.value.toLowerCase();
      return students.value.filter(student => 
        student.name.toLowerCase().includes(search) || 
        student.student_id.toLowerCase().includes(search)
      );
    });

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

    const onSearch = (value) => {
      searchValue.value = value;
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
      filteredStudents,
      formState,
      formRef,
      rules,
      columns,
      searchValue,
      showModal,
      editStudent,
      handleOk,
      handleCancel,
      deleteStudent,
      onSearch
    }
  }
})
</script>

<style scoped>
.student-list-container {
  background-color: #f5f7fa;
  min-height: 100%;
  padding: 16px;
}

.student-list {
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

.students-table {
  background-color: #fff;
}

.action-button {
  padding: 0 8px;
  display: flex;
  align-items: center;
}

.student-id {
  font-family: 'Courier New', monospace;
  font-weight: 500;
  color: #606266;
}

.student-name {
  font-weight: 500;
  color: #303133;
}

.class-tag {
  font-weight: 500;
  border-radius: 4px;
}

/* 表单样式 */
.student-modal {
  border-radius: 12px;
  overflow: hidden;
}

.student-form {
  padding: 8px 16px;
}

.form-input {
  border-radius: 6px;
}
</style>
