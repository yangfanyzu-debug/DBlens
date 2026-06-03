<template>
  <div class="editor-tab">
    <EditorToolbar :tab="tab" @execute="onExecute" @kill="onKill" @format="onFormat" @db-change="onDbChange" />
    <div ref="assistRef" class="query-assist-shell">
      <div class="query-assist">
        <div class="assist-switch" role="tablist" aria-label="查询助手">
          <button class="assist-btn" :class="{ active: assistMode === 'history' }" @click="toggleAssist('history')">
            <el-icon><Clock /></el-icon>
            历史
            <span class="assist-count">{{ currentHistory.length }}</span>
          </button>
          <button class="assist-btn" :class="{ active: assistMode === 'saved' }" @click="toggleAssist('saved')">
            <el-icon><Star /></el-icon>
            收藏
            <span class="assist-count">{{ savedQueries.length }}</span>
          </button>
        </div>
        <button class="assist-save-btn" @click="saveCurrentSql">
          <el-icon><CollectionTag /></el-icon>
          收藏当前
        </button>
      </div>
      <transition name="query-library-slide">
        <aside v-if="assistMode" class="query-library-drawer" role="dialog" aria-label="查询库">
          <div class="library-header">
            <div class="library-heading">
              <span class="library-kicker">Query Library</span>
              <strong>{{ assistMode === 'history' ? '查询历史' : '收藏查询' }}</strong>
            </div>
            <button
              v-if="assistMode === 'history' && currentHistory.length"
              class="library-text-btn"
              @click="queryStore.clearHistory()"
            >
              清空历史
            </button>
            <button class="library-close-btn" @click="assistMode = null">收起</button>
          </div>

          <div class="library-tabs" role="tablist" aria-label="查询库类型">
            <button :class="{ active: assistMode === 'history' }" @click="setAssistMode('history')">
              历史
              <span>{{ currentHistory.length }}</span>
            </button>
            <button :class="{ active: assistMode === 'saved' }" @click="setAssistMode('saved')">
              收藏
              <span>{{ savedQueries.length }}</span>
            </button>
          </div>

          <el-input
            v-model="assistSearch"
            class="library-search"
            size="small"
            clearable
            placeholder="搜索 SQL / 库名 / 标题"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <div class="library-filters">
            <button :class="{ active: assistScope === 'all' }" @click="assistScope = 'all'">全部</button>
            <button :class="{ active: assistScope === 'connection' }" @click="assistScope = 'connection'">当前连接</button>
            <button :class="{ active: assistScope === 'database' }" @click="assistScope = 'database'">当前库</button>
          </div>

          <div class="library-body">
            <div class="library-list">
              <template v-if="assistMode === 'history'">
                <button
                  v-for="entry in visibleHistory"
                  :key="entry.key"
                  class="library-item"
                  :class="{ selected: selectedQuery?.key === entry.key }"
                  @click="selectQuery(entry)"
                >
                  <span class="library-item-title">{{ entry.title }}</span>
                  <span class="library-item-sql">{{ compactSql(entry.sql) }}</span>
                  <span class="library-item-meta">
                    <span>{{ entry.database || '默认库' }}</span>
                    <span>{{ formatAssistTime(entry.time) }}</span>
                  </span>
                </button>
                <span v-if="!filteredHistory.length" class="library-empty">暂无匹配的查询历史</span>
              </template>
              <template v-else>
                <button
                  v-for="item in visibleSavedQueries"
                  :key="item.key"
                  class="library-item"
                  :class="{ selected: selectedQuery?.key === item.key }"
                  @click="selectQuery(item)"
                >
                  <span class="library-item-title">{{ item.title }}</span>
                  <span class="library-item-sql">{{ compactSql(item.sql) }}</span>
                  <span class="library-item-meta">
                    <span>收藏</span>
                    <span>{{ formatAssistTime(item.time) }}</span>
                  </span>
                </button>
                <span v-if="!filteredSavedQueries.length" class="library-empty">暂无匹配的收藏查询</span>
              </template>
              <div v-if="assistHiddenCount > 0" class="library-more">
                还有 {{ assistHiddenCount }} 条未显示，继续搜索可快速定位
              </div>
            </div>

            <div class="library-preview">
              <template v-if="selectedQuery">
                <div class="library-preview-head">
                  <div>
                    <span class="library-preview-label">预览</span>
                    <strong>{{ selectedQuery.title }}</strong>
                  </div>
                  <button
                    v-if="selectedQuery.source === 'saved'"
                    class="library-text-btn danger"
                    @click="removeSavedSql(selectedQuery.sql)"
                  >
                    移除收藏
                  </button>
                  <button
                    v-else
                    class="library-text-btn"
                    @click="saveSql(selectedQuery.sql)"
                  >
                    {{ isSavedSql(selectedQuery.sql) ? '已收藏' : '收藏' }}
                  </button>
                </div>
                <pre>{{ selectedQuery.sql }}</pre>
                <div class="library-preview-actions">
                  <button @click="applySelectedSql">替换</button>
                  <button @click="insertSelectedSql">插入</button>
                  <button @click="copySelectedSql">复制</button>
                  <button class="primary" @click="executeSelectedSql">执行</button>
                </div>
              </template>
              <span v-else class="library-preview-empty">选择一条 SQL 查看预览</span>
            </div>
          </div>
        </aside>
      </transition>
    </div>
    <div class="editor-body" ref="bodyRef">
      <div class="editor-pane" :style="{ height: editorHeight + 'px' }">
        <MonacoEditor
          ref="monacoRef"
          :conn-id="tab.connId"
          :database="currentDb"
          @execute="onExecute"
        />
      </div>
      <div class="resize-handle" @mousedown="startResize" />
      <div class="results-pane" :style="{ height: resultsHeight + 'px' }">
        <ResultsPane :query-id="currentQueryId" :conn-id="tab.connId" :database="currentDb" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, CollectionTag, Search, Star } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import type { Tab } from '@/stores/tabs'
