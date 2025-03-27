<template>
  <div class="test-result-detail">
    <a-page-header
      title="测试成绩详情"
      :subtitle="`学生: ${testResult.student_name || '未知'}`"
      @back="$router.go(-1)"
    />

    <a-row :gutter="16">
      <a-col :span="16">
        <a-card :loading="loading" class="result-card">
          <a-descriptions title="基本信息" bordered>
            <a-descriptions-item label="测试计划">
              {{ testResult.test_plan_title }}
            </a-descriptions-item>
            <a-descriptions-item label="测试日期">
              {{ testResult.test_date }}
            </a-descriptions-item>
            <a-descriptions-item label="学生姓名">
              {{ testResult.student_name }}
            </a-descriptions-item>
            <a-descriptions-item label="学号">
              {{ testResult.student_id }}
            </a-descriptions-item>
            <a-descriptions-item label="班级">
              {{ testResult.class_name }}
            </a-descriptions-item>
            <a-descriptions-item label="总分">
              <span :class="getScoreClass(testResult.total_score)">
                {{ testResult.total_score }}
              </span>
            </a-descriptions-item>
          </a-descriptions>

          <a-divider />

          <a-descriptions title="测试项目成绩" bordered>
            <a-descriptions-item label="身高(cm)">
              {{ testResult.height }}
            </a-descriptions-item>
            <a-descriptions-item label="体重(kg)">
              {{ testResult.weight }}
            </a-descriptions-item>
            <a-descriptions-item label="BMI">
              <span :class="getBMIClass(testResult.bmi)">{{ testResult.bmi }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="50米跑(秒)">
              <span :class="getItemScoreClass(testResult.running_score)">
                {{ testResult.running_50m }}
                <a-tag color="blue" v-if="testResult.running_score">{{ testResult.running_score }}分</a-tag>
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="立定跳远(cm)">
              <span :class="getItemScoreClass(testResult.long_jump_score)">
                {{ testResult.long_jump }}
                <a-tag color="blue" v-if="testResult.long_jump_score">{{ testResult.long_jump_score }}分</a-tag>
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="仰卧起坐(次)">
              <span :class="getItemScoreClass(testResult.sit_ups_score)">
                {{ testResult.sit_ups }}
                <a-tag color="blue" v-if="testResult.sit_ups_score">{{ testResult.sit_ups_score }}分</a-tag>
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="1000米/800米(分:秒)">
              <span :class="getItemScoreClass(testResult.endurance_run_score)">
                {{ testResult.endurance_run }}
                <a-tag color="blue" v-if="testResult.endurance_run_score">{{ testResult.endurance_run_score }}分</a-tag>
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="坐位体前屈(cm)">
              <span :class="getItemScoreClass(testResult.flexibility_score)">
                {{ testResult.flexibility }}
                <a-tag color="blue" v-if="testResult.flexibility_score">{{ testResult.flexibility_score }}分</a-tag>
              </span>
            </a-descriptions-item>
          </a-descriptions>

          <a-divider />

          <div class="comments-section">
            <h3>教师评语</h3>
            <div class="comment-box">
              {{ testResult.teacher_comments || '暂无评语' }}
            </div>
          </div>

          <div class="action-buttons" style="margin-top: 24px; display: flex; justify-content: flex-end;">
            <a-button type="primary" style="margin-right: 8px;">
              打印成绩单
            </a-button>
            <a-button @click="$router.go(-1)">
              返回
            </a-button>
          </div>
        </a-card>
      </a-col>
      
      <a-col :span="8">
        <a-card title="成绩分析" :loading="loading" class="analysis-card">
          <div class="score-badge">
            <div class="score-title">总分</div>
            <div class="score-value" :class="getScoreClass(testResult.total_score)">
              {{ testResult.total_score }}
            </div>
            <div class="score-text">{{ getScoreText(testResult.total_score) }}</div>
          </div>
          
          <a-divider />
          
          <div class="score-chart-container" ref="scoreChartRef" style="height: 300px;"></div>
          
          <a-divider />
          
          <h4>班级排名</h4>
          <div class="ranking-info">
            <div class="rank-number">{{ testResult.class_rank || 'N/A' }}</div>
            <div class="rank-text">班级排名 / {{ testResult.class_total || 'N/A' }}</div>
          </div>
          
          <a-progress 
            :percent="calculateRankPercentage(testResult.class_rank, testResult.class_total)" 
            :format="percent => `${testResult.class_rank} / ${testResult.class_total}`"
            :status="getRankStatus(testResult.class_rank, testResult.class_total)"
          />
          
          <a-divider />
          
          <h4>健康建议</h4>
          <p>{{ testResult.health_suggestions || '暂无健康建议' }}</p>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import axios from 'axios'
import * as echarts from 'echarts/core'
import { BarChart, RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必需的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  BarChart,
  RadarChart,
  CanvasRenderer
])

const route = useRoute()
const router = useRouter()
const testResultId = route.params.id
const testResult = ref({})
const loading = ref(true)
const scoreChartRef = ref(null)
let scoreChartInstance = null

