<template>
  <div class="simple-pdf-viewer">
    <!-- Top Toolbar -->
    <div class="pdf-toolbar">
      <div class="toolbar-left">
        <!-- Page Control -->
        <el-button-group size="small">
          <el-button @click="prevPage" :disabled="currentPage <= 1" icon="ArrowLeft">
            Previous
          </el-button>
          <el-input
            v-model="pageInput"
            size="small"
            class="page-input"
            @keyup.enter="goToPage"
            @blur="goToPage"
          />
          <span class="page-total">/ {{ numPages }}</span>
          <el-button @click="nextPage" :disabled="currentPage >= numPages" icon="ArrowRight">
            Next
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-center">
        <!-- Zoom Control -->
        <el-button-group size="small">
          <el-button @click="zoomOut" :disabled="scale <= 0.5" icon="ZoomOut">
            Zoom Out
          </el-button>
          <el-button @click="resetZoom">
            {{ Math.round(scale * 100) }}%
          </el-button>
          <el-button @click="zoomIn" :disabled="scale >= 3" icon="ZoomIn">
            Zoom In
          </el-button>
        </el-button-group>

        <!-- Fit Control -->
        <el-button-group size="small" style="margin-left: 8px;">
          <el-button @click="fitWidth">
            Fit Width
          </el-button>
          <el-button @click="fitPage">
            Fit Page
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-right">
        <div class="wheel-tip">
          <el-icon><Mouse /></el-icon>
          <span>Scroll to browse/turn pages</span>
        </div>
        <el-button size="small" @click="downloadPDF" type="primary" icon="Download">
          Download PDF
        </el-button>
      </div>
    </div>
    
    <!-- PDF Display Area -->
    <div class="pdf-content" ref="pdfContainer">
      <div v-if="loading && !pdfSource" class="pdf-loading">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>Loading PDF...</p>
      </div>

      <div v-else-if="error" class="pdf-error">
        <el-icon class="error-icon"><Warning /></el-icon>
        <p>{{ error }}</p>
        <el-button @click="retry" type="primary">Retry</el-button>
      </div>

      <div v-else-if="pdfSource" class="pdf-viewer-container">
        <vue-pdf-embed
          ref="pdfRef"
          :source="pdfSource"
          :page="currentPage"
          :scale="scale"
          text-layer
          annotation-layer
          @loaded="onLoaded"
          @loading-failed="onError"
          @page-loaded="onPageLoaded"
          @password-requested="onPasswordRequested"
          @internal-link-clicked="onInternalLinkClicked"
          @source-changed="onSourceChanged"
          @rendering-failed="onRenderingFailed"
          class="pdf-page"
          :style="{
            width: scale > 1.0 ? (595 * scale) + 'px' : 'auto',
            height: scale > 1.0 ? (842 * scale) + 'px' : 'auto'
          }"
        />
      </div>

      <div v-else class="pdf-waiting">
        <p>Waiting for PDF data to load...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { Mouse } from '@element-plus/icons-vue'

// 导入PDF.js的样式文件，以支持文字选择和注释
import 'vue-pdf-embed/dist/styles/annotationLayer.css'
import 'vue-pdf-embed/dist/styles/textLayer.css'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  paperId: {
    type: [Number, String],
    default: null
  }
})

const emits = defineEmits(['load', 'error'])

// 用户store
const userStore = useUserStore()

// 引用
const pdfContainer = ref()
const pdfRef = ref()

// PDF状态
const loading = ref(true)
const error = ref('')
const currentPage = ref(1)
const numPages = ref(0)
const scale = ref(1.0)
const pageInput = ref('1')

// 滚轮翻页相关
const wheelTimeout = ref(null)
const isWheelScrolling = ref(false)

// 容器尺寸
const containerWidth = ref(0)
const containerHeight = ref(0)

