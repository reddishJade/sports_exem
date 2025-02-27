import { createStore } from 'vuex'
import axios from 'axios'

const store = createStore({
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
        const response = await axios.post('http://localhost:8000/api/auth/login/', credentials)
        const { access, refresh, user } = response.data
        commit('setToken', { access, refresh })
        commit('setUser', user)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
        return response.data
      } finally {
        commit('setLoading', false)
      }
    },
    
    async register({ commit }, userData) {
      commit('setLoading', true)
      try {
        const response = await axios.post('http://localhost:8000/api/auth/register/', userData)
        const { access, refresh, user } = response.data
        commit('setToken', { access, refresh })
        commit('setUser', user)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
        return response.data
      } finally {
        commit('setLoading', false)
      }
    },
    
    async refreshToken({ commit, state }) {
      try {
        const response = await axios.post('http://localhost:8000/api/auth/refresh/', {
          refresh: state.refreshToken
        })
        const { access } = response.data
        commit('setToken', { 
          access,
          refresh: state.refreshToken 
        })
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
        return response.data
      } catch (error) {
        commit('clearAuth')
        throw error
      }
    },
    
    logout({ commit }) {
      commit('clearAuth')
      delete axios.defaults.headers.common['Authorization']
    }
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    isAdmin: state => state.user?.is_staff || false,
    isLoading: state => state.loading,
    currentUser: state => state.user
  }
})

export default store
