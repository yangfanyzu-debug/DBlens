<template>
  <div class="structure-view">
    <el-tabs v-model="activeTab" size="small">
      <el-tab-pane label="字段" name="columns">
        <el-table :data="columns" size="small" border stripe height="100%">
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
      </el-tab-pane>

      <el-tab-pane label="索引" name="indexes">
        <el-table :data="indexes" size="small" border stripe height="100%">
          <el-table-column prop="name" label="索引名" min-width="150" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column label="字段" min-width="150">
            <template #default="{ row }">{{ row.columns?.join(', ') }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="外键" name="fks">
        <el-table :data="foreignKeys" size="small" border stripe height="100%">
          <el-table-column prop="name" label="外键名" min-width="150" />
          <el-table-column prop="column" label="本表字段" min-width="120" />
          <el-table-column prop="ref_table" label="引用表" min-width="120" />
          <el-table-column prop="ref_column" label="引用字段" min-width="120" />
        </el-table>
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
.structure-view { height: 100%; display: flex; flex-direction: column; }
:deep(.el-tabs) { height: 100%; display: flex; flex-direction: column; }
:deep(.el-tabs__content) { flex: 1; overflow: hidden; }
:deep(.el-tab-pane) { height: 100%; }
</style>
