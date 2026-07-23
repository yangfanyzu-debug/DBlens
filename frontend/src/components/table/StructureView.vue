<template>
  <div class="structure-view">
    <el-tabs v-model="activeTab" size="small" class="structure-tabs">
      <el-tab-pane label="字段" name="columns">
        <div class="pane-body">
          <el-table :data="columns" size="small" border height="100%">
          <el-table-column prop="name" label="字段名" min-width="120" />
          <el-table-column prop="type" label="类型" min-width="100" />
          <el-table-column label="可空" width="60">
            <template #default="{ row }">
              <el-tag :type="row.nullable ? 'info' : 'danger'" size="small">{{ row.nullable ? 'YES' : 'NO' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="default" label="默认值" min-width="100" />
          <el-table-column prop="comment" label="注释" min-width="120" />
          <el-table-column label="主键" width="60">
            <template #default="{ row }">
              <el-tag v-if="row.primary_key" type="warning" size="small">PK</el-tag>
            </template>
          </el-table-column>
        </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="索引" name="indexes">
        <div class="pane-body">
          <el-table :data="indexes" size="small" border height="100%">
          <el-table-column prop="name" label="索引名" min-width="150" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column label="字段" min-width="150">
            <template #default="{ row }">{{ row.columns?.join(', ') }}</template>
          </el-table-column>
        </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="外键" name="fks">
        <div class="pane-body">
          <el-table :data="foreignKeys" size="small" border height="100%">
          <el-table-column prop="name" label="外键名" min-width="150" />
          <el-table-column prop="column" label="本表字段" min-width="120" />
          <el-table-column prop="ref_table" label="引用表" min-width="120" />
          <el-table-column prop="ref_column" label="引用字段" min-width="120" />
        </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="建表语句" name="ddl">
        <div v-loading="ddlLoading" class="ddl-pane">
          <div class="ddl-toolbar">
            <div>
              <strong>Schema DDL</strong>
              <span>{{ tab.database }} / {{ tab.table }}</span>
            </div>
            <el-tooltip content="复制建表语句" placement="bottom">
              <button
                class="copy-ddl-btn"
                type="button"
                :disabled="!tableDdl"
                aria-label="复制建表语句"
                @click="copyTableDdl"
              >
                <el-icon><DocumentCopy /></el-icon>
              </button>
            </el-tooltip>
          </div>
          <pre v-if="tableDdl" class="ddl-code">{{ tableDdl }}</pre>
          <el-empty v-else-if="!ddlLoading" description="暂无可用的建表语句" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentCopy } from '@element-plus/icons-vue'
import type { Tab } from '@/stores/tabs'
import * as dbApi from '@/api/databases'
import { copyTextToClipboard } from '@/utils/clipboard'

const props = defineProps<{ tab: Tab }>()
const activeTab = ref('columns')
const columns = ref<any[]>([])
const indexes = ref<any[]>([])
const foreignKeys = ref<any[]>([])
const tableDdl = ref('')
const ddlLoading = ref(false)
const ddlLoaded = ref(false)

onMounted(async () => {
  if (!props.tab.connId || !props.tab.database || !props.tab.table) return
  try {
    const [cols, idxs, fks] = await Promise.all([
      dbApi.listColumns(props.tab.connId, props.tab.database, props.tab.table),
      dbApi.listIndexes(props.tab.connId, props.tab.database, props.tab.table),
      dbApi.listForeignKeys(props.tab.connId, props.tab.database, props.tab.table),
    ])
    columns.value = cols
    indexes.value = idxs
    foreignKeys.value = fks
  } catch (e: any) {
    ElMessage.error(e.message)
  }
})

watch(activeTab, tab => {
  if (tab === 'ddl') void loadTableDdl()
})

async function loadTableDdl() {
  if (ddlLoaded.value || ddlLoading.value) return
  if (!props.tab.connId || !props.tab.database || !props.tab.table) return

  ddlLoading.value = true
  try {
    const result = await dbApi.getTableDdl(props.tab.connId, props.tab.database, props.tab.table)
    tableDdl.value = result.ddl
    ddlLoaded.value = true
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    ddlLoading.value = false
  }
}

async function copyTableDdl() {
  if (!tableDdl.value) return
  await copyTextToClipboard(tableDdl.value)
  ElMessage.success('建表语句已复制')
}
</script>

<style scoped>
.structure-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary);
}

.structure-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.structure-tabs :deep(.el-tabs__header) {
  flex-shrink: 0;
  margin: 0;
  padding: 0 16px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  border-bottom: 1px solid var(--border-default);
}

.structure-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.structure-tabs :deep(.el-tabs__item) {
  height: 40px;
  font-weight: 600;
  color: var(--text-secondary);
}

.structure-tabs :deep(.el-tabs__item.is-active) {
  color: var(--accent-blue);
}

.structure-tabs :deep(.el-tabs__active-bar) {
  background: var(--accent-blue);
}

.structure-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.structure-tabs :deep(.el-tab-pane) {
  height: 100%;
  overflow: auto;
}

.structure-tabs :deep(.el-table) {
  --el-table-border-color: var(--border-muted);
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-row-hover-bg-color: var(--glow-blue);
  background: var(--bg-primary);
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--border-muted);
}

.structure-tabs :deep(.el-table th.el-table__cell) {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 600;
}

.structure-tabs :deep(.el-table td.el-table__cell) {
  color: var(--text-primary);
}

.pane-body {
  padding: 16px;
  height: 100%;
  box-sizing: border-box;
}

.ddl-pane {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 240px;
  background: var(--bg-secondary);
}

.ddl-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-muted);
  background: var(--bg-primary);
}

.ddl-toolbar > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.ddl-toolbar strong {
  color: var(--text-primary);
  font-size: 13px;
}

.ddl-toolbar span {
  color: var(--text-muted);
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.copy-ddl-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  width: 30px;
  height: 30px;
  padding: 0;
  border: 1px solid var(--border-default);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
}

.copy-ddl-btn:hover:not(:disabled) {
  border-color: var(--accent-blue);
  color: var(--accent-blue);
}

.copy-ddl-btn:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.ddl-code {
  flex: 1;
  min-height: 0;
  margin: 0;
  padding: 16px;
  overflow: auto;
  color: var(--text-primary);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.65;
  white-space: pre;
  tab-size: 2;
}
</style>
