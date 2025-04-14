import { createStore } from 'vuex'
import api from '@/services/api'
import aiChat from './modules/aiChat'

const store = createStore({
  modules: {
    aiChat
  },
  state: {
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    loading: false
  },
  
  mutations: {
    setToken(state, { access, refresh }) {
      state.token = access
      state.refreshToken = refresh
      localStorage.setItem('token', access)
      localStorage.setItem('refreshToken', refresh)
    },
    
    setUser(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    
    setLoading(state, loading) {
      state.loading = loading
    },
    
    clearAuth(state) {
      state.token = null
      state.refreshToken = null
      state.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      commit('setLoading', true)
      try {
        const response = await api.post('/auth/login/', credentials)
        const { access, refresh, user } = response.data
        commit('setToken', { access, refresh })
        commit('setUser', user)
        return response.data
      } finally {
        commit('setLoading', false)
      }
    },
    
    async register({ commit }, userData) {
      commit('setLoading', true)
      try {
        const response = await api.post('/auth/register/', userData)
        const { access, refresh, user } = response.data
        commit('setToken', { access, refresh })
        commit('setUser', user)
        return response.data
      } finally {
        commit('setLoading', false)
      }
    },
    
    async refreshToken({ commit, state }) {
      try {
        const response = await api.post('/auth/refresh/', {
          refresh: state.refreshToken
        })
        const { access } = response.data
        commit('setToken', { 
          access,
          refresh: state.refreshToken 
        })
        return response.data
      } catch (error) {
        commit('clearAuth')
        throw error
      }
    },
    
    async fetchCurrentUser({ commit, state }) {
      if (!state.token || !state.user || !state.user.id) return null
      
      commit('setLoading', true)
      try {
        // 获取当前用户详细信息，包括学生资料
        const userId = state.user.id
        const response = await api.get(`/users/${userId}/`)
        
        // 如果是学生，尝试获取学生资料
        let userData = response.data
        if (userData.user_type === 'student') {
          try {
            // 尝试获取学生资料
            const studentResponse = await api.get('/students/', {
              params: { user: userId }
            })
            
            if (studentResponse.data && studentResponse.data.length > 0) {
              // 将学生数据加入到用户数据中
              userData.student_profile = studentResponse.data[0]
            }
          } catch (studentError) {
            console.warn('获取学生数据失败:', studentError)
          }
        }
        
        // 更新用户数据
        commit('setUser', userData)
        return userData
      } catch (error) {
        console.error('获取用户信息失败:', error)
        if (error.response && error.response.status === 401) {
          // 如果是认证问题，尝试刷新令牌
          try {
            await this.dispatch('refreshToken')
            return this.dispatch('fetchCurrentUser')  // 递归调用自身
          } catch (refreshError) {
            // 如果刷新失败，清除认证状态
            commit('clearAuth')
            throw refreshError
          }
        }
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    
    logout({ commit }) {
      commit('clearAuth')
      // 不需要手动删除Authorization头，因为每个请求都会从当前store状态获取token
    }
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    isAdmin: state => state.user?.is_staff || false,
    isLoading: state => state.loading,
    currentUser: state => state.user,
    userType: state => state.user?.user_type || null,
    isStudent: state => state.user?.user_type === 'student',
    isParent: state => state.user?.user_type === 'parent'
  }
})

export default store