import { useQueryStore } from '@/stores/query'
import { useConnectionsStore } from '@/stores/connections'
import * as queryApi from '@/api/query'
import { QueryWebSocket } from '@/utils/websocket'
import { assessSqlRisk } from '@/utils/sqlRisk'
import { getConnectionEndpoint, getConnectionEnvironment } from '@/utils/connectionExperience'
import EditorToolbar from './EditorToolbar.vue'
import MonacoEditor from './MonacoEditor.vue'
import ResultsPane from './ResultsPane.vue'

const props = defineProps<{ tab: Tab }>()

interface LibraryItem {
  key: string
  source: 'history' | 'saved'
  sql: string
  title: string
  database: string
  connId: string
  time: number
}

const queryStore = useQueryStore()
const connStore = useConnectionsStore()
const { savedQueries } = storeToRefs(queryStore)
const monacoRef = ref<any>(null)
const bodyRef = ref<HTMLElement>()
const assistRef = ref<HTMLElement>()
const currentQueryId = ref<string>('')
const currentDb = ref(props.tab.database ?? '')
const currentConnection = computed(() => connStore.connections.find(c => c.id === props.tab.connId))
const assistMode = ref<'history' | 'saved' | null>(null)
const assistSearch = ref('')
const assistScope = ref<'all' | 'connection' | 'database'>('connection')
const selectedQueryKey = ref('')
const ASSIST_LIMIT = 40
const currentHistory = computed(() =>
  queryStore.history
    .filter(entry => entry.connId === props.tab.connId),
)
const filteredHistory = computed(() =>
  queryStore.history
    .map((entry): LibraryItem => ({
      key: `history-${entry.ran_at}-${entry.connId}-${entry.sql}`,
      source: 'history',
      sql: entry.sql,
      title: firstSqlLine(entry.sql),
      database: entry.database,
      connId: entry.connId,
      time: entry.ran_at,
    }))
    .filter(entry => matchesAssistScope(entry))
    .filter(entry => matchesAssistSearch(entry.sql, entry.database)),
)
const filteredSavedQueries = computed(() =>
  savedQueries.value
    .map((item): LibraryItem => ({
      key: item.id,
      source: 'saved',
      sql: item.sql,
      title: item.title,
      database: '',
      connId: '',
      time: item.saved_at,
    }))
    .filter(item => matchesAssistSearch(item.sql, item.title)),
)
const visibleHistory = computed(() => filteredHistory.value.slice(0, ASSIST_LIMIT))
const visibleSavedQueries = computed(() => filteredSavedQueries.value.slice(0, ASSIST_LIMIT))
const assistTotalCount = computed(() => assistMode.value === 'history' ? currentHistory.value.length : savedQueries.value.length)
const assistVisibleCount = computed(() => assistMode.value === 'history' ? filteredHistory.value.length : filteredSavedQueries.value.length)
const assistHiddenCount = computed(() => Math.max(0, assistVisibleCount.value - ASSIST_LIMIT))
const activeLibraryItems = computed(() => assistMode.value === 'history' ? visibleHistory.value : visibleSavedQueries.value)
const selectedQuery = computed(() =>
  activeLibraryItems.value.find(item => item.key === selectedQueryKey.value) ?? activeLibraryItems.value[0] ?? null,
)

