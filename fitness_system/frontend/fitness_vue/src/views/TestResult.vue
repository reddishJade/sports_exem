<template>
  <div class="test-result">
    <div class="table-operations" style="margin-bottom: 16px">
      <a-space>
        <a-button type="primary" @click="showModal" v-if="isAdmin">录入成绩</a-button>
        <a-button @click="showMakeupList" v-if="isAdmin">补考名单</a-button>
      </a-space>
    </div>

    <a-table :columns="columns" :data-source="results" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="viewDetail(record)">查看详情</a>
            <template v-if="isAdmin">
              <a-divider type="vertical" />
              <a @click="editResult(record)">编辑</a>
              <a-divider type="vertical" />
              <a-popconfirm
                title="确定要删除这个成绩记录吗？"
                @confirm="deleteResult(record.id)"
              >
                <a>删除</a>
              </a-popconfirm>
            </template>
          </a-space>
        </template>
        <template v-else-if="column.key === 'total_score'">
          <span :style="{ color: record.total_score < 60 ? '#ff4d4f' : '#52c41a' }">
            {{ record.total_score }}
          </span>
        </template>
      </template>
    </a-table>

    <!-- 成绩录入/编辑模态框 -->
    <a-modal
      :title="modalTitle"
      :visible="visible"
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
      :visible="detailVisible"
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
          :data-source="comments"
          :loading="commentsLoading"
          item-layout="horizontal"
        >
          <template #header>
            <a-input-group compact>
              <a-input
                v-model:value="newComment"
                placeholder="写下你的评论..."
                style="width: calc(100% - 80px)"
              />
              <a-button type="primary" @click="submitComment">发送</a-button>
            </a-input-group>
          </template>
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta
                :title="item.student.name"
                :description="item.content"
              >
                <template #avatar>
                  <a-avatar>{{ item.student.name[0] }}</a-avatar>
                </template>
              </a-list-item-meta>
              <template #extra>
                <a-tag :color="item.is_approved ? 'green' : 'orange'">
                  {{ item.is_approved ? '已审核' : '待审核' }}
                </a-tag>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </a-modal>

    <!-- 补考名单模态框 -->
    <a-modal
      title="补考名单"
      :visible="makeupVisible"
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
    const comments = ref([])
    const commentsLoading = ref(false)
    const newComment = ref('')
    const makeupList = ref([])
    const makeupLoading = ref(false)
    
    const isAdmin = computed(() => store.getters.isAdmin)

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
        results.value = response.data
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

    // 获取评论列表
    const fetchComments = async (resultId) => {
      commentsLoading.value = true
      try {
        const response = await axios.get(`http://localhost:8000/api/comments/?test_result=${resultId}`, {
          headers: { Authorization: `Bearer ${store.state.token}` }
        })
        comments.value = response.data
      } catch (error) {
        message.error('获取评论失败')
        console.error(error)
      } finally {
        commentsLoading.value = false
      }
    }

    // 提交评论
    const submitComment = async () => {
      if (!newComment.value.trim()) {
        message.warning('请输入评论内容')
        return
      }

      try {
        await axios.post(
          'http://localhost:8000/api/comments/',
          {
            test_result: currentDetail.value.id,
            content: newComment.value
          },
          {
            headers: { Authorization: `Bearer ${store.state.token}` }
          }
        )
        message.success('评论提交成功，等待审核')
        newComment.value = ''
        fetchComments(currentDetail.value.id)
      } catch (error) {
        message.error('评论提交失败')
        console.error(error)
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
      currentDetail.value = record
      detailVisible.value = true
      fetchComments(record.id)
    }

    const closeDetail = () => {
      detailVisible.value = false
      currentDetail.value = null
      comments.value = []
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
      comments,
      commentsLoading,
      newComment,
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
</style>