const fetchTestResult = async () => {
  loading.value = true
  try {
    // 在实际应用中，这里应该使用真实的API调用
    // 在此使用模拟数据
    const response = await axios.get(`/api/test-results/${testResultId}`)
    testResult.value = response.data
  } catch (error) {
    console.error('获取测试结果失败:', error)
    message.error('获取测试结果详情失败，请稍后再试')
    // 使用模拟数据以展示页面
    testResult.value = {
      id: testResultId,
      test_plan_title: '2023年秋季体能测试',
      test_date: '2023-10-15',
      student_name: '张三',
      student_id: '2023001',
      class_name: '高二(1)班',
      height: 175,
      weight: 65,
      bmi: 21.2,
      running_50m: 7.2,
      running_score: 90,
      long_jump: 230,
      long_jump_score: 85,
      sit_ups: 48,
      sit_ups_score: 92,
      endurance_run: '3:45',
      endurance_run_score: 88,
      flexibility: 12.5,
      flexibility_score: 80,
      total_score: 87,
      teacher_comments: '总体表现良好，建议加强耐力训练，提高长跑能力。',
      health_suggestions: '身体各项指标正常，建议保持良好的运动习惯，每周至少进行3次30分钟以上的有氧运动。',
      class_rank: 5,
      class_total: 45
    }
  } finally {
    loading.value = false
    nextTick(() => {
      renderScoreChart()
    })
  }
}

const getScoreClass = (score) => {
  if (!score) return ''
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

const getScoreText = (score) => {
  if (!score) return '未评分'
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 60) return '及格'
  return '不及格'
}

const getBMIClass = (bmi) => {
  if (!bmi) return ''
  if (bmi < 18.5) return 'score-low'
  if (bmi <= 24.9) return 'score-good'
  if (bmi <= 29.9) return 'score-high'
  return 'score-very-high'
}

const getItemScoreClass = (score) => {
  if (!score) return ''
  if (score >= 90) return 'item-excellent'
  if (score >= 80) return 'item-good'
  if (score >= 60) return 'item-pass'
  return 'item-fail'
}

const calculateRankPercentage = (rank, total) => {
  if (!rank || !total || total === 0) return 0
  // 计算排名百分比（反向，因为排名越小越好）
  return 100 - (rank / total * 100)
}

const getRankStatus = (rank, total) => {
  if (!rank || !total) return 'normal'
  const percentage = calculateRankPercentage(rank, total)
  if (percentage >= 80) return 'success'
  if (percentage >= 60) return 'normal'
  return 'exception'
}

const renderScoreChart = () => {
  if (!testResult.value || !scoreChartRef.value) return
  
  if (scoreChartInstance) {
    scoreChartInstance.dispose()
  }
  
  scoreChartInstance = echarts.init(scoreChartRef.value)
  
  const option = {
    radar: {
      indicator: [
        { name: '50米跑', max: 100 },
        { name: '立定跳远', max: 100 },
        { name: '仰卧起坐', max: 100 },
        { name: '耐力跑', max: 100 },
        { name: '坐位体前屈', max: 100 }
      ]
    },
    series: [{
      name: '成绩得分',
      type: 'radar',
      data: [
        {
          value: [
            testResult.value.running_score || 0,
            testResult.value.long_jump_score || 0,
            testResult.value.sit_ups_score || 0,
            testResult.value.endurance_run_score || 0,
            testResult.value.flexibility_score || 0
          ],
          name: '个人得分',
          areaStyle: {
            color: 'rgba(0, 128, 255, 0.3)'
          },
          lineStyle: {
            color: '#0080ff',
            width: 2
          },
          itemStyle: {
            color: '#0080ff'
          }
        }
      ]
    }]
  }
  
  scoreChartInstance.setOption(option)
}

onMounted(() => {
  fetchTestResult()
  window.addEventListener('resize', () => {
    scoreChartInstance?.resize()
  })
})
</script>

<style scoped>
.test-result-detail {
  padding: 0 24px;
}

.result-card {
  margin-bottom: 20px;
}

.score-badge {
  text-align: center;
  padding: 20px 0;
}

.score-title {
  font-size: 16px;
  color: #666;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  margin: 10px 0;
}

.score-text {
  font-size: 18px;
  font-weight: 500;
}

.ranking-info {
  text-align: center;
  margin-bottom: 15px;
}

.rank-number {
  font-size: 36px;
  font-weight: bold;
  color: #1890ff;
}

.rank-text {
  font-size: 14px;
  color: #666;
}

.score-excellent {
  color: #52c41a;
}

.score-good {
  color: #1890ff;
}

.score-pass {
  color: #faad14;
}

.score-fail {
  color: #f5222d;
}

.score-low {
  color: #faad14;
}

.score-high {
  color: #faad14;
}

.score-very-high {
  color: #f5222d;
}

.item-excellent,
.item-good,
.item-pass,
.item-fail {
  font-weight: 500;
}

.item-excellent {
  color: #52c41a;
}

.item-good {
  color: #1890ff;
}

.item-pass {
  color: #faad14;
}

.item-fail {
  color: #f5222d;
}

.comments-section {
  margin: 16px 0;
}

.comment-box {
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 4px;
  min-height: 80px;
}
</style>
