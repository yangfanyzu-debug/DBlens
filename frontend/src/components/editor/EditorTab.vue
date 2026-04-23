<template>
  <div class="editor-tab">
    <EditorToolbar :tab="tab" @execute="onExecute" @kill="onKill" @format="onFormat" @db-change="onDbChange" />
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
        <ResultsPane :query-id="currentQueryId" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { Tab } from '@/stores/tabs'
import { useQueryStore } from '@/stores/query'
import { useConnectionsStore } from '@/stores/connections'
import * as queryApi from '@/api/query'
import { QueryWebSocket } from '@/utils/websocket'
import EditorToolbar from './EditorToolbar.vue'
import MonacoEditor from './MonacoEditor.vue'
import ResultsPane from './ResultsPane.vue'

const props = defineProps<{ tab: Tab }>()

const queryStore = useQueryStore()
const connStore = useConnectionsStore()
const monacoRef = ref<any>(null)
const bodyRef = ref<HTMLElement>()
const currentQueryId = ref<string>('')
const currentDb = ref(props.tab.database ?? '')

const editorHeight = ref(300)
const resultsHeight = ref(200)
let wsClient: QueryWebSocket | null = null

async function onExecute(sql?: string) {
  const code = sql ?? monacoRef.value?.getValue() ?? ''
  if (!code.trim()) return
  const queryId = uuidv4()
  currentQueryId.value = queryId
  queryStore.setRunning(queryId)
  wsClient?.stop()
  wsClient = new QueryWebSocket(queryId)
  wsClient.connect()
  await queryApi.executeQuery(props.tab.connId, currentDb.value, code, queryId)
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
})

onUnmounted(() => wsClient?.stop())
</script>

<style scoped>
.editor-tab { display: flex; flex-direction: column; height: 100%; }
.editor-body { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.editor-pane { overflow: hidden; }
.resize-handle { height: 6px; background: var(--el-border-color); cursor: row-resize; flex-shrink: 0; }
.resize-handle:hover { background: var(--el-color-primary-light-7); }
.results-pane { overflow: hidden; }
</style>