const editorHeight = ref(300)
const resultsHeight = ref(200)
let wsClient: QueryWebSocket | null = null

async function onExecute(sql?: string) {
  const code = sql ?? monacoRef.value?.getSelectedTextOrValue?.() ?? monacoRef.value?.getValue() ?? ''
  if (!code.trim()) return
  if (!(await confirmRiskySql(code))) return
  const queryId = uuidv4()
  currentQueryId.value = queryId
  queryStore.setRunning(queryId)
  wsClient?.stop()
  wsClient = new QueryWebSocket(queryId)
  await wsClient.connect()
  await queryApi.executeQuery(props.tab.connId, currentDb.value, code, queryId)
  queryStore.recordHistory({
    sql: code,
    connId: props.tab.connId,
    database: currentDb.value,
    ran_at: Date.now(),
  })
}

async function confirmRiskySql(sql: string): Promise<boolean> {
  const risk = assessSqlRisk(sql)
  if (!risk.risky) return true

  const conn = currentConnection.value
  const env = getConnectionEnvironment(conn ?? {})
  const target = conn ? getConnectionEndpoint({ ...conn, database: currentDb.value || conn.database }) : currentDb.value
  const detail = [
    ...risk.reasons,
    `目标：${conn?.name ?? props.tab.connId}（${env.label}）`,
    target ? `地址：${target}` : '',
  ].filter(Boolean).join('\n')

  try {
    await ElMessageBox.confirm(detail, risk.title, {
      type: 'warning',
      confirmButtonText: '继续执行',
      cancelButtonText: '取消',
    })
    return true
  } catch {
    return false
  }
}

async function onKill() {
  if (currentQueryId.value) {
    await queryApi.killQuery(currentQueryId.value)
  }
}

function onFormat() {
  monacoRef.value?.format()
}

function onDbChange(db: string) {
  currentDb.value = db
}

function setAssistMode(mode: 'history' | 'saved') {
  assistMode.value = mode
  selectedQueryKey.value = ''
}

function toggleAssist(mode: 'history' | 'saved') {
  const closing = assistMode.value === mode
  assistMode.value = closing ? null : mode
  assistSearch.value = ''
  selectedQueryKey.value = ''
}

function selectQuery(item: LibraryItem) {
  selectedQueryKey.value = item.key
}

function applySql(sql: string) {
  monacoRef.value?.setValue(sql)
  assistMode.value = null
}

function applySelectedSql() {
  if (!selectedQuery.value) return
  applySql(selectedQuery.value.sql)
}

function insertSelectedSql() {
  if (!selectedQuery.value) return
  monacoRef.value?.insertText?.(selectedQuery.value.sql)
  assistMode.value = null
}

