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
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { Tab } from '@/stores/tabs'
import * as dbApi from '@/api/databases'

const props = defineProps<{ tab: Tab }>()
const activeTab = ref('columns')
const columns = ref<any[]>([])
const indexes = ref<any[]>([])
const foreignKeys = ref<any[]>([])

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
</style>