// 计算PDF显示尺寸
const basePdfWidth = computed(() => {
  if (containerWidth.value > 0) {
    return Math.min(containerWidth.value - 40, 1200) // 最大宽度1200px，留40px边距
  }
  return 800 // 默认宽度
})

const basePdfHeight = computed(() => {
  if (containerHeight.value > 0) {
    return containerHeight.value - 20 // 留20px边距
  }
  return 600 // 默认高度
})

// 根据缩放比例计算实际PDF尺寸
const pdfWidth = computed(() => {
  // 当缩放比例大于1时，允许PDF超出容器大小
  const baseWidth = basePdfWidth.value
  if (scale.value > 1.0) {
    return baseWidth * scale.value
  }
  return baseWidth
})

const pdfHeight = computed(() => {
  // 当缩放比例大于1时，允许PDF超出容器大小
  const baseHeight = basePdfHeight.value
  if (scale.value > 1.0) {
    return baseHeight * scale.value
  }
  return baseHeight
})

// PDF数据状态
const pdfBlobUrl = ref(null)
const pdfDataLoading = ref(false)

// 手动获取PDF数据
const fetchPDFData = async (url) => {
  console.log('开始获取PDF数据:', url)
  
  pdfDataLoading.value = true
  loading.value = true
  error.value = ''
  
  try {
    const token = userStore.token
    console.log('使用Token:', token ? `${token.substring(0, 20)}...` : 'NO TOKEN')
    
    const response = await fetch(url, {
      method: 'GET',
      headers: token ? {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/pdf'
      } : {},
      credentials: 'same-origin'
    })
    
    console.log('Response status:', response.status, response.statusText)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const blob = await response.blob()
    console.log('Blob data received:', blob.size, 'bytes')

    // Clear old blob URL
    if (pdfBlobUrl.value) {
      URL.revokeObjectURL(pdfBlobUrl.value)
    }

    // Create new blob URL
    pdfBlobUrl.value = URL.createObjectURL(blob)
    console.log('Blob URL created:', pdfBlobUrl.value)

    console.log('PDF data fetched successfully')

  } catch (error) {
    console.error('Failed to fetch PDF data:', error)

    let errorMessage = 'Failed to load PDF'
    if (error.message.includes('401')) {
      errorMessage = 'PDF access requires login. Please login and try again'
    } else if (error.message.includes('404')) {
      errorMessage = 'PDF file does not exist or has been deleted'
    } else if (error.message.includes('fetch')) {
      errorMessage = 'Network connection failed. Please check your network and try again'
    } else {
      errorMessage = `Failed to load PDF: ${error.message}`
    }

    error.value = errorMessage
    loading.value = false
    ElMessage.error(errorMessage)
    emits('error')
  } finally {
    pdfDataLoading.value = false
  }
}

// Handle authenticated PDF source
const pdfSource = computed(() => {
  console.log('Computing PDF Source')
  console.log('- Props src:', props.src)
  console.log('- pdfBlobUrl:', pdfBlobUrl.value)

  if (!props.src) {
    console.log('No src, returning null')
    return null
  }

  // If blob URL exists, use it directly
  if (pdfBlobUrl.value) {
    console.log('Using Blob URL:', pdfBlobUrl.value)
    return pdfBlobUrl.value
  }

  // If API path, need to fetch data manually
  if (props.src.includes('/api/papers/')) {
    console.log('Detected API path, triggering data fetch')
    // Trigger data fetch in nextTick
    nextTick(() => {
      if (!pdfDataLoading.value && !pdfBlobUrl.value) {
        fetchPDFData(props.src)
      }
    })
    return null // Temporarily return null, waiting for data fetch to complete
  }

  console.log('Returning src directly:', props.src)
  return props.src
})

// 更新容器尺寸
const updateContainerSize = () => {
  if (pdfContainer.value) {
    const rect = pdfContainer.value.getBoundingClientRect()
    containerWidth.value = rect.width
    containerHeight.value = rect.height
  }
}

