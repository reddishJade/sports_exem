<template>
  <div class="test-result-input">
    <a-card title="测试成绩录入" :bordered="false">
      <a-alert
        v-if="successMessage"
        message="成功"
        :description="successMessage"
        type="success"
        show-icon
        style="margin-bottom: 20px"
      />
      
      <a-form :model="formState" :rules="rules" ref="formRef" layout="vertical">
        <a-row :gutter="24">
          <a-col :xs="24" :md="12">
            <a-form-item name="testPlan" label="测试计划">
              <a-select
                v-model:value="formState.testPlan"
                placeholder="请选择测试计划"
                :loading="plansLoading"
                @change="handleTestPlanChange"
              >
                <a-select-option v-for="plan in testPlans" :key="plan.id" :value="plan.id">
                  {{ plan.title }} ({{ plan.test_date }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          
          <a-col :xs="24" :md="12">
            <a-form-item name="student" label="学生">
              <a-select
                v-model:value="formState.student"
                placeholder="请选择学生"
                :loading="studentsLoading"
                :disabled="!formState.testPlan"
              >
                <a-select-option v-for="student in students" :key="student.id" :value="student.id">
                  {{ student.user.username }} ({{ student.student_id }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-divider orientation="left">测试项目</a-divider>
        
        <a-row :gutter="24">
          <a-col :xs="24" :md="8">
            <a-form-item name="height" label="身高 (cm)">
              <a-input-number v-model:value="formState.height" style="width: 100%" :min="0" :max="250" />
            </a-form-item>
          </a-col>
          
          <a-col :xs="24" :md="8">
            <a-form-item name="weight" label="体重 (kg)">
              <a-input-number v-model:value="formState.weight" style="width: 100%" :min="0" :max="200" />
            </a-form-item>
          </a-col>
          
          <a-col :xs="24" :md="8">
            <a-form-item name="bmi" label="BMI">
              <a-input-number v-model:value="formState.bmi" style="width: 100%" :min="0" :max="50" disabled />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="24">
          <a-col :xs="24" :md="8">
            <a-form-item name="running" label="50米跑 (秒)">
              <a-input-number v-model:value="formState.running" style="width: 100%" :min="0" :precision="2" />
            </a-form-item>
          </a-col>
          
          <a-col :xs="24" :md="8">
            <a-form-item name="longJump" label="立定跳远 (cm)">
              <a-input-number v-model:value="formState.longJump" style="width: 100%" :min="0" />
            </a-form-item>
          </a-col>
          
          <a-col :xs="24" :md="8">
            <a-form-item name="sitUp" label="仰卧起坐 (次)">
              <a-input-number v-model:value="formState.sitUp" style="width: 100%" :min="0" />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="24">
          <a-col :xs="24" :md="12">
            <a-form-item name="endurance" label="1000米跑 (分:秒)">
              <a-input v-model:value="formState.endurance" placeholder="例如: 4:30" />
            </a-form-item>
          </a-col>
          
          <a-col :xs="24" :md="12">
            <a-form-item name="flexibility" label="坐位体前屈 (cm)">
              <a-input-number v-model:value="formState.flexibility" style="width: 100%" :min="-20" :max="30" />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-form-item>
          <a-button type="primary" @click="submitForm" :loading="submitting">保存成绩</a-button>
          <a-button style="margin-left: 10px" @click="resetForm">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import { useStore } from 'vuex'

const store = useStore()
const token = computed(() => store.state.token)

// 表单引用
const formRef = ref()
const plansLoading = ref(false)
const studentsLoading = ref(false)
const submitting = ref(false)
const successMessage = ref('')

// 数据列表
const testPlans = ref([])
const students = ref([])

// 表单数据
const formState = reactive({
  testPlan: undefined,
  student: undefined,
  height: undefined,
  weight: undefined,
  bmi: undefined,
  running: undefined,
  longJump: undefined,
  sitUp: undefined,
  endurance: undefined,
  flexibility: undefined,
})

// 表单验证规则
const rules = {
  testPlan: [{ required: true, message: '请选择测试计划' }],
  student: [{ required: true, message: '请选择学生' }],
  height: [{ required: true, message: '请输入身高' }],
  weight: [{ required: true, message: '请输入体重' }],
  running: [{ required: true, message: '请输入50米跑成绩' }],
  longJump: [{ required: true, message: '请输入立定跳远成绩' }],
  sitUp: [{ required: true, message: '请输入仰卧起坐成绩' }],
  endurance: [{ required: true, message: '请输入1000米跑成绩' }],
  flexibility: [{ required: true, message: '请输入坐位体前屈成绩' }],
}

// 监听身高体重变化自动计算BMI
watch([() => formState.height, () => formState.weight], ([height, weight]) => {
  if (height && weight) {
    const heightInMeters = height / 100
    formState.bmi = parseFloat((weight / (heightInMeters * heightInMeters)).toFixed(2))
  } else {
    formState.bmi = undefined
  }
})

// 获取测试计划列表
const fetchTestPlans = async () => {
  plansLoading.value = true
  try {
    const response = await axios.get('/api/test-plans/', {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    testPlans.value = response.data
  } catch (error) {
    console.error('获取测试计划失败:', error)
  } finally {
    plansLoading.value = false
  }
}

// 获取学生列表
const fetchStudents = async (testPlanId) => {
  if (!testPlanId) return
  
  studentsLoading.value = true
  try {
    const response = await axios.get(`/api/test-plans/${testPlanId}/students/`, {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    students.value = response.data
  } catch (error) {
    console.error('获取学生列表失败:', error)
  } finally {
    studentsLoading.value = false
  }
}

// 测试计划变更处理
const handleTestPlanChange = (value) => {
  formState.student = undefined
  fetchStudents(value)
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    try {
      const payload = {
        test_plan: formState.testPlan,
        student: formState.student,
        height: formState.height,
        weight: formState.weight,
        bmi: formState.bmi,
        running_50m: formState.running,
        long_jump: formState.longJump,
        sit_ups: formState.sitUp,
        endurance_run: formState.endurance,
        flexibility: formState.flexibility,
      }
      
      await axios.post('/api/test-results/', payload, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      
      successMessage.value = '成绩保存成功！'
      resetForm()
      
      // 3秒后清除成功消息
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
      
    } catch (error) {
      console.error('保存成绩失败:', error)
    } finally {
      submitting.value = false
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  formRef.value.resetFields()
  formState.bmi = undefined
}

// 生命周期钩子
onMounted(() => {
  fetchTestPlans()
})
</script>

<style scoped>
.test-result-input {
  padding: 24px;
}
</style>
