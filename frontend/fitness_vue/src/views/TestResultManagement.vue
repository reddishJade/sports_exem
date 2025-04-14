<!--
  @description 管理员视角的测试结果管理组件
  @roles 管理员 - 录入、编辑、删除测试成绩
-->
<template>
  <div class="test-result">
    <div class="page-header">
      <div class="header-title">
        <file-text-outlined />
        <span>测试结果管理</span>
      </div>
      <p class="header-description">录入、编辑和管理学生体测成绩</p>
    </div>
    
    <div class="table-operations" style="margin-bottom: 16px">
      <a-space>
        <a-button type="primary" @click="showModal" v-if="isAdmin">
          <plus-outlined />
          录入成绩
        </a-button>
        <a-button @click="showMakeupList" v-if="isAdmin">
          <calendar-outlined />
          补考名单
        </a-button>
      </a-space>
    </div>

    <div v-for="result in results" :key="result.id" class="result-card" style="margin-bottom: 24px">
      <a-card class="animated-card">
        <template #title>
          <span>
            {{ result.student.name }} - {{ result.test_plan.title }}
            <span :style="{ color: result.total_score < 60 ? '#ff4d4f' : '#52c41a', marginLeft: '8px' }">
              总分: {{ result.total_score }}
            </span>
          </span>
        </template>
        <template #extra>
          <a-space>
            <a @click="result.expanded = !result.expanded" class="action-link">
              <eye-outlined />
              {{ result.expanded ? '收起' : '展开' }}
            </a>
            <a @click="viewDetail(result)" class="action-link">
              <solution-outlined />
              查看详情
            </a>
            <template v-if="isAdmin">
              <a-divider type="vertical" />
              <a @click="editResult(result)" class="action-link edit-link">
                <edit-outlined />
                编辑
              </a>
              <a-divider type="vertical" />
              <a-popconfirm
                title="确定要删除这个成绩记录吗？"
                @confirm="deleteResult(result.id)"
                okText="确定"
                cancelText="取消"
              >
                <a class="action-link delete-link">
                  <delete-outlined />
                  删除
                </a>
              </a-popconfirm>
            </template>
          </a-space>
        </template>

        <div v-if="result.expanded">
          <a-descriptions :column="4" class="result-descriptions">
            <a-descriptions-item label="BMI指数">{{ result.bmi }}</a-descriptions-item>
            <a-descriptions-item label="肺活量">{{ result.vital_capacity }}ml</a-descriptions-item>
            <a-descriptions-item label="50米跑">{{ result.run_50m }}秒</a-descriptions-item>
            <a-descriptions-item label="坐位体前屈">{{ result.sit_and_reach }}cm</a-descriptions-item>
            <a-descriptions-item label="立定跳远">{{ result.standing_jump }}cm</a-descriptions-item>
            <a-descriptions-item label="800米跑">{{ result.run_800m }}秒</a-descriptions-item>
          </a-descriptions>
  
          <!-- 评论区 -->
          <div style="margin-top: 16px" v-if="store.state.user?.user_type === 'student'">
            <a-divider>评论区</a-divider>
            <a-list
              :data-source="result.comments"
              :loading="result.commentsLoading"
              item-layout="horizontal"
              class="comments-list"
            >
              <template #header>
                <a-input-group compact>
                  <a-input
                    :value="result.newComment || ''"
                    @update:value="val => result && (result.newComment = val)"
                    placeholder="写下你的评论..."
                    style="width: calc(100% - 80px)"
                    @keyup.enter="() => result && submitComment(result)"
                  />
                  <a-button 
                    type="primary" 
                    @click="() => submitComment(result)" 
                    :loading="result.commentsLoading"
                  >发送</a-button>
                </a-input-group>
              </template>
              <template #renderItem="{ item }">
                <a-list-item v-if="item && item.student" class="comment-item">
                  <a-list-item-meta
                    :title="item.student?.name || '未知用户'"
                    :description="item.content"
                  >
                    <template #avatar>
                      <a-avatar>{{ item.student?.name?.[0] || '?' }}</a-avatar>
                    </template>
                  </a-list-item-meta>
                  <template #extra>
                    <a-tag :color="item.is_approved ? 'green' : 'orange'">
                      {{ item.is_approved ? '已审核' : '待审核' }}
                    </a-tag>
                  </template>
                </a-list-item>
              </template>
              <template #empty>
                <a-empty v-if="result.commentError" description="加载评论失败" />
                <a-empty v-else description="暂无评论" />
              </template>
            </a-list>
          </div>
        </div>
        <div v-else class="collapsed-hint">
          <a-button type="link" @click="result.expanded = true">点击展开查看详细信息和评论</a-button>
        </div>
      </a-card>
    </div>

    <!-- 成绩录入/编辑模态框 -->
    <a-modal
      :title="modalTitle"
      :open="visible"
      @ok="handleOk"
      @cancel="handleCancel"
      :confirmLoading="confirmLoading"
      width="800px"
      class="result-modal"
    >
      <a-form
        :model="formState"
        :rules="rules"
        ref="formRef"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
        class="result-form"
      >
        <a-form-item label="学生" name="student" v-if="!formState.id">
          <a-select
            v-model:value="formState.student"
            show-search
            placeholder="请选择学生"
            :options="students"
            :field-names="{ label: 'name', value: 'id' }"
            class="form-select"
          />
        </a-form-item>
        <a-form-item label="测试计划" name="test_plan" v-if="!formState.id">
          <a-select
            v-model:value="formState.test_plan"
            show-search
            placeholder="请选择测试计划"
            :options="testPlans"
            :field-names="{ label: 'title', value: 'id' }"
            class="form-select"
          />
        </a-form-item>
        <a-form-item label="BMI指数" name="bmi">
          <a-input-number v-model:value="formState.bmi" :min="10" :max="40" style="width: 100%" class="form-input" />
        </a-form-item>
        <a-form-item label="肺活量(ml)" name="vital_capacity">
          <a-input-number v-model:value="formState.vital_capacity" :min="0" :max="10000" style="width: 100%" class="form-input" />
        </a-form-item>
        <a-form-item label="50米跑(秒)" name="run_50m">
          <a-input-number v-model:value="formState.run_50m" :min="0" :max="60" :precision="2" style="width: 100%" class="form-input" />
        </a-form-item>
        <a-form-item label="坐位体前屈(cm)" name="sit_and_reach">
          <a-input-number v-model:value="formState.sit_and_reach" :min="-20" :max="40" style="width: 100%" class="form-input" />
        </a-form-item>
        <a-form-item label="立定跳远(cm)" name="standing_jump">
          <a-input-number v-model:value="formState.standing_jump" :min="0" :max="400" style="width: 100%" class="form-input" />
        </a-form-item>
        <a-form-item label="800米跑(秒)" name="run_800m">
          <a-input-number v-model:value="formState.run_800m" :min="0" :max="1000" style="width: 100%" class="form-input" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 详情模态框 -->
    <a-modal
      :open="detailVisible"
      title="成绩详情"
      width="800px"
      @ok="handleDetailOk"
      @cancel="handleDetailCancel"
      class="detail-modal"
    >
      <a-descriptions bordered>
        <a-descriptions-item label="学生姓名" :span="3">
          {{ currentDetail?.student?.name }}
        </a-descriptions-item>
        <a-descriptions-item label="测试计划" :span="3">
          {{ currentDetail?.test_plan?.title }}
        </a-descriptions-item>
        <a-descriptions-item label="测试日期" :span="3">
          {{ formatDate(currentDetail?.test_date) }}
        </a-descriptions-item>
        <a-descriptions-item label="总分" :span="3">
          <span :style="{ color: currentDetail?.total_score < 60 ? '#ff4d4f' : '#52c41a' }">
            {{ currentDetail?.total_score }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="BMI指数">
          {{ currentDetail?.bmi }}
        </a-descriptions-item>
        <a-descriptions-item label="肺活量">
          {{ currentDetail?.vital_capacity }}ml
        </a-descriptions-item>
        <a-descriptions-item label="50米跑">
          {{ currentDetail?.run_50m }}秒
        </a-descriptions-item>
        <a-descriptions-item label="坐位体前屈">
          {{ currentDetail?.sit_and_reach }}cm
        </a-descriptions-item>
        <a-descriptions-item label="立定跳远">
          {{ currentDetail?.standing_jump }}cm
        </a-descriptions-item>
        <a-descriptions-item label="800米跑">
          {{ currentDetail?.run_800m }}秒
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>

    <!-- 补考名单模态框 -->
    <a-modal
      :open="makeupListVisible"
      title="补考名单"
      width="800px"
      @ok="makeupListVisible = false"
      @cancel="makeupListVisible = false"
      class="makeup-modal"
    >
      <a-table
        :columns="makeupColumns"
        :data-source="makeupList"
        :loading="makeupLoading"
        rowKey="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a @click="notifyStudent(record.id)">通知学生</a>
          </template>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { FileTextOutlined, EyeOutlined, SolutionOutlined, EditOutlined, DeleteOutlined, PlusOutlined, CalendarOutlined } from '@ant-design/icons-vue'
import { useStore } from 'vuex'
import axios from 'axios'
import moment from 'moment'

export default defineComponent({
  name: 'TestResultManagement',
  components: {
    FileTextOutlined,
    EyeOutlined,
    SolutionOutlined,
    EditOutlined,
    DeleteOutlined,
    PlusOutlined,
    CalendarOutlined
  },
  setup() {
    const store = useStore()
    const results = ref([])
    const loading = ref(false)
    const visible = ref(false)
    const confirmLoading = ref(false)
    const detailVisible = ref(false)
    const currentDetail = ref(null)
    const makeupListVisible = ref(false)
    const makeupList = ref([])
    const makeupLoading = ref(false)
    const formRef = ref(null)
    const students = ref([])
    const testPlans = ref([])
    
    const isAdmin = computed(() => {
      return store.state.user && store.state.user.user_type === 'admin'
    })
    
    const modalTitle = computed(() => {
      return formState.value.id ? '编辑成绩' : '录入成绩'
    })

    const formState = ref({
      id: null,
      student: null,
      test_plan: null,
      test_date: moment().format('YYYY-MM-DD'),
      bmi: 0,
      vital_capacity: 0,
      run_50m: 0,
      sit_and_reach: 0,
      standing_jump: 0,
      run_800m: 0
    })

    const rules = {
      student: [{ required: true, message: '请选择学生' }],
      test_plan: [{ required: true, message: '请选择测试计划' }],
      bmi: [{ required: true, message: '请输入BMI指数' }],
      vital_capacity: [{ required: true, message: '请输入肺活量' }],
      run_50m: [{ required: true, message: '请输入50米跑成绩' }],
      sit_and_reach: [{ required: true, message: '请输入坐位体前屈成绩' }],
      standing_jump: [{ required: true, message: '请输入立定跳远成绩' }],
      run_800m: [{ required: true, message: '请输入800米跑成绩' }]
    }

    const makeupColumns = [
      {
        title: '学生',
        dataIndex: ['student', 'name'],
        key: 'student'
      },
      {
        title: '测试计划',
        dataIndex: ['test_plan', 'title'],
        key: 'test_plan'
      },
      {
        title: '总分',
        dataIndex: 'total_score',
        key: 'total_score'
      },
      {
        title: '操作',
        key: 'action'
      }
    ]

    const resetForm = () => {
      formState.value = {
        id: null,
        student: null,
        test_plan: null,
        test_date: moment().format('YYYY-MM-DD'),
        bmi: 0,
        vital_capacity: 0,
        run_50m: 0,
        sit_and_reach: 0,
        standing_jump: 0,
        run_800m: 0
      }
      if (formRef.value) {
        formRef.value.resetFields()
      }
    }

    const showModal = () => {
      resetForm()
      visible.value = true
      fetchStudents()
      fetchTestPlans()
    }

    const handleOk = async () => {
      try {
        await formRef.value.validate()
        confirmLoading.value = true
        
        if (formState.value.id) {
          // 更新现有成绩
          await axios.put(`/api/test-results/${formState.value.id}/`, formState.value)
          message.success('成绩更新成功')
        } else {
          // 创建新成绩
          await axios.post('/api/test-results/', formState.value)
          message.success('成绩录入成功')
        }
        
        visible.value = false
        confirmLoading.value = false
        fetchResults()
      } catch (error) {
        message.error('表单验证失败，请检查输入')
        confirmLoading.value = false
      }
    }

    const handleCancel = () => {
      visible.value = false
      resetForm()
    }

    const editResult = (result) => {
      formState.value = { ...result }
      if (typeof formState.value.student === 'object') {
        formState.value.student = formState.value.student.id
      }
      if (typeof formState.value.test_plan === 'object') {
        formState.value.test_plan = formState.value.test_plan.id
      }
      visible.value = true
      fetchStudents()
      fetchTestPlans()
    }

    const deleteResult = async (id) => {
      try {
        await axios.delete(`/api/test-results/${id}/`)
        message.success('成绩删除成功')
        fetchResults()
      } catch (error) {
        message.error('删除失败，请稍后再试')
      }
    }

    const viewDetail = (result) => {
      currentDetail.value = { ...result }
      detailVisible.value = true
    }

    const handleDetailOk = () => {
      detailVisible.value = false
    }

    const handleDetailCancel = () => {
      detailVisible.value = false
    }

    const showMakeupList = () => {
      makeupListVisible.value = true
      fetchMakeupList()
    }

    const notifyStudent = async (id) => {
      try {
        await axios.post(`/api/test-results/${id}/notify/`)
        message.success('通知已发送')
      } catch (error) {
        message.error('发送通知失败，请稍后再试')
      }
    }

    const fetchResults = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/test-results/')
        // 给每个结果添加expanded属性
        results.value = response.data.map(result => ({
          ...result,
          expanded: false,
          comments: [],
          commentsLoading: false,
          commentError: false,
          newComment: ''
        }))
        loading.value = false
      } catch (error) {
        message.error('获取成绩列表失败')
        loading.value = false
      }
    }

    const fetchStudents = async () => {
      try {
        const response = await axios.get('/api/students/')
        students.value = response.data
      } catch (error) {
        message.error('获取学生列表失败')
      }
    }

    const fetchTestPlans = async () => {
      try {
        const response = await axios.get('/api/test-plans/')
        testPlans.value = response.data
      } catch (error) {
        message.error('获取测试计划列表失败')
      }
    }

    const fetchMakeupList = async () => {
      makeupLoading.value = true
      try {
        const response = await axios.get('/api/test-results/makeup/')
        makeupList.value = response.data
        makeupLoading.value = false
      } catch (error) {
        message.error('获取补考名单失败')
        makeupLoading.value = false
      }
    }

    const fetchComments = async (result) => {
      if (!result) return
      result.commentsLoading = true
      try {
        const response = await axios.get(`/api/test-results/${result.id}/comments/`)
        result.comments = response.data
        result.commentError = false
        result.commentsLoading = false
      } catch (error) {
        result.commentError = true
        result.commentsLoading = false
      }
    }

    const submitComment = async (result) => {
      if (!result || !result.newComment) return
      result.commentsLoading = true
      try {
        await axios.post(`/api/test-results/${result.id}/comments/`, {
          content: result.newComment
        })
        result.newComment = ''
        await fetchComments(result)
      } catch (error) {
        message.error('评论发送失败')
        result.commentsLoading = false
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return moment(dateStr).format('YYYY-MM-DD')
    }

    // 监听expanded属性变化，加载评论
    const watchResultExpanded = () => {
      const resultsCopy = [...results.value]
      for (const result of resultsCopy) {
        if (result.expanded) {
          fetchComments(result)
        }
      }
    }

    onMounted(() => {
      fetchResults()
    })

    return {
      store,
      isAdmin,
      results,
      loading,
      visible,
      confirmLoading,
      formState,
      formRef,
      modalTitle,
      rules,
      students,
      testPlans,
      detailVisible,
      currentDetail,
      makeupListVisible,
      makeupList,
      makeupLoading,
      makeupColumns,
      showModal,
      handleOk,
      handleCancel,
      editResult,
      deleteResult,
      viewDetail,
      handleDetailOk,
      handleDetailCancel,
      showMakeupList,
      notifyStudent,
      formatDate,
      submitComment,
      watchResultExpanded
    }
  }
})
</script>

