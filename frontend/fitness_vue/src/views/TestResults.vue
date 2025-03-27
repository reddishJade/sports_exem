&lt;template>
  &lt;div class="test-results">
    &lt;a-card title="体测成绩查询" :bordered="false">
      &lt;a-tabs v-model:activeKey="activeTab">
        &lt;a-tab-pane key="list" tab="成绩列表">
          &lt;a-table :columns="columns" :data-source="testResults" :loading="loading">
            &lt;template #bodyCell="{ column, record }">
              &lt;template v-if="column.key === 'action'">
                &lt;a-space>
                  &lt;a @click="showDetail(record)">查看详情&lt;/a>
                  &lt;a v-if="!record.is_makeup && !record.is_passed" type="danger">
                    需要补考
                  &lt;/a>
                &lt;/a-space>
              &lt;/template>
              &lt;template v-else-if="column.key === 'total_score'">
                &lt;span :class="{ 'text-danger': record.total_score < 60 }">
                  {{ record.total_score }}
                &lt;/span>
              &lt;/template>
            &lt;/template>
          &lt;/a-table>
        &lt;/a-tab-pane>
        
        &lt;a-tab-pane key="chart" tab="成绩趋势">
          &lt;div ref="chartRef" style="height: 400px">&lt;/div>
        &lt;/a-tab-pane>
      &lt;/a-tabs>
    &lt;/a-card>

    &lt;a-modal
      v-model:open="detailVisible"
      title="成绩详情"
      width="800px"
      @ok="detailVisible = false"
    >
      &lt;a-descriptions bordered v-if="currentResult">
        &lt;a-descriptions-item label="测试计划">
          {{ currentResult.test_plan.title }}
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="测试时间">
          {{ formatDate(currentResult.test_date) }}
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="是否补考">
          {{ currentResult.is_makeup ? '是' : '否' }}
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="BMI指数">
          {{ currentResult.bmi }}
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="肺活量">
          {{ currentResult.vital_capacity }} ml
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="50米跑">
          {{ currentResult.run_50m }} 秒
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="坐位体前屈">
          {{ currentResult.sit_and_reach }} cm
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="立定跳远">
          {{ currentResult.standing_jump }} cm
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="800米跑">
          {{ currentResult.run_800m }} 秒
        &lt;/a-descriptions-item>
        &lt;a-descriptions-item label="总分">
          &lt;span :class="{ 'text-danger': currentResult.total_score < 60 }">
            {{ currentResult.total_score }}
          &lt;/span>
        &lt;/a-descriptions-item>
      &lt;/a-descriptions>

      &lt;template v-if="currentResult?.health_report">
        &lt;a-divider>健康报告&lt;/a-divider>
        &lt;a-descriptions bordered>
          &lt;a-descriptions-item label="总体评估" :span="3">
            {{ currentResult.health_report.overall_assessment }}
          &lt;/a-descriptions-item>
          &lt;a-descriptions-item label="健康建议" :span="3">
            {{ currentResult.health_report.health_suggestions }}
          &lt;/a-descriptions-item>
        &lt;/a-descriptions>
      &lt;/template>
    &lt;/a-modal>
  &lt;/div>
&lt;/template>

&lt;script setup>
import { ref, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { formatDate } from '@/utils/format'

const activeTab = ref('list')
const loading = ref(false)
const testResults = ref([])
const detailVisible = ref(false)
const currentResult = ref(null)
const chartRef = ref(null)
let chart = null

const columns = [
  {
    title: '测试计划',
    dataIndex: ['test_plan', 'title'],
    key: 'test_plan',
  },
  {
    title: '测试时间',
    dataIndex: 'test_date',
    key: 'test_date',
    customRender: ({ text }) => formatDate(text),
  },
  {
    title: '总分',
    dataIndex: 'total_score',
    key: 'total_score',
    sorter: (a, b) => a.total_score - b.total_score,
  },
  {
    title: '是否补考',
    dataIndex: 'is_makeup',
    key: 'is_makeup',
    customRender: ({ text }) => (text ? '是' : '否'),
  },
  {
    title: '操作',
    key: 'action',
  },
]

const fetchTestResults = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/test-results/')
    testResults.value = response.data
  } catch (error) {
    message.error('获取成绩数据失败')
  } finally {
    loading.value = false
  }
}

const showDetail = (record) => {
  currentResult.value = record
  detailVisible.value = true
}

const initChart = () => {
  if (chart) {
    chart.dispose()
  }
  
  chart = echarts.init(chartRef.value)
  const dates = testResults.value.map(result => formatDate(result.test_date))
  const scores = testResults.value.map(result => result.total_score)
  
  const option = {
    title: {
      text: '体测成绩趋势'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [{
      name: '总分',
      type: 'line',
      data: scores,
      markLine: {
        data: [
          {
            name: '及格线',
            yAxis: 60,
            lineStyle: {
              color: '#ff4d4f'
            }
          }
        ]
      }
    }]
  }
  
  chart.setOption(option)
}

watch(activeTab, (newVal) => {
  if (newVal === 'chart' && testResults.value.length > 0) {
    setTimeout(initChart, 0)
  }
})

watch(testResults, () => {
  if (activeTab.value === 'chart' && testResults.value.length > 0) {
    setTimeout(initChart, 0)
  }
}, { deep: true })

onMounted(() => {
  fetchTestResults()
})
&lt;/script>

&lt;style scoped>
.test-results {
  padding: 24px;
}

.text-danger {
  color: #ff4d4f;
}

:deep(.ant-card-head) {
  min-height: 48px;
}

:deep(.ant-descriptions) {
  margin-bottom: 24px;
}
&lt;/style>
