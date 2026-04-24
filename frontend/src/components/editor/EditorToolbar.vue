<template>
  <div class="editor-toolbar">
    <div class="toolbar-left">
      <el-select v-model="currentDb" size="small" placeholder="选择数据库" class="db-select" @change="onDbChange">
        <template #prefix>
          <el-icon style="margin-right:2px"><Connection /></el-icon>
        </template>
        <el-option v-for="db in databases" :key="db" :label="db" :value="db" />
      </el-select>
    </div>
    <div class="toolbar-center">
      <div class="toolbar-sep" />
      <button class="tool-btn primary" @click="emit('execute')" :disabled="isRunning">
        <el-icon v-if="isRunning" class="spin"><Loading /></el-icon>
        <el-icon v-else><VideoPlay /></el-icon>
        {{ isRunning ? '执行中' : '执行' }}
      </button>
      <button class="tool-btn" @click="emit('kill')" :disabled="!isRunning" title="终止查询">
        <el-icon><VideoPause /></el-icon>
      </button>
      <div class="toolbar-sep" />
      <button class="tool-btn icon-only" @click="emit('format')" title="格式化 SQL">
        <el-icon><MagicStick /></el-icon>
      </button>
    </div>
    <div class="toolbar-right">
      <span v-if="isRunning" class="status-indicator running">
        <span class="pulse" />
        执行中
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { Loading, VideoPlay, VideoPause, MagicStick, Connection } from '@element-plus/icons-vue'
import { useQueryStore } from '@/stores/query'
import * as dbApi from '@/api/databases'
import type { Tab } from '@/stores/tabs'

const props = defineProps<{ tab: Tab }>()
const emit = defineEmits<{
  (e: 'execute'): void
  (e: 'kill'): void
  (e: 'format'): void
  (e: 'db-change', db: string): void
}>()

const queryStore = useQueryStore()
const databases = ref<string[]>([])
const currentDb = ref(props.tab.database ?? '')

const isRunning = computed(() => {
  for (const qid of Object.keys(queryStore.results)) {
    const r = queryStore.getResult(qid)
    if (r?.status === 'running') return true
  }
  return false
})

watch(() => props.tab.connId, async (connId) => {
  if (connId) {
    databases.value = await dbApi.listDatabases(connId)
    currentDb.value = props.tab.database ?? databases.value[0] ?? ''
  }
}, { immediate: true })

function onDbChange(db: string) {
  currentDb.value = db
  emit('db-change', db)
}
</script>

<style scoped>
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  height: 42px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}
.toolbar-left { display: flex; align-items: center; }
.toolbar-center { display: flex; align-items: center; gap: 4px; flex: 1; justify-content: center; }
.toolbar-right { display: flex; align-items: center; gap: 8px; }

.db-select {
  width: 160px;
}

.toolbar-sep {
  width: 1px;
  height: 20px;
  background: var(--border-default);
  margin: 0 4px;
}

.tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border: 1px solid var(--border-default);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  font-size: 12.5px;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.12s ease;
}
.tool-btn:hover:not(:disabled) {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-color: var(--border-default);
}
.tool-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.tool-btn.primary {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
  color: #fff;
}
.tool-btn.primary:hover:not(:disabled) {
  background: #79b8ff;
  border-color: #79b8ff;
  box-shadow: 0 2px 8px var(--glow-blue);
  transform: translateY(-1px);
}
.tool-btn.icon-only {
  padding: 5px 8px;
}

.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: var(--text-muted);
}
.status-indicator.running { color: var(--accent-green); }
.pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-green);
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}
</style>
