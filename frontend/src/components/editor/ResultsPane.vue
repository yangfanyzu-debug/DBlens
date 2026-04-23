<template>
  <div class="results-pane">
    <div v-if="!queryState" class="empty">执行 SQL 后结果显示在这里</div>
    <div v-else-if="queryState.status === 'running'" class="running">
      <el-icon class="is-loading"><Loading /></el-icon> 执行中...
    </div>
    <div v-else-if="queryState.status === 'error'" class="error-msg">
      <el-alert :title="queryState.error ?? '未知错误'" type="error" show-icon :closable="false" />
    </div>
    <div v-else-if="queryState.status === 'killed'" class="killed">查询已终止</div>
    <div v-else class="results">
      <el-tabs v-if="queryState.statements.length > 1" type="card" size="small">
        <el-tab-pane v-for="(stmt, i) in queryState.statements" :key="i" :label="`结果 ${i + 1}`">
          <ResultTable :stmt="stmt" />
        </el-tab-pane>
      </el-tabs>
      <ResultTable v-else-if="queryState.statements.length === 1" :stmt="queryState.statements[0]" />
    </div>
    <div class="status-bar" v-if="queryState">
      <span v-if="queryState.status === 'success'">
        {{ totalRows }} 行 · {{ queryState.total_ms }}ms
      </span>
      <span v-else-if="queryState.status === 'error'" class="err">错误</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect } from 'vue'
import { storeToRefs } from 'pinia'
import { Loading } from '@element-plus/icons-vue'
import { useQueryStore } from '@/stores/query'
import ResultTable from './ResultTable.vue'

const props = defineProps<{ queryId: string }>()
const store = useQueryStore()
const { results } = storeToRefs(store)

const queryState = ref<any>(null)
const totalRows = computed(() => queryState.value?.statements.reduce((s: number, r: any) => s + r.row_count, 0) ?? 0)

watchEffect(() => {
  queryState.value = results.value[props.queryId] ?? null
})
</script>

<style scoped>
.results-pane { display: flex; flex-direction: column; height: 100%; overflow: hidden; }
.empty, .running, .killed { display: flex; align-items: center; justify-content: center; height: 100%; color: var(--el-text-color-secondary); gap: 8px; }
.error-msg { padding: 12px; }
.results { flex: 1; overflow: auto; }
.status-bar { padding: 2px 12px; font-size: 12px; color: var(--el-text-color-secondary); border-top: 1px solid var(--el-border-color); background: var(--el-bg-color-page); }
.err { color: var(--el-color-danger); }
</style>
