<template>
  <div class="test-result">
    <div class="table-operations" style="margin-bottom: 16px">
      <a-space>
        <a-button type="primary" @click="showModal" v-if="isAdmin">录入成绩</a-button>
        <a-button @click="showMakeupList" v-if="isAdmin">补考名单</a-button>
      </a-space>
    </div>

    <div v-for="result in results" :key="result.id" class="result-card" style="margin-bottom: 24px">
      <a-card>
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
            <a @click="result.expanded = !result.expanded">
              {{ result.expanded ? '收起' : '展开' }}
            </a>
            <a @click="viewDetail(result)">查看详情</a>
            <template v-if="isAdmin">
              <a-divider type="vertical" />
              <a @click="editResult(result)">编辑</a>
              <a-divider type="vertical" />
              <a-popconfirm
                title="确定要删除这个成绩记录吗？"
                @confirm="deleteResult(result.id)"
              >
                <a>删除</a>
              </a-popconfirm>
            </template>
          </a-space>
        </template>

        <div v-if="result.expanded">
          <a-descriptions :column="4">
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
                <a-list-item v-if="item && item.student">
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
    >
      <a-form
        :model="formState"
        :rules="rules"
        ref="formRef"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="学生" name="student" v-if="!formState.id">
          <a-select
            v-model:value="formState.student"
            show-search
            placeholder="请选择学生"
            :options="students"
            :field-names="{ label: 'name', value: 'id' }"
          />
        </a-form-item>
        <a-form-item label="测试计划" name="test_plan" v-if="!formState.id">
          <a-select
            v-model:value="formState.test_plan"
            show-search
            placeholder="请选择测试计划"
            :options="testPlans"
            :field-names="{ label: 'title', value: 'id' }"
          />
        </a-form-item>
        <a-form-item label="BMI指数" name="bmi">
          <a-input-number v-model:value="formState.bmi" :min="10" :max="40" style="width: 100%" />
        </a-form-item>
        <a-form-item label="肺活量(ml)" name="vital_capacity">
          <a-input-number v-model:value="formState.vital_capacity" :min="0" :max="10000" style="width: 100%" />
        </a-form-item>
        <a-form-item label="50米跑(秒)" name="run_50m">
          <a-input-number v-model:value="formState.run_50m" :min="0" :max="60" :precision="2" style="width: 100%" />
        </a-form-item>
        <a-form-item label="坐位体前屈(cm)" name="sit_and_reach">
          <a-input-number v-model:value="formState.sit_and_reach" :min="-20" :max="40" style="width: 100%" />
        </a-form-item>
        <a-form-item label="立定跳远(cm)" name="standing_jump">
          <a-input-number v-model:value="formState.standing_jump" :min="0" :max="400" style="width: 100%" />
        </a-form-item>
        <a-form-item label="800米跑(秒)" name="run_800m">
          <a-input-number v-model:value="formState.run_800m" :min="0" :max="600" style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 成绩详情模态框 -->
    <a-modal
      title="成绩详情"
      :open="detailVisible"
      @ok="closeDetail"
      @cancel="closeDetail"
      width="800px"
    >
      <a-descriptions bordered>
        <a-descriptions-item label="学生姓名" :span="3">
          {{ currentDetail?.student?.name }}
        </a-descriptions-item>
        <a-descriptions-item label="测试计划" :span="3">
          {{ currentDetail?.test_plan?.title }}
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
        <a-descriptions-item label="总分" :span="3">
          <span :style="{ color: currentDetail?.total_score < 60 ? '#ff4d4f' : '#52c41a' }">
            {{ currentDetail?.total_score }}
          </span>
        </a-descriptions-item>
      </a-descriptions>

      <!-- 评论区 -->
      <div style="margin-top: 24px">
        <a-divider>评论区</a-divider>
        <a-list
          :data-source="currentDetail?.comments"
          :loading="currentDetail?.commentsLoading"
          item-layout="horizontal"
        >
          <template #header v-if="store.state.user?.user_type === 'student'">
            <a-input-group compact>
              <a-input
                :value="currentDetail?.newComment || ''"
                @update:value="val => currentDetail && (currentDetail.newComment = val)"
                placeholder="写下你的评论..."
                style="width: calc(100% - 80px)"
                @keyup.enter="() => currentDetail && submitComment(currentDetail)"
              />
              <a-button 
                type="primary" 
                @click="() => currentDetail && submitComment(currentDetail)" 
                :loading="currentDetail?.commentsLoading"
              >发送</a-button>
            </a-input-group>
          </template>
          <template #renderItem="{ item }">
            <a-list-item v-if="item && item.student">
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
            <template v-if="store.state.user?.user_type !== 'student'">
              <a-empty description="只有学生可以查看和发表评论" />
            </template>
            <template v-else>
              <a-empty v-if="currentDetail?.commentError" description="加载评论失败" />
              <a-empty v-else description="暂无评论" />
            </template>
          </template>
        </a-list>
      </div>
    </a-modal>

    <!-- 补考名单模态框 -->
    <a-modal
      title="补考名单"
      :open="makeupVisible"
      @ok="closeMakeup"
      @cancel="closeMakeup"
      width="800px"
    >
      <a-table :columns="makeupColumns" :data-source="makeupList" :loading="makeupLoading">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-button type="primary" size="small" @click="arrangeMakeup(record)">
              安排补考
            </a-button>
          </template>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import { useStore } from 'vuex'