// 页面导航
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    updatePageInput()
  }
}

const nextPage = () => {
  if (currentPage.value < numPages.value) {
    currentPage.value++
    updatePageInput()
  }
}

const goToPage = () => {
  const page = parseInt(pageInput.value)
  if (page >= 1 && page <= numPages.value && page !== currentPage.value) {
    currentPage.value = page
  } else {
    updatePageInput()
  }
}

const updatePageInput = () => {
  pageInput.value = currentPage.value.toString()
}

// Wheel page turning handler
const handleWheel = (event) => {
  // If zooming PDF, don't handle wheel page turning
  if (event.ctrlKey || event.metaKey) {
    return
  }

  // Debounce to avoid wheel being too sensitive
  if (isWheelScrolling.value) {
    return
  }

  const container = pdfContainer.value
  if (!container) return

  // Get scroll information
  const scrollTop = container.scrollTop
  const scrollHeight = container.scrollHeight
  const clientHeight = container.clientHeight

  // Check if there's enough wheel movement
  const threshold = 50 // Increase threshold for more stable page turning
  if (Math.abs(event.deltaY) < threshold) {
    return // Allow small scrolling
  }

  // Determine scroll position and direction
  const isScrollingDown = event.deltaY > 0
  const isScrollingUp = event.deltaY < 0

  // Check if at boundary
  const isAtTop = scrollTop <= 1 // Allow 1px error
  const isAtBottom = scrollTop >= scrollHeight - clientHeight - 1 // Allow 1px error

  // Only flip page when scrolling at boundary
  let shouldFlipPage = false

  if (isScrollingDown && isAtBottom) {
    // Continue scrolling down at bottom -> next page
    if (currentPage.value < numPages.value) {
      shouldFlipPage = true
      isWheelScrolling.value = true

      // Clear previous timer
      if (wheelTimeout.value) {
        clearTimeout(wheelTimeout.value)
      }

      nextPage()
      console.log('Wheel scroll down page turn:', currentPage.value)

      // Give user visual feedback
      container.style.transform = 'translateY(-2px)'
      setTimeout(() => {
        if (container) {
          container.style.transform = 'translateY(0)'
        }
      }, 100)

      // Reset scroll position to top after page turn
      setTimeout(() => {
        container.scrollTop = 0
      }, 50)

      // Set debounce delay
      wheelTimeout.value = setTimeout(() => {
        isWheelScrolling.value = false
      }, 300)
    }
  } else if (isScrollingUp && isAtTop) {
    // Continue scrolling up at top -> previous page
    if (currentPage.value > 1) {
      shouldFlipPage = true
      isWheelScrolling.value = true

      // Clear previous timer
      if (wheelTimeout.value) {
        clearTimeout(wheelTimeout.value)
      }
      
      prevPage()
      console.log('Wheel scroll up page turn:', currentPage.value)

      // Give user visual feedback
      container.style.transform = 'translateY(2px)'
      setTimeout(() => {
        if (container) {
          container.style.transform = 'translateY(0)'
        }
      }, 100)

      // Reset scroll position to bottom after page turn
      setTimeout(() => {
        container.scrollTop = container.scrollHeight - container.clientHeight
      }, 50)

      // Set debounce delay
      wheelTimeout.value = setTimeout(() => {
        isWheelScrolling.value = false
      }, 300)
    }
  }

  // Only prevent default scroll behavior when page turning
  if (shouldFlipPage) {
    event.preventDefault()
  }
  // Allow natural scrolling in other cases
}

// Zoom control
const zoomIn = () => {
  const oldScale = scale.value
  scale.value = Math.min(scale.value * 1.25, 3.0)
  console.log(`Zoom in: ${oldScale} -> ${scale.value}`)
}

const zoomOut = () => {
  const oldScale = scale.value
  scale.value = Math.max(scale.value / 1.25, 0.5)
  console.log(`Zoom out: ${oldScale} -> ${scale.value}`)
}

