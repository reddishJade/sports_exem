<template>
  <div class="test-plan-detail">
    <a-page-header
      :title="testPlan.title || '测试计划详情'"
      :subtitle="testPlan.plan_code || ''" 
      @back="$router.go(-1)"
    />

    <a-card :loading="loading">
      <a-descriptions bordered>
        <a-descriptions-item label="测试计划名称" :span="3">
          {{ testPlan.title }}
        </a-descriptions-item>
        <a-descriptions-item label="测试代码">
          {{ testPlan.plan_code }}
        </a-descriptions-item>
        <a-descriptions-item label="测试日期">
          {{ testPlan.test_date }}
        </a-descriptions-item>
        <a-descriptions-item label="测试地点">
          {{ testPlan.location }}
        </a-descriptions-item>
        <a-descriptions-item label="参与班级" :span="3">
          {{ testPlan.participating_classes?.join(', ') || '未指定' }}
        </a-descriptions-item>
        <a-descriptions-item label="测试内容" :span="3">
          {{ testPlan.test_items?.join(', ') || '未指定' }}
        </a-descriptions-item>
        <a-descriptions-item label="详情说明" :span="3">
          {{ testPlan.description || '无详细说明' }}
        </a-descriptions-item>
        <a-descriptions-item label="创建人">
          {{ testPlan.created_by }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ testPlan.created_at }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="getStatusColor(testPlan.status)">
            {{ getStatusText(testPlan.status) }}
          </a-tag>
        </a-descriptions-item>
      </a-descriptions>

      <div class="action-buttons" style="margin-top: 24px; display: flex; justify-content: flex-end;">
        <a-button type="primary" style="margin-right: 8px;">
          查看测试结果
        </a-button>
        <a-button>
          返回列表
        </a-button>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const testPlanId = route.params.id
const testPlan = ref({})
const loading = ref(true)

const fetchTestPlan = async () => {
  loading.value = true
  try {
    // 在实际应用中，这里应该使用真实的API调用
    // 在此使用模拟数据
    const response = await axios.get(`/api/test-plans/${testPlanId}`.replace(/\/\//g, '/'))
    testPlan.value = response.data
  } catch (error) {
    console.error('获取测试计划失败:', error)
    message.error('获取测试计划详情失败，请稍后再试')
    // 使用模拟数据以展示页面
    testPlan.value = {
      id: testPlanId,
      title: '2023年秋季体能测试',
      plan_code: 'FALL2023-PE-001',
      test_date: '2023-10-15',
      location: '学校体育馆',
      participating_classes: ['高一(1)班', '高一(2)班', '高二(1)班'],
      test_items: ['50米跑', '立定跳远', '仰卧起坐', '800米跑', '坐位体前屈'],
      description: '本次测试为期末体能测试，请各班按照指定时间到达测试地点，携带学生证和运动装备。',
      created_by: '体育教师',
      created_at: '2023-09-01',
      status: 'active'
    }
  } finally {
    loading.value = false
  }
}

const getStatusColor = (status) => {
  const statusMap = {
    active: 'green',
    pending: 'orange',
    completed: 'blue',
    cancelled: 'red'
  }
  return statusMap[status] || 'default'
}

const getStatusText = (status) => {
  const textMap = {
    active: '进行中',
    pending: '未开始',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || '未知状态'
}

onMounted(() => {
  fetchTestPlan()
})
</script>

<style scoped>
.test-plan-detail {
  padding: 0 24px;
}
</style>
