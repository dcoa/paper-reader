<template>
  <div class="page-layout" :class="{ 
    'page-layout--full-height': fullHeight, 
    'page-layout--centered': centered 
  }">
    <div v-if="showHeader" class="page-header">
      <div class="page-header__content">
        <div class="page-header__left">
          <h1 v-if="title" class="page-title">{{ title }}</h1>
          <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
        </div>
        <div v-if="$slots.headerActions" class="page-header__actions">
          <slot name="headerActions"></slot>
        </div>
      </div>
    </div>
    
    <div class="page-content" :class="{ 'page-content--with-padding': padding }">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  // 页面标题
  title: {
    type: String,
    default: ''
  },
  // 页面副标题
  subtitle: {
    type: String,
    default: ''
  },
  // 是否显示头部
  showHeader: {
    type: Boolean,
    default: false
  },
  // 是否全屏高度
  fullHeight: {
    type: Boolean,
    default: true
  },
  // 是否居中显示
  centered: {
    type: Boolean,
    default: false
  },
  // 是否添加内边距
  padding: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.page-layout {
  background-color: var(--color-background-default);
  display: flex;
  flex-direction: column;
}

.page-layout--full-height {
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
}

.page-layout--centered {
  align-items: center;
  justify-content: center;
}

.page-header {
  background-color: var(--color-background-paper);
  border-bottom: 1px solid var(--color-grey-200);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.page-header__content {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-6) var(--spacing-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
}

.page-header__left {
  flex: 1;
  min-width: 0;
}

.page-title {
  margin: 0 0 var(--spacing-1) 0;
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-h2);
  color: var(--color-text-primary);
}

.page-subtitle {
  margin: 0;
  font-size: var(--font-size-body2);
  line-height: var(--line-height-body2);
  color: var(--color-text-secondary);
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  flex-shrink: 0;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.page-content--with-padding {
  padding: var(--spacing-6);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header__content {
    padding: var(--spacing-4) var(--spacing-3);
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-3);
  }
  
  .page-header__actions {
    justify-content: center;
  }
  
  .page-title {
    font-size: var(--font-size-h3);
    text-align: center;
  }
  
  .page-subtitle {
    text-align: center;
  }
  
  .page-content--with-padding {
    padding: var(--spacing-4);
  }
}

@media (min-width: 768px) {
  .page-header__content {
    padding: var(--spacing-6);
  }
}

@media (min-width: 1024px) {
  .page-header__content {
    padding: var(--spacing-8) var(--spacing-6);
  }
  
  .page-content--with-padding {
    padding: var(--spacing-8);
  }
}
</style> 