<style scoped>
.test-result {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-title {
  font-size: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.header-title span {
  margin-left: 8px;
}

.header-description {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
}

.animated-card {
  transition: all 0.3s;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.animated-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.action-link {
  transition: color 0.3s;
}

.action-link:hover {
  color: #1890ff;
}

.edit-link:hover {
  color: #faad14;
}

.delete-link:hover {
  color: #ff4d4f;
}

.result-descriptions :deep(.ant-descriptions-item) {
  padding: 12px;
}

.comments-list {
  margin-top: 16px;
  background-color: #fafafa;
  border-radius: 4px;
  padding: 12px;
}

.comment-item {
  padding: 8px;
  transition: background-color 0.3s;
}

.comment-item:hover {
  background-color: #f0f0f0;
}

.collapsed-hint {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}

.result-form :deep(.ant-form-item) {
  margin-bottom: 20px;
}

.form-select,
.form-input {
  border-radius: 4px;
}

.detail-modal :deep(.ant-modal-body),
.makeup-modal :deep(.ant-modal-body) {
  padding: 24px;
}

/* 补考名单表格样式 */
.makeup-modal :deep(.ant-table) {
  border-radius: 8px;
  overflow: hidden;
}

.makeup-modal :deep(.ant-table-thead > tr > th) {
  background-color: #f5f5f5;
}
</style>
