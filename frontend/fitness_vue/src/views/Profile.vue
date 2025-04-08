<template>
  <div class="profile-container">
    <a-page-header
      title="个人信息"
      sub-title="查看和管理您的个人信息"
      :backIcon="false"
    />
    
    <a-row :gutter="24">
      <a-col :xs="24" :md="8">
        <a-card class="profile-card">
          <div class="profile-header">
            <a-avatar :size="80" :style="{ backgroundColor: avatarColor }">
              {{ usernameFirstChar }}
            </a-avatar>
            <div class="profile-name">
              <h2>{{ username }}</h2>
              <a-tag :color="userTypeColor">{{ userTypeText }}</a-tag>
            </div>
          </div>
          
          <a-divider />
          
          <div class="profile-info">
            <div class="info-item">
              <user-outlined />
              <span>{{ username }}</span>
            </div>
            <div class="info-item">
              <mail-outlined />
              <span>{{ userEmail || '未设置邮箱' }}</span>
            </div>
            <div class="info-item">
              <calendar-outlined />
              <span>注册时间: {{ formatDate(userJoinDate) }}</span>
            </div>
            <div class="info-item">
              <clock-circle-outlined />
              <span>上次登录: {{ formatDate(userLastLogin) }}</span>
            </div>
          </div>
          
          <a-divider />
          
          <a-button type="primary" block @click="showEditModal">
            编辑个人信息
          </a-button>
        </a-card>
      </a-col>
      
      <a-col :xs="24" :md="16">
        <a-card v-if="userType === 'student'" class="student-info-card" title="学生信息">
          <a-descriptions bordered>
            <a-descriptions-item label="学号" :span="3">
              {{ studentProfile?.student_id || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="班级" :span="3">
              {{ studentProfile?.class_name || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="专业" :span="3">
              {{ studentProfile?.major || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="年级" :span="3">
              {{ studentProfile?.grade || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="性别" :span="3">
              {{ studentProfile?.gender === 'M' ? '男' : studentProfile?.gender === 'F' ? '女' : '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="出生日期" :span="3">
              {{ formatDate(studentProfile?.birth_date) || '未设置' }}
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
        
        <a-card class="password-card" title="安全设置" style="margin-top: 24px;">
          <a-list>
            <a-list-item>
              <a-list-item-meta title="修改密码">
                <template #description>
                  定期修改密码可以提高账号安全性
                </template>
                <template #avatar>
                  <a-avatar style="background-color: #52c41a">
                    <lock-outlined />
                  </a-avatar>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a-button type="primary" @click="showPasswordModal">
                  修改密码
                </a-button>
              </template>
            </a-list-item>
          </a-list>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- 编辑个人信息弹窗 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑个人信息"
      @ok="handleEditSubmit"
      :confirmLoading="submitLoading"
    >
      <a-form :model="editForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="用户名">
          <a-input v-model:value="editForm.username" disabled />
        </a-form-item>
        <a-form-item label="邮箱">
          <a-input v-model:value="editForm.email" />
        </a-form-item>
        <template v-if="userType === 'student'">
          <a-form-item label="学号">
            <a-input v-model:value="editForm.student_id" disabled />
          </a-form-item>
          <a-form-item label="班级">
            <a-input v-model:value="editForm.class_name" />
          </a-form-item>
          <a-form-item label="专业">
            <a-input v-model:value="editForm.major" />
          </a-form-item>
          <a-form-item label="年级">
            <a-input v-model:value="editForm.grade" />
          </a-form-item>
          <a-form-item label="性别">
            <a-select v-model:value="editForm.gender">
              <a-select-option value="M">男</a-select-option>
              <a-select-option value="F">女</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="出生日期">
            <a-date-picker 
              v-model:value="editForm.birth_date" 
              style="width: 100%"
              :format="dateFormat"
            />
          </a-form-item>
        </template>
      </a-form>
    </a-modal>
    
    <!-- 修改密码弹窗 -->
    <a-modal
      v-model:open="passwordModalVisible"
      title="修改密码"
      @ok="handlePasswordSubmit"
      :confirmLoading="submitLoading"
    >
      <a-form :model="passwordForm" :label-col="{ span: 8 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="当前密码" name="currentPassword" :rules="[{ required: true, message: '请输入当前密码' }]">
          <a-input-password v-model:value="passwordForm.currentPassword" />
        </a-form-item>
        <a-form-item label="新密码" name="newPassword" :rules="[{ required: true, message: '请输入新密码' }]">
          <a-input-password v-model:value="passwordForm.newPassword" />
        </a-form-item>
        <a-form-item label="确认新密码" name="confirmPassword" :rules="[
          { required: true, message: '请确认新密码' },
          { validator: validateConfirmPassword }
        ]">
          <a-input-password v-model:value="passwordForm.confirmPassword" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useStore } from 'vuex'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import axios from 'axios'
import {
  UserOutlined,
  MailOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  LockOutlined
} from '@ant-design/icons-vue'

const store = useStore()
const dateFormat = 'YYYY-MM-DD'

// 用户基本信息
const username = computed(() => store.state.user?.username || '')
const userEmail = computed(() => store.state.user?.email || '')
const userType = computed(() => store.state.user?.user_type || '')
const userJoinDate = computed(() => store.state.user?.date_joined || '')
const userLastLogin = computed(() => store.state.user?.last_login || '')
const studentProfile = computed(() => store.state.user?.student_profile || null)

// 头像和用户类型显示
const usernameFirstChar = computed(() => {
  return username.value ? username.value.charAt(0).toUpperCase() : '?'
})

const avatarColor = computed(() => {
  const colors = ['#1890ff', '#52c41a', '#722ed1', '#faad14', '#eb2f96', '#fa541c']
  let hash = 0
  for (let i = 0; i < username.value.length; i++) {
    hash = username.value.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
})

const userTypeText = computed(() => {
  const typeMap = {
    'student': '学生',
    'parent': '家长',
    'admin': '管理员'
  }
  return typeMap[userType.value] || '未知'
})

const userTypeColor = computed(() => {
  const colorMap = {
    'student': 'blue',
    'parent': 'green',
    'admin': 'red'
  }
  return colorMap[userType.value] || 'default'
})

// 编辑个人信息
const editModalVisible = ref(false)
const submitLoading = ref(false)
const editForm = reactive({
  username: '',
  email: '',
  student_id: '',
  class_name: '',
  major: '',
  grade: '',
  gender: '',
  birth_date: null
})

const showEditModal = () => {
  editForm.username = username.value
  editForm.email = userEmail.value
  
  if (userType.value === 'student' && studentProfile.value) {
    editForm.student_id = studentProfile.value.student_id || ''
    editForm.class_name = studentProfile.value.class_name || ''
    editForm.major = studentProfile.value.major || ''
    editForm.grade = studentProfile.value.grade || ''
    editForm.gender = studentProfile.value.gender || ''
    editForm.birth_date = studentProfile.value.birth_date ? dayjs(studentProfile.value.birth_date) : null
  }
  
  editModalVisible.value = true
}

const handleEditSubmit = async () => {
  submitLoading.value = true
  try {
    const userData = {
      email: editForm.email
    }
    
    if (userType.value === 'student') {
      userData.student_profile = {
        class_name: editForm.class_name,
        major: editForm.major,
        grade: editForm.grade,
        gender: editForm.gender,
        birth_date: editForm.birth_date ? editForm.birth_date.format('YYYY-MM-DD') : null
      }
    }
    
    // users是正确的API端点，使用PATCH方法更新用户
    await axios.patch(`http://localhost:8000/api/users/${store.state.user.id}/`, userData, {
      headers: { 
        Authorization: `Bearer ${store.state.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    message.success('个人信息更新成功')
    editModalVisible.value = false
    
    // 更新本地状态
    store.dispatch('fetchCurrentUser')
  } catch (error) {
    console.error('更新个人信息失败:', error)
    message.error('更新个人信息失败，请稍后重试')
  } finally {
    submitLoading.value = false
  }
}

// 修改密码
const passwordModalVisible = ref(false)
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const showPasswordModal = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordModalVisible.value = true
}

const validateConfirmPassword = async (rule, value) => {
  if (value !== passwordForm.newPassword) {
    throw new Error('两次输入的密码不一致')
  }
}

const handlePasswordSubmit = async () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    message.error('两次输入的密码不一致')
    return
  }
  
  submitLoading.value = true
  try {
    // 对于密码修改，使用User视图集的自定义操作
    await axios.post(`http://localhost:8000/api/users/${store.state.user.id}/change_password/`, {
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    }, {
      headers: { 
        Authorization: `Bearer ${store.state.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    message.success('密码修改成功')
    passwordModalVisible.value = false
  } catch (error) {
    console.error('修改密码失败:', error)
    message.error('修改密码失败，请确认当前密码是否正确')
  } finally {
    submitLoading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return null
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN')
  } catch (e) {
    return dateString
  }
}
</script>

<style scoped>
.profile-container {
  padding: 24px;
}

.profile-card, .student-info-card, .password-card {
  margin-bottom: 24px;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.profile-name {
  margin-left: 16px;
}

.profile-name h2 {
  margin-bottom: 4px;
}

.profile-info {
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.info-item .anticon {
  margin-right: 12px;
  color: #1890ff;
}
</style>
