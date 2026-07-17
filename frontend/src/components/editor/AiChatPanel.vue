<template>
  <transition name="ai-chat-slide">
    <aside v-if="visible" class="ai-chat-panel" role="dialog" aria-label="DBLens AI 助手">
      <header class="ai-chat-header">
        <div class="ai-chat-title">
          <span class="ai-chat-badge">AI</span>
          <div>
            <strong>DBLens 助手</strong>
            <small>基于当前数据库上下文</small>
          </div>
        </div>
        <button class="ai-icon-btn" type="button" title="关闭" @click="closePanel">
          <el-icon><Close /></el-icon>
        </button>
      </header>

      <div class="ai-context-strip">
        <span>{{ schemaCountText }}</span>
        <span>{{ activeContext.selectedSql ? '选中 SQL' : '完整编辑器' }}</span>
        <span>{{ streaming ? '生成中' : '待命' }}</span>
      </div>

      <section ref="messagesRef" class="ai-chat-messages">
        <div v-if="!messages.length" class="ai-chat-empty ai-assistant-home">
          <div class="ai-home-title">
            <span>我能帮你做</span>
            <strong>{{ activeContext.database || '当前数据库' }}</strong>
          </div>
          <div class="ai-prompt-rail">
            <button
              v-for="prompt in promptSamples"
              :key="prompt.title"
              class="ai-prompt-card"
              type="button"
              @click="usePrompt(prompt.prompt)"
            >
              <strong>{{ prompt.title }}</strong>
              <span>{{ prompt.description }}</span>
            </button>
          </div>
          <div class="ai-home-suggestion">
            <span>你也可以直接输入：帮我根据当前 SQL 生成一个更安全的查询。</span>
          </div>
        </div>

        <article v-for="(message, index) in messages" :key="index" class="ai-message" :class="message.role">
          <span class="ai-message-role">{{ message.role === 'user' ? '你' : 'AI' }}</span>
          <pre>{{ message.content }}</pre>
          <div v-if="message.role === 'assistant' && extractSqlBlocks(message.content).length" class="ai-sql-actions">
            <div v-for="(sql, sqlIndex) in extractSqlBlocks(message.content)" :key="sqlIndex" class="ai-sql-block">
              <code>{{ sql }}</code>
              <div class="ai-sql-toolbar">
                <button type="button" @click="copySql(sql)">复制</button>
                <button type="button" @click="$emit('insert-sql', sql)">插入</button>
                <button type="button" class="primary" @click="$emit('replace-sql', sql)">替换</button>
              </div>
            </div>
          </div>
        </article>
        <div v-if="streaming" class="ai-stream-indicator">
          <span />
          <span />
          <span />
        </div>
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
import { computed, nextTick, ref, watch } from 'vue'
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
const messagesRef = ref<HTMLElement>()
const streaming = ref(false)
let abortController: AbortController | null = null

const activeContext = computed(() => props.context)
const promptSamples = [
  {
    title: 'SQL 生成',
    description: '按自然语言生成查询',
    prompt: '根据当前数据库结构，帮我生成一个查询 SQL。',
  },
  {
    title: 'SQL 解释',
    description: '说明当前语句逻辑',
    prompt: '解释当前 SQL 的执行意图和关键条件。',
  },
  {
    title: '风险检查',
    description: '识别更新和删除风险',
    prompt: '检查当前 SQL 是否有风险，并给出更安全的写法。',
  },
  {
    title: '结构分析',
    description: '梳理表关系和字段',
    prompt: '根据当前库的表结构，帮我分析相关表和字段该怎么使用。',
  },
]
const schemaCountText = computed(() => {
  const count = activeContext.value.schema?.tables.length ?? 0
  return count ? `${count} 张表` : '未加载结构'
})

watch(messages, () => {
  nextTick(() => {
    const target = messagesRef.value
    if (target) target.scrollTop = target.scrollHeight
  })
}, { deep: true })

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

function usePrompt(prompt: string) {
  draft.value = prompt
}

async function copySql(sql: string) {
  await navigator.clipboard?.writeText(sql)
  ElMessage.success('已复制 SQL')
}
</script>

<style scoped>
.ai-chat-panel {
  position: fixed;
  top: 68px;
  right: 24px;
  bottom: 76px;
  z-index: 80;
  display: flex;
  flex-direction: column;
  width: min(456px, calc(100vw - 32px));
  background: color-mix(in srgb, var(--bg-primary) 96%, #f8fbff);
  border: 1px solid color-mix(in srgb, var(--border-default) 78%, #4f8cff);
  border-radius: 8px;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.24), 0 0 0 1px rgba(255, 255, 255, 0.48) inset;
  overflow: hidden;
}

.ai-chat-slide-enter-active,
.ai-chat-slide-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.ai-chat-slide-enter-from,
.ai-chat-slide-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.98);
}

.ai-chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 14px 12px 16px;
  border-bottom: 1px solid var(--border-muted);
  background:
    linear-gradient(180deg, rgba(88, 166, 255, 0.09), transparent 72%),
    var(--bg-primary);
}