const resetZoom = () => {
  const oldScale = scale.value
  scale.value = 1.0
  console.log(`Reset zoom: ${oldScale} -> ${scale.value}`)
}

// Fit control
const fitWidth = () => {
  if (basePdfWidth.value > 0) {
    // Calculate fit width scale based on base width
    const targetScale = Math.min((basePdfWidth.value - 40) / 595, 2.0)
    scale.value = Math.max(targetScale, 0.5)
    console.log(`Fit width: base width=${basePdfWidth.value}, scale=${scale.value}`)
  }
}

const fitPage = () => {
  if (basePdfWidth.value > 0 && basePdfHeight.value > 0) {
    // Calculate fit page scale based on base dimensions
    const scaleX = (basePdfWidth.value - 40) / 595
    const scaleY = (basePdfHeight.value - 40) / 842
    const targetScale = Math.min(scaleX, scaleY, 2.0)
    scale.value = Math.max(targetScale, 0.5)
    console.log(`Fit page: base width=${basePdfWidth.value}, base height=${basePdfHeight.value}, scale=${scale.value}`)
  }
}

// PDF event handling
const onLoaded = (document) => {
  console.log('=== PDF loaded successfully ===')
  console.log('Document object:', document)
  console.log('Total pages:', document.numPages)
  console.log('PDF component reference:', pdfRef.value)

  loading.value = false
  error.value = ''
  numPages.value = document.numPages
  updatePageInput()
  ElMessage.success('PDF loaded successfully')
  emits('load')

  // Only fit width on initial load to avoid conflicts with user zoom
  // Remove auto fit width, let user control zoom manually
}

const onPageLoaded = (pageData) => {
  console.log('Page loaded:', pageData)
}

const onError = (error) => {
  console.error('PDF loading error:', error)

  loading.value = false
  let errorMessage = 'Failed to load PDF'
  
  if (error && error.message) {
    if (error.message.includes('password')) {
      errorMessage = 'PDF file requires password to open'
    } else if (error.message.includes('InvalidPDFException')) {
      errorMessage = 'PDF file format error or corrupted'
    } else if (error.message.includes('MissingPDFException')) {
      errorMessage = 'PDF file does not exist'
    } else {
      errorMessage = `Failed to load PDF: ${error.message}`
    }
  }

  error.value = errorMessage
  ElMessage.error(errorMessage)
  emits('error')
}

const onPasswordRequested = (callback) => {
  console.log('PDF requires password')
  ElMessage.warning('This PDF file requires a password. Encrypted PDFs are not supported')
  callback('')
}

const onInternalLinkClicked = (params) => {
  console.log('PDF internal link clicked:', params)
}

const onSourceChanged = (source) => {
  console.log('PDF source changed:', source)
}

const onRenderingFailed = (error) => {
  console.error('PDF rendering failed:', error)
  error.value = `PDF rendering failed: ${error.message || 'Unknown error'}`
  loading.value = false
  ElMessage.error('PDF rendering failed')
}

// Download PDF
const downloadPDF = () => {
  if (pdfBlobUrl.value) {
    const link = document.createElement('a')
    link.href = pdfBlobUrl.value
    link.download = `paper_${props.paperId || 'unknown'}.pdf`
    link.click()
  } else if (props.src) {
    const link = document.createElement('a')
    link.href = props.src
    link.download = `paper_${props.paperId || 'unknown'}.pdf`
    link.click()
  }
}

// Retry
const retry = () => {
  error.value = ''
  loading.value = true

  // Clear old data
  if (pdfBlobUrl.value) {
    URL.revokeObjectURL(pdfBlobUrl.value)
    pdfBlobUrl.value = null
  }

  // Fetch data again
  if (props.src.includes('/api/papers/')) {
    fetchPDFData(props.src)
  }
}



// Watch window resize
const handleResize = () => {
  updateContainerSize()
}

