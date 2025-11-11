<script setup>
// 科研加速Web应用主应用文件
import { onMounted } from 'vue'
import { useUserStore } from '@/store/user'

// 初始化用户store
const userStore = useUserStore()

onMounted(() => {
  // 应用启动时检查用户登录状态
  userStore.checkAuth()
})
</script>

<template>
  <div id="app">
    <!-- 这里使用router-view显示路由页面 -->
    <router-view />
  </div>
</template>

<style>
/* 引入设计系统 */
@import '@/styles/design-system.css';

/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  height: 100%;
  width: 100%;
}

body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  font-family: var(--font-family);
  font-size: var(--font-size-body1);
  line-height: var(--line-height-body1);
  color: var(--color-text-primary);
  background-color: var(--color-background-default);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  width: 100%;
  background-color: var(--color-background-default);
  box-sizing: border-box;
}

/* Element Plus 样式覆盖 */
.el-button--primary {
  background-color: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
}

.el-button--primary:hover,
.el-button--primary:focus {
  background-color: var(--color-primary-dark) !important;
  border-color: var(--color-primary-dark) !important;
}

.el-button--success {
  background-color: var(--color-feedback-success) !important;
  border-color: var(--color-feedback-success) !important;
}

.el-button--warning {
  background-color: var(--color-feedback-warning) !important;
  border-color: var(--color-feedback-warning) !important;
}

.el-button--danger {
  background-color: var(--color-feedback-error) !important;
  border-color: var(--color-feedback-error) !important;
}

.el-link--primary {
  color: var(--color-primary) !important;
}

.el-tag--primary {
  background-color: var(--color-primary-light) !important;
  color: var(--color-primary-dark) !important;
  border-color: var(--color-primary) !important;
}

.el-card {
  border-radius: var(--border-radius-lg) !important;
  box-shadow: var(--shadow-sm) !important;
  border: 1px solid var(--color-grey-200) !important;
}

.el-card:hover {
  box-shadow: var(--shadow-md) !important;
}

.el-input__wrapper {
  border-radius: var(--border-radius) !important;
}

.el-select .el-input__wrapper {
  border-radius: var(--border-radius) !important;
}

.el-menu-item.is-active {
  background-color: var(--color-primary-light) !important;
  color: var(--color-primary-dark) !important;
}

.el-message-box {
  z-index: 3000 !important;
  border-radius: var(--border-radius-lg) !important;
}

.el-loading-mask {
  z-index: 2000 !important;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-grey-100);
  border-radius: var(--border-radius);
}

::-webkit-scrollbar-thumb {
  background: var(--color-grey-400);
  border-radius: var(--border-radius);
  transition: background var(--transition-fast);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-grey-500);
}

/* Firefox 滚动条样式 */
* {
  scrollbar-width: thin;
  scrollbar-color: var(--color-grey-400) var(--color-grey-100);
}

/* 改善焦点样式 */
*:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.el-button:focus,
.el-input__wrapper:focus,
.el-select:focus {
  outline: none;
}

/* 响应式容器 */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-4);
}

@media (min-width: 768px) {
  .container {
    padding: 0 var(--spacing-6);
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 0 var(--spacing-8);
  }
}
</style>
