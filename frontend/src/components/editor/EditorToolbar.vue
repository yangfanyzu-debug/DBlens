<template>
  <div class="editor-toolbar">
    <el-select v-model="currentDb" size="small" placeholder="选择数据库" style="width:160px" @change="onDbChange">
      <el-option v-for="db in databases" :key="db" :label="db" :value="db" />
    </el-select>
    <el-button size="small" type="primary" @click="emit('execute')" :loading="isRunning">
      执行 <kbd>Ctrl+Enter</kbd>
    </el-button>
    <el-button size="small" @click="emit('kill')" :disabled="!isRunning">终止</el-button>
    <el-button size="small" @click="emit('format')">格式化</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'
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
  // Check if any query for this tab's connId is running
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
  padding: 6px 12px;
  border-bottom: 1px solid var(--el-border-color);
  background: var(--el-bg-color-page);
}
kbd {
  font-size: 10px;
  opacity: 0.6;
  margin-left: 4px;
}
.run-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--el-color-primary);
}
</style>