async function copySelectedSql() {
  if (!selectedQuery.value) return
  await navigator.clipboard?.writeText(selectedQuery.value.sql)
  ElMessage.success('已复制 SQL')
}

function executeSelectedSql() {
  if (!selectedQuery.value) return
  onExecute(selectedQuery.value.sql)
  assistMode.value = null
}

function saveCurrentSql() {
  const code = monacoRef.value?.getSelectedTextOrValue?.() ?? monacoRef.value?.getValue?.() ?? ''
  if (!code.trim()) {
    ElMessage.warning('没有可收藏的 SQL')
    return
  }
  saveSql(code)
  setAssistMode('saved')
}

function saveSql(sql: string) {
  if (isSavedSql(sql)) {
    ElMessage.info('已在收藏中')
    return
  }
  queryStore.toggleSaved(sql)
  ElMessage.success('已收藏')
}

function removeSavedSql(sql: string) {
  queryStore.toggleSaved(sql)
  ElMessage.success('已移除收藏')
}

function isSavedSql(sql: string) {
  const target = sql.trim()
  return savedQueries.value.some(item => item.sql.trim() === target)
}

function firstSqlLine(sql: string) {
  return sql.trim().split('\n').find(line => line.trim())?.trim() || '空 SQL'
}

function compactSql(sql: string) {
  return sql.trim().replace(/\s+/g, ' ').slice(0, 160) || '空 SQL'
}

function matchesAssistSearch(sql: string, secondary = '') {
  const keyword = assistSearch.value.trim().toLowerCase()
  if (!keyword) return true
  return `${sql} ${secondary}`.toLowerCase().includes(keyword)
}

function matchesAssistScope(item: LibraryItem) {
  if (assistScope.value === 'all') return true
  if (item.connId !== props.tab.connId) return false
  if (assistScope.value === 'database') return item.database === currentDb.value
  return true
}

function formatAssistTime(timestamp: number) {
  return new Date(timestamp).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function onAssistOutsideClick(e: MouseEvent) {
  if (!assistMode.value) return
  const target = e.target as Node | null
  if (target && assistRef.value?.contains(target)) return
  assistMode.value = null
}

// Resize handle
let resizing = false
let startY = 0
let startEditorH = 0

function startResize(e: MouseEvent) {
  resizing = true
  startY = e.clientY
  startEditorH = editorHeight.value
  document.addEventListener('mousemove', doResize)
  document.addEventListener('mouseup', stopResize)
}

function doResize(e: MouseEvent) {
  if (!resizing || !bodyRef.value) return
  const delta = e.clientY - startY
  const totalH = bodyRef.value.clientHeight - 6
  editorHeight.value = Math.max(80, Math.min(totalH - 80, startEditorH + delta))
  resultsHeight.value = totalH - editorHeight.value
  monacoRef.value?.layout()
}

function stopResize() {
  resizing = false
  document.removeEventListener('mousemove', doResize)
  document.removeEventListener('mouseup', stopResize)
  monacoRef.value?.layout()
}

onMounted(() => {
  if (bodyRef.value) {
    const h = bodyRef.value.clientHeight - 6
    editorHeight.value = Math.floor(h * 0.55)
    resultsHeight.value = h - editorHeight.value
  }
  nextTick(() => monacoRef.value?.layout())
  document.addEventListener('mousedown', onAssistOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', onAssistOutsideClick)
  wsClient?.stop()
})
</script>

<style scoped>
.editor-tab { display: flex; flex-direction: column; height: 100%; }

.query-assist-shell {
  position: relative;
  z-index: 12;
  flex-shrink: 0;
}

.query-assist {
  display: flex;
  align-items: center;
  gap: 6px;
  min-height: 38px;
  padding: 5px 12px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-muted);
  flex-shrink: 0;
}

.assist-switch {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px;
  border: 1px solid var(--border-muted);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
}

.assist-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-height: 26px;
  padding: 3px 9px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
}

