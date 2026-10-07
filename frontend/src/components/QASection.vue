<template>
  <div class="qa-section">
    <h2>Intelligent Q&A</h2>

    <div class="chat-container">
      <div class="messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          Enter your question to start the conversation
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.type]"
        >
          <div class="message-content">
            <div class="message-text">{{ msg.text }}</div>
            <div v-if="msg.sources && msg.sources.length > 0" class="sources">
              <el-divider content-position="left">References</el-divider>
              <div v-for="(source, idx) in msg.sources" :key="idx" class="source-item">
                <p><strong>Source {{ idx + 1 }}:</strong> {{ source.metadata.title }}</p>
                <p class="source-text">{{ source.document.substring(0, 200) }}...</p>
                <p class="score">Relevance: {{ (source.score * 100).toFixed(2) }}%</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="question"
          placeholder="Enter your question..."
          @keyup.enter="askQuestion"
          :disabled="loading"
          class="question-input"
        >
          <template #append>
            <el-button
              type="primary"
              @click="askQuestion"
              :loading="loading"
              class="ask-btn"
            >
              {{ loading ? 'Thinking...' : 'Ask' }}
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { askQuestion as askQuestionAPI } from '../api'

const question = ref('')
const messages = ref([])
const loading = ref(false)
const messagesContainer = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const askQuestion = async () => {
  if (!question.value.trim()) {
    ElMessage.warning('Please enter a question')
    return
  }

  const userQuestion = question.value
  messages.value.push({
    type: 'user',
    text: userQuestion
  })

  question.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const response = await askQuestionAPI(userQuestion)
    messages.value.push({
      type: 'assistant',
      text: response.data.answer,
      sources: response.data.sources
    })
  } catch (error) {
    ElMessage.error(error.response?.data?.error || 'Q&A failed')
    messages.value.push({
      type: 'assistant',
      text: 'Sorry, an error occurred while answering the question. Please try again later.'
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.qa-section {
  padding: 32px;
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.3s ease;
}

.qa-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  margin-bottom: 24px;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.messages {
  height: 70dvh;
  overflow-y: auto;
  padding: 20px;
  background: #F5F7FA;
  border-radius: 8px;
  margin-bottom: 20px;
  scroll-behavior: smooth;
}

.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: #E4E7ED;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb {
  background: #C0C4CC;
  border-radius: 3px;
  transition: background 0.3s ease;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.empty-state {
  text-align: center;
  color: #909399;
  padding: 60px 20px;
  font-size: 15px;
}

.message {
  margin-bottom: 20px;
  animation: messageSlideIn 0.3s ease;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user .message-content {
  background: #409EFF;
  color: white;
  margin-left: auto;
  max-width: 70%;
}

.message.assistant .message-content {
  background: #FFFFFF;
  color: #303133;
  max-width: 85%;
  border: 1px solid #E4E7ED;
}

.message-content {
  padding: 16px 18px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.message-content:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
}

.message-text {
  line-height: 1.7;
  white-space: pre-wrap;
  font-size: 14px;
}

.sources {
  margin-top: 16px;
}

.source-item {
  background: #F5F7FA;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  font-size: 13px;
  border-left: 3px solid #409EFF;
  transition: all 0.2s ease;
}

.source-item:hover {
  background: #ECF5FF;
  transform: translateX(4px);
}

.source-text {
  color: #606266;
  margin: 8px 0;
  line-height: 1.6;
}

.score {
  color: #909399;
  font-size: 12px;
  font-weight: 500;
}

.input-area {
  margin-top: auto;
}

.question-input {
  transition: all 0.3s ease;
}

.question-input :deep(.el-input__wrapper) {
  transition: all 0.3s ease;
}

.question-input :deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.question-input :deep(.el-input__inner) {
  font-size: 14px;
}

.ask-btn {
  transition: all 0.3s ease;
}

.ask-btn:hover {
  transform: translateY(-1px);
}

.ask-btn:active {
  transform: translateY(0);
}
</style>