// Watch pdfSource changes
watch(pdfSource, (newSource) => {
  if (newSource) {
    console.log('PDF source updated')
  }
})

// Watch pdfRef changes
watch(pdfRef, (newRef) => {
  if (newRef) {
    console.log('PDF component mounted')
  }
})

// Watch scale changes
watch(scale, (newScale, oldScale) => {
  console.log(`Scale changed: ${oldScale} -> ${newScale}`)
})

onMounted(() => {
  console.log('SimplePDFViewer component mounted')

  window.addEventListener('resize', handleResize)
  updateContainerSize()

  // Add wheel event listener
  if (pdfContainer.value) {
    pdfContainer.value.addEventListener('wheel', handleWheel, { passive: false })
    console.log('Wheel page turn event listener added')
  }

  // Delay adding wheel listener (prevent container not rendered yet)
  nextTick(() => {
    if (pdfContainer.value && !pdfContainer.value.onwheel) {
      pdfContainer.value.addEventListener('wheel', handleWheel, { passive: false })
      console.log('Wheel page turn event listener added with delay')
    }
  })

  if (props.src) {
    console.log('Starting to process PDF source')
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)

  // Clean up wheel event listener
  if (pdfContainer.value) {
    pdfContainer.value.removeEventListener('wheel', handleWheel)
    console.log('Wheel page turn event listener cleaned up')
  }

  // Clean up timer
  if (wheelTimeout.value) {
    clearTimeout(wheelTimeout.value)
  }

  // Clean up blob URL
  if (pdfBlobUrl.value) {
    console.log('Cleaning up Blob URL')
    URL.revokeObjectURL(pdfBlobUrl.value)
    pdfBlobUrl.value = null
  }
})
</script>

<style scoped>
.simple-pdf-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f7fa;
}

.pdf-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wheel-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
  background: #f0f2f5;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.wheel-tip:hover {
  background: #e4e7ed;
  color: #409eff;
}

.wheel-tip .el-icon {
  font-size: 14px;
}

.page-input {
  width: 60px !important;
}

.page-total {
  padding: 0 8px;
  color: #666;
  font-size: 14px;
}

.pdf-content {
  flex: 1;
  overflow: auto;
  background: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 20px;
  position: relative;
  transition: transform 0.1s ease-out;
}

.pdf-viewer-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-width: 100%;
  min-height: 100%;
  position: relative;
}

.pdf-page {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  background: white;
  /* 移除最大宽度和高度限制，让PDF能够根据缩放自由调整大小 */
  /* max-width: 100%; */
  /* max-height: 100%; */
  display: block;
  margin: 0 auto;
}

.pdf-waiting {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #666;
  font-size: 14px;
}

.pdf-loading,
.pdf-error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #666;
}

.loading-icon {
  font-size: 48px;
  color: #409eff;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.error-icon {
  font-size: 48px;
  color: #f56c6c;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 滚动条样式 */
.pdf-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.pdf-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.pdf-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.pdf-content::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pdf-toolbar {
    flex-direction: column;
    gap: 8px;
    padding: 8px 12px;
  }
  
  .toolbar-left,
  .toolbar-center,
  .toolbar-right {
    flex-wrap: wrap;
    justify-content: center;
    gap: 4px;
  }
  
  .pdf-content {
    padding: 10px;
  }
  
  .page-input {
    width: 50px !important;
  }
  
  .wheel-tip {
    display: none;
  }
}

@media (max-width: 480px) {
  .toolbar-center {
    flex-direction: column;
    gap: 4px;
  }
  
  .pdf-content {
    padding: 5px;
  }
}

/* PDF文字选择样式 - 只保留选择高亮，让PDF.js自然处理文字层定位 */
:deep(.textLayer ::selection) {
  background: rgba(0, 123, 255, 0.3) !important;
}

:deep(.textLayer ::-moz-selection) {
  background: rgba(0, 123, 255, 0.3) !important;
}
</style> 