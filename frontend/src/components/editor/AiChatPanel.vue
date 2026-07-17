<template>
  <transition name="ai-chat-slide">
    <aside v-if="visible" class="ai-chat-panel" role="dialog" aria-label="DBLens AI 助手">
      <header class="ai-chat-header">
        <div>
          <span class="ai-chat-kicker">DBLens AI</span>
          <strong>智能助手</strong>
          <small>{{ activeContext.database || '未选择数据库' }}</small>
        </div>
        <button class="ai-icon-btn" type="button" title="关闭" @click="closePanel">
          <el-icon><Close /></el-icon>
        </button>
      </header>

      <section class="ai-chat-messages">
        <div v-if="!messages.length" class="ai-chat-empty">
          <strong>可以直接描述要查询或分析的问题。</strong>
          <span>我会结合当前 SQL、选中内容和已加载表结构生成建议，不会自动执行语句。</span>
        </div>

        <article v-for="(message, index) in messages" :key="index" class="ai-message" :class="message.role">
          <span class="ai-message-role">{{ message.role === 'user' ? '你' : 'AI' }}</span>
          <pre>{{ message.content }}</pre>
          <div v-if="message.role === 'assistant' && extractSqlBlocks(message.content).length" class="ai-sql-actions">
            <div v-for="(sql, sqlIndex) in extractSqlBlocks(message.content)" :key="sqlIndex" class="ai-sql-block">
              <code>{{ sql }}</code>
              <div>
                <button type="button" @click="copySql(sql)">复制</button>
                <button type="button" @click="$emit('insert-sql', sql)">插入</button>
                <button type="button" class="primary" @click="$emit('replace-sql', sql)">替换</button>
              </div>
            </div>
          </div>
        </article>
      </section>

      <footer class="ai-chat-input">
        <textarea
          v-model="draft"
          :disabled="streaming"
          placeholder="例如：帮我写一个查询分类树的 SQL"
          @keydown.enter.exact.prevent="sendMessage"
        />
        <div class="ai-chat-actions">
          <span>{{ activeContext.selectedSql ? '已带入选中 SQL' : '已带入当前编辑器 SQL' }}</span>
          <button v-if="streaming" type="button" @click="stopStreaming">停止</button>
          <button v-else type="button" class="primary" :disabled="!draft.trim()" @click="sendMessage">
            <el-icon><Promotion /></el-icon>
            发送
          </button>
        </div>
      </footer>
    </aside>
  </transition>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Close, Promotion } from '@element-plus/icons-vue'
import { streamAiChat } from '@/api/ai'
import { appendAiDelta, extractSqlBlocks, type AiChatContext, type AiMessage } from '@/utils/aiChat'

const props = defineProps<{
  visible: boolean
  context: AiChatContext
  getContext?: () => AiChatContext
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'insert-sql', sql: string): void
  (e: 'replace-sql', sql: string): void
}>()

const draft = ref('')
const messages = ref<AiMessage[]>([])
const streaming = ref(false)
let abortController: AbortController | null = null

const activeContext = computed(() => props.context)

async function sendMessage() {
  const text = draft.value.trim()
  if (!text || streaming.value) return

  const context = resolveActiveContext()
  const history = messages.value.slice(-8)
  messages.value = [...messages.value, { role: 'user', content: text }]
  draft.value = ''
  streaming.value = true
  abortController = new AbortController()

  try {
    await streamAiChat({
      ...context,
      message: text,
      history,
    }, {
      onDelta(content) {
        messages.value = appendAiDelta(messages.value, content)
      },
      onError(message) {
        messages.value = appendAiDelta(messages.value, `\n${message}`)
      },
    }, abortController.signal)
  } catch (error: any) {
    if (error?.name !== 'AbortError') {
      ElMessage.error(error?.message || 'AI 请求失败')
    }
  } finally {
    streaming.value = false
    abortController = null
  }
}

function stopStreaming() {
  abortController?.abort()
  streaming.value = false
}

function closePanel() {
  emit('update:visible', false)
}

function resolveActiveContext() {
  return props.getContext?.() ?? props.context
}

async function copySql(sql: string) {
  await navigator.clipboard?.writeText(sql)
  ElMessage.success('已复制 SQL')
}
</script>

<style scoped>
.ai-chat-panel {
  position: fixed;
  top: 72px;
  right: 18px;
  bottom: 24px;
  z-index: 80;
  display: flex;
  flex-direction: column;
  width: min(430px, calc(100vw - 40px));
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: 0 18px 46px rgba(15, 23, 42, 0.22);
  overflow: hidden;
}

.ai-chat-slide-enter-active,
.ai-chat-slide-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.ai-chat-slide-enter-from,
.ai-chat-slide-leave-to {
  opacity: 0;
  transform: translateX(16px);
}

.ai-chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 14px 12px;
  border-bottom: 1px solid var(--border-muted);
}

.ai-chat-header div {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.ai-chat-kicker {
  color: var(--accent-blue);
  font-size: 11px;
  font-weight: 700;
}

.ai-chat-header strong {
  color: var(--text-primary);
  font-size: 16px;
}

.ai-chat-header small {
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ai-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
}

.ai-chat-messages {
  flex: 1;
  overflow: auto;
  padding: 14px;
  background: var(--bg-secondary);
}

.ai-chat-empty {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  line-height: 1.6;
}

.ai-chat-empty strong {
  color: var(--text-primary);
}

.ai-message {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.ai-message-role {
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
}

.ai-message pre {
  margin: 0;
  padding: 10px 12px;
  max-width: 100%;
  border: 1px solid var(--border-muted);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.55;
}

.ai-message.user pre {
  border-color: rgba(88, 166, 255, 0.35);
  background: var(--glow-blue);
}

.ai-sql-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-sql-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.ai-sql-block code {
  max-height: 150px;
  overflow: auto;
  white-space: pre;
  color: var(--text-primary);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
}

.ai-sql-block div,
.ai-chat-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-sql-block button,
.ai-chat-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-height: 28px;
  padding: 4px 10px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
}

.ai-sql-block button.primary,
.ai-chat-actions button.primary {
  border-color: var(--accent-blue);
  background: var(--accent-blue);
  color: #fff;
}

.ai-chat-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border-muted);
  background: var(--bg-primary);
}

.ai-chat-input textarea {
  width: 100%;
  min-height: 86px;
  resize: vertical;
  padding: 10px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-family: inherit;
  line-height: 1.5;
  outline: none;
}

.ai-chat-actions {
  justify-content: space-between;
}

.ai-chat-actions span {
  color: var(--text-muted);
  font-size: 12px;
}
</style>