import dayjs from 'dayjs'

export default defineComponent({
  name: 'TestResult',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const visible = ref(false)
    const detailVisible = ref(false)
    const makeupVisible = ref(false)
    const confirmLoading = ref(false)
    const modalTitle = ref('录入成绩')
    const results = ref([])
    const students = ref([])
    const testPlans = ref([])
    const formRef = ref(null)
    const currentDetail = ref(null)
    const makeupList = ref([])
    const makeupLoading = ref(false)
    
    const isAdmin = computed(() => store.getters.isAdmin)

    // 初始化每个测试结果的评论状态
    const initializeResultComments = (result) => {
      if (!result.comments) result.comments = []
      if (!result.newComment) result.newComment = ''
      if (result.commentsLoading === undefined) result.commentsLoading = false
      if (result.commentError === undefined) result.commentError = false
      // Initialize the expanded property to false for collapsible view
      result.expanded = false
      return result
    }

    const formState = ref({
      id: null,
      student: null,
      test_plan: null,
      bmi: null,
      vital_capacity: null,
      run_50m: null,
      sit_and_reach: null,
      standing_jump: null,
      run_800m: null
    })

    const rules = {
      student: [{ required: true, message: '请选择学生' }],
      test_plan: [{ required: true, message: '请选择测试计划' }],
      bmi: [{ required: true, message: '请输入BMI指数' }],
      vital_capacity: [{ required: true, message: '请输入肺活量' }],
      run_50m: [{ required: true, message: '请输入50米跑成绩' }],
      sit_and_reach: [{ required: true, message: '请输入体前屈成绩' }],
      standing_jump: [{ required: true, message: '请输入立定跳远成绩' }],
      run_800m: [{ required: true, message: '请输入800米跑成绩' }]
    }

    const columns = [
      {
        title: '学生',
        dataIndex: ['student', 'name'],
        key: 'student_name'
      },
      {
        title: '测试计划',
        dataIndex: ['test_plan', 'title'],
        key: 'test_plan_title'
      },
      {
        title: '测试日期',
        dataIndex: 'test_date',
        key: 'test_date',
        render: (text) => dayjs(text).format('YYYY-MM-DD')
      },
      {
        title: '总分',
        dataIndex: 'total_score',
        key: 'total_score'
      },
      {
        title: '是否补考',
        dataIndex: 'is_makeup',
        key: 'is_makeup',
        render: (text) => text ? '是' : '否'
      },
      {
        title: '操作',
        key: 'action'
      }
    ]

    const makeupColumns = [
      {
        title: '学生',
        dataIndex: ['student', 'name'],
        key: 'student_name'
      },
      {
        title: '原测试计划',
        dataIndex: ['test_plan', 'title'],
        key: 'test_plan_title'
      },
      {
        title: '原测试日期',
        dataIndex: 'test_date',
        key: 'test_date',
        render: (text) => dayjs(text).format('YYYY-MM-DD')
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

    // 获取所有成绩记录
    const fetchResults = async () => {
      loading.value = true
      try {
        const response = await axios.get('http://localhost:8000/api/test-results/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        
        // Initialize result data with proper properties
        if (store.state.user?.user_type === 'student') {
          results.value = response.data.map(initializeResultComments)
          await fetchAllComments()
        } else {
          // For non-students, still initialize the expanded property
          results.value = response.data.map(result => ({
            ...result,
            expanded: false
          }))
        }
      } catch (error) {
        message.error('获取成绩记录失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    // 获取学生列表
    const fetchStudents = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/students/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        students.value = response.data
      } catch (error) {
        message.error('获取学生列表失败')
        console.error(error)
      }
    }

    // 获取测试计划列表
    const fetchTestPlans = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/test-plans/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        testPlans.value = response.data
      } catch (error) {
        message.error('获取测试计划失败')
        console.error(error)
      }
    }

    // 获取所有测试结果的评论
    const fetchAllComments = async () => {
      for (const result of results.value) {
        await fetchResultComments(result)
      }
    }

    // 获取单个测试结果的评论
    const fetchResultComments = async (result) => {
      if (!result?.id) return
      
      // 初始化评论相关属性
      if (!result.comments) result.comments = []
      if (!result.newComment) result.newComment = ''
      if (result.commentsLoading === undefined) result.commentsLoading = false
      if (result.commentError === undefined) result.commentError = false

      result.commentsLoading = true
      result.commentError = false

      try {
        const response = await axios.get(`http://localhost:8000/api/comments/?test_result=${result.id}`, {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        result.comments = response.data || []
      } catch (error) {
        console.error('获取评论失败:', error)
        result.commentError = true
        result.comments = []
      } finally {
        result.commentsLoading = false
      }
    }

    // 提交评论
    const submitComment = async (result) => {
      if (!result?.id) {
        message.error('无效的测试结果ID')
        return
      }
      if (!result.newComment?.trim()) {
        message.warning('请输入评论内容')
        return
      }
      if (!store.state.user?.id) {
        message.error('请先登录')
        return
      }
      if (store.state.user.user_type !== 'student') {
        message.error('只有学生可以发表评论')
        return
      }
      
      // Check if user has a student_profile
      if (!store.state.user.student_profile) {
        message.error('未找到学生资料，请先完善个人资料，创建学生档案才能发表评论')
        return
      }

      result.commentsLoading = true
      try {
        await axios.post(
          'http://localhost:8000/api/comments/',
          {
            test_result: result.id,
            content: result.newComment.trim()
          },
          {
            headers: { Authorization: `Bearer ${store.state.token}` }
          }
        )
        message.success('评论提交成功，等待审核')
        result.newComment = ''
        await fetchResultComments(result)
      } catch (error) {
        console.error('Comment submission error:', error.response?.data || error)
        let errorMessage = '评论提交失败'
        
        // Handle student profile error specifically
        if (error.response?.data?.student) {
          errorMessage = '未找到学生信息，请先完善个人资料。需要创建学生档案才能发表评论。'
          // Redirect to profile page or show more specific instructions could be added here
        } else if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail
        }
        message.error(errorMessage)
      } finally {
        result.commentsLoading = false
      }
    }

    // 获取补考名单
    const fetchMakeupList = async () => {
      makeupLoading.value = true
      try {
        const response = await axios.get('http://localhost:8000/api/test-results/makeup_list/', {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        makeupList.value = response.data
      } catch (error) {
        message.error('获取补考名单失败')
        console.error(error)
      } finally {
        makeupLoading.value = false
      }
    }

    const showModal = () => {
      modalTitle.value = '录入成绩'
      formState.value = {
        id: null,
        student: null,
        test_plan: null,
        bmi: null,
        vital_capacity: null,
        run_50m: null,
        sit_and_reach: null,
        standing_jump: null,
        run_800m: null
      }
      visible.value = true
    }

    const editResult = (record) => {
      modalTitle.value = '编辑成绩'
      formState.value = { ...record }
      visible.value = true
    }

    const handleOk = async () => {
      try {
        await formRef.value.validate()
        confirmLoading.value = true
        
        if (formState.value.id) {
          // 更新成绩
          await axios.put(
            `http://localhost:8000/api/test-results/${formState.value.id}/`,
            formState.value,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('更新成功')
        } else {
          // 添加成绩
          await axios.post(
            'http://localhost:8000/api/test-results/',
            formState.value,
            {
              headers: { Authorization: `Bearer ${store.state.token}` }
            }
          )
          message.success('添加成功')
        }
        
        visible.value = false
        fetchResults()
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

    const deleteResult = async (id) => {
      try {
        await axios.delete(`http://localhost:8000/api/test-results/${id}/`, {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        message.success('删除成功')
        fetchResults()
      } catch (error) {
        message.error('删除失败')
        console.error(error)
      }
    }

    const viewDetail = async (record) => {
      // Deep clone to avoid modifying the original record
      currentDetail.value = { ...record }
      
      // Only initialize comment features if user is a student
      if (store.state.user?.user_type === 'student') {
        currentDetail.value = initializeResultComments(currentDetail.value)
        await fetchResultComments(currentDetail.value)
      }
      
      detailVisible.value = true
    }

    const closeDetail = () => {
      detailVisible.value = false
      currentDetail.value = null
    }

    const showMakeupList = () => {
      makeupVisible.value = true
      fetchMakeupList()
    }

    const closeMakeup = () => {
      makeupVisible.value = false
    }

    const arrangeMakeup = (record) => {
      // 这里可以添加安排补考的逻辑
      message.info('补考安排功能待实现')
    }

    onMounted(() => {
      fetchResults()
      if (isAdmin.value) {
        fetchStudents()
        fetchTestPlans()
      }
    })

    return {
      store,
      loading,
      visible,
      detailVisible,
      makeupVisible,
      confirmLoading,
      modalTitle,
      results,
      students,
      testPlans,
      formState,
      formRef,
      rules,
      columns,
      makeupColumns,
      currentDetail,
      makeupList,
      makeupLoading,
      isAdmin,
      showModal,
      editResult,
      handleOk,
      handleCancel,
      deleteResult,
      viewDetail,
      closeDetail,
      submitComment,
      showMakeupList,
      closeMakeup,
      arrangeMakeup
    }
  }
})
</script>

<style scoped>
.test-result {
  padding: 24px;
}

.collapsed-hint {
  text-align: center;
  padding: 8px 0;
  color: #1890ff;
}
</style>
