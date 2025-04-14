<!--
  @description 体测计划详情视图组件 - 显示单个体测计划的详细信息
  @roles 所有用户
  @features
    - 展示体测计划的基本信息和详情
    - 显示参与体测的学生名单
    - 提供测试项目和要求说明
    - 管理员可编辑计划信息和状态
-->
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
        <a-button type="primary" style="margin-right: 8px;" @click="viewTestResults">
          查看测试结果
        </a-button>
        <a-button @click="router.push('/test-plans')">
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
    // 使用真实的 API 调用
    const response = await axios.get(`/api/test-plans/${testPlanId}`.replace(/\/\//g, '/'))
    testPlan.value = response.data
  } catch (error) {
    console.error('获取测试计划失败:', error)
    message.error('获取测试计划详情失败，请稍后再试')
    // 初始化空对象，而不是使用模拟数据
    testPlan.value = {
      id: testPlanId,
      title: '',
      plan_code: '',
      test_date: '',
      location: '',
      participating_classes: [],
      test_items: [],
      description: '',
      created_by: '',
      created_at: '',
      status: ''
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

// 查看测试结果
const viewTestResults = () => {
  // 导航到测试结果报表页面，并传递当前测试计划ID
  router.push({
    path: '/test-result-reports',
    query: { plan_id: testPlanId }
  })
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