.assist-btn.active {
  color: var(--accent-blue);
  background: var(--glow-blue);
}

.assist-count {
  min-width: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 10px;
  line-height: 16px;
  text-align: center;
}

.assist-save-btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-height: 28px;
  padding: 3px 10px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
}

.assist-save-btn:hover {
  color: var(--accent-blue);
  border-color: rgba(88, 166, 255, 0.45);
  background: var(--glow-blue);
}

.query-library-drawer {
  position: absolute;
  top: calc(100% + 8px);
  right: 12px;
  z-index: 40;
  display: flex;
  flex-direction: column;
  width: clamp(420px, 34vw, 560px);
  max-width: calc(100vw - 280px);
  height: min(640px, calc(100vh - 174px));
  min-height: 420px;
  padding: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.18);
}

.query-library-slide-enter-active,
.query-library-slide-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.query-library-slide-enter-from,
.query-library-slide-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

.library-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.library-heading {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.library-kicker,
.library-preview-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0;
  color: var(--text-muted);
}

.library-heading strong,
.library-preview-head strong {
  color: var(--text-primary);
  font-size: 13px;
  line-height: 18px;
}

.library-text-btn,
.library-close-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
}

.library-text-btn:hover,
.library-close-btn:hover {
  color: var(--accent-blue);
}

.library-text-btn.danger:hover {
  color: var(--accent-red);
}

.library-tabs,
.library-filters {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  gap: 4px;
  padding: 2px;
  border: 1px solid var(--border-muted);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  margin-bottom: 8px;
}

.library-tabs button,
.library-filters button {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  min-height: 25px;
  padding: 3px 8px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
}

.library-tabs button.active,
.library-filters button.active {
  background: var(--glow-blue);
  color: var(--accent-blue);
}

.library-tabs span {
  min-width: 17px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 10px;
  line-height: 15px;
  text-align: center;
}

.library-search {
  margin-bottom: 8px;
}

.library-search :deep(.el-input__wrapper) {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 1px var(--border-muted) inset;
}

.library-body {
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
  gap: 10px;
}

.library-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 0;
  flex: 1;
  overflow-y: auto;
  padding-right: 2px;
}

.library-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  min-height: 72px;
  padding: 8px 10px;
  border: 1px solid var(--border-muted);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  text-align: left;
  font-family: inherit;
  cursor: pointer;
}

.library-item:hover,
.library-item.selected {
  border-color: rgba(88, 166, 255, 0.5);
  background: var(--glow-blue);
}

.library-item-title,
.library-item-sql {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.library-item-title {
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
}

.library-item-sql {
  color: var(--text-secondary);
  font-size: 12px;
}

.library-item-meta {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  color: var(--text-muted);
  font-size: 11px;
}

.library-empty,
.library-more,
.library-preview-empty {
  padding: 14px 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
}

.library-more {
  padding: 4px 0 0;
  font-size: 11px;
}

.library-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 170px;
  padding-top: 10px;
  border-top: 1px solid var(--border-muted);
}

.library-preview-head {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.library-preview-head > div {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.library-preview pre {
  flex: 1;
  min-height: 78px;
  max-height: 148px;
  margin: 0;
  padding: 9px 10px;
  overflow: auto;
  border: 1px solid var(--border-muted);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.library-preview-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.library-preview-actions button {
  min-height: 28px;
  padding: 3px 10px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
}

.library-preview-actions button:hover {
  color: var(--accent-blue);
  border-color: rgba(88, 166, 255, 0.45);
}

.library-preview-actions button.primary {
  border-color: var(--accent-blue);
  background: var(--accent-blue);
  color: #fff;
}

.editor-body { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.editor-pane { overflow: hidden; }
.resize-handle {
  height: 10px;
  background: var(--el-border-color);
  cursor: row-resize;
  flex-shrink: 0;
  transition: background-color 0.15s ease;
}
.resize-handle:hover {
  background: var(--accent-blue);
}
.results-pane { overflow: hidden; }
</style>