.ai-chat-title {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.ai-chat-title div {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.ai-chat-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #0f5fd7;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0;
  box-shadow: 0 8px 18px rgba(15, 95, 215, 0.28);
}

.ai-chat-header strong {
  color: var(--text-primary);
  font-size: 14px;
  letter-spacing: 0;
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
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
}

.ai-icon-btn:hover {
  color: var(--accent-blue);
  border-color: rgba(88, 166, 255, 0.55);
  background: var(--glow-blue);
}

.ai-context-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  padding: 1px;
  background: var(--border-muted);
}

.ai-context-strip span {
  min-width: 0;
  padding: 7px 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 11px;
  line-height: 16px;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ai-chat-messages {
  flex: 1;
  overflow: auto;
  padding: 14px;
  background:
    linear-gradient(rgba(148, 163, 184, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.07) 1px, transparent 1px),
    var(--bg-secondary);
  background-size: 18px 18px;
}

.ai-chat-empty {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px;
  border: 1px solid var(--border-muted);
  border-radius: 8px;
  background: color-mix(in srgb, var(--bg-primary) 92%, #eef6ff);
  color: var(--text-secondary);
  line-height: 1.6;
}

.ai-assistant-home {
  min-height: 100%;
  justify-content: flex-start;
}

.ai-home-title {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.ai-home-title span {
  color: var(--text-secondary);
  font-size: 13px;
}

.ai-home-title strong {
  color: var(--text-primary);
  font-size: 18px;
  line-height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ai-prompt-rail {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.ai-prompt-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  min-height: 74px;
  padding: 11px 12px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 12px;
  text-align: left;
  cursor: pointer;
}

.ai-prompt-card strong {
  color: var(--text-primary);
  font-size: 13px;
  line-height: 18px;
}

.ai-prompt-card span {
  color: var(--text-muted);
  line-height: 17px;
}

.ai-prompt-card:hover {
  transform: translateY(-1px);
  color: var(--text-primary);
  border-color: rgba(88, 166, 255, 0.55);
  background: var(--glow-blue);
}

.ai-home-suggestion {
  padding: 10px 11px;
  border-radius: 8px;
  background: color-mix(in srgb, var(--bg-secondary) 78%, #eef6ff);
  color: var(--text-muted);
  font-size: 12px;
  line-height: 18px;
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
  letter-spacing: 0;
}

.ai-message pre {
  margin: 0;
  padding: 11px 12px;
  max-width: 100%;
  border: 1px solid var(--border-muted);
  border-radius: 8px;
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
  background: color-mix(in srgb, var(--glow-blue) 72%, var(--bg-primary));
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
  padding: 0;
  border: 1px solid color-mix(in srgb, var(--border-default) 78%, #0f5fd7);
  border-radius: 8px;
  background: #0b1220;
  overflow: hidden;
}

.ai-sql-block code {
  max-height: 150px;
  overflow: auto;
  padding: 12px;
  white-space: pre;
  color: #d8e6ff;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.55;
}

.ai-sql-toolbar,
.ai-chat-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-sql-toolbar {
  justify-content: flex-end;
  padding: 8px;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.88);
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
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
}

.ai-sql-block button.primary,
.ai-chat-actions button.primary {
  border-color: #0f5fd7;
  background: #0f5fd7;
  color: #fff;
}

.ai-sql-toolbar button {
  border-color: rgba(148, 163, 184, 0.32);
  background: rgba(15, 23, 42, 0.4);
  color: #d8e6ff;
}

.ai-sql-toolbar button.primary {
  border-color: #58a6ff;
  background: #1f6feb;
}

.ai-sql-block button:disabled,
.ai-chat-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.ai-stream-indicator {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  width: fit-content;
  padding: 9px 11px;
  border: 1px solid var(--border-muted);
  border-radius: 8px;
  background: var(--bg-primary);
}

.ai-stream-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--accent-blue);
  animation: ai-pulse 1s infinite ease-in-out;
}

.ai-stream-indicator span:nth-child(2) {
  animation-delay: 0.14s;
}

.ai-stream-indicator span:nth-child(3) {
  animation-delay: 0.28s;
}

@keyframes ai-pulse {
  0%, 80%, 100% {
    opacity: 0.28;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-3px);
  }
}

.ai-chat-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 14px 14px;
  border-top: 1px solid var(--border-muted);
  background: var(--bg-primary);
}

.ai-chat-input textarea {
  width: 100%;
  min-height: 86px;
  max-height: 180px;
  resize: vertical;
  padding: 11px 12px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-family: inherit;
  line-height: 1.5;
  outline: none;
}

.ai-chat-input textarea:focus {
  border-color: rgba(88, 166, 255, 0.78);
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.14);
}

.ai-chat-actions {
  justify-content: space-between;
}

.ai-chat-actions span {
  color: var(--text-muted);
  font-size: 12px;
}

@media (max-width: 720px) {
  .ai-chat-panel {
    right: 12px;
    bottom: 70px;
    width: calc(100vw - 24px);
    height: min(78vh, 680px);
  }
}
</style>
