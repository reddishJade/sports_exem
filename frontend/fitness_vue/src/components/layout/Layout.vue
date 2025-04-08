<template>
  <div class="layout">
    <router-view />
    <footer class="footer">
      <div class="footer-content">
        <span>体测管理系统 2025</span>
        <span>|</span>
        <span>打造专业体育测试管理平台</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.footer {
  width: 100%;
  padding: 20px 0;
  background: #f5f5f5;
  text-align: center;
  margin-top: auto;
}

.footer-content {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  color: #666;
  font-size: 14px;
}
</style>
