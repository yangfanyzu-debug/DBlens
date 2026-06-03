<template>
  <div class="result-table-wrap">
    <div v-if="stmt.affected_rows !== null && stmt.affected_rows !== undefined" class="affected">
      影响行数：{{ stmt.affected_rows }}
    </div>
    <template v-else>
      <el-alert
        v-if="limitNotice"
        class="limit-notice"
        type="warning"
        :title="limitNotice"
        show-icon
        :closable="false"
      />
      <el-table
        :data="tableData"
        size="small"
        border
        height="100%"
        style="width:100%"
        @header-dragend="onHeaderDragEnd"
      >
        <el-table-column
          v-for="col in stmt.columns"
          :key="col"
          :prop="col"
          :label="col"
          :width="getSavedWidth(col)"
          min-width="120"
          sortable
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ formatCellValue(row[col]) }}
          </template>
        </el-table-column>
      </el-table>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { QueryResult } from '@/stores/query'
import { formatCellValue } from '@/utils/displayFormat'
import { getColumnStorageKey, getResultLimitNotice } from '@/utils/resultTableUx'

const props = defineProps<{ stmt: QueryResult; connId: string; database: string }>()

const tableData = computed(() =>
  props.stmt.rows.map(row => {
    const obj: Record<string, any> = {}
    props.stmt.columns.forEach((col, i) => { obj[col] = row[i] })
    return obj
  })
)
const limitNotice = computed(() => getResultLimitNotice(props.stmt))

function getSavedWidth(column: string) {
  if (typeof localStorage === 'undefined') return undefined
  const value = Number(localStorage.getItem(getColumnStorageKey(props.connId, props.database, column)))
  return Number.isFinite(value) && value > 0 ? value : undefined
}

function onHeaderDragEnd(newWidth: number, _oldWidth: number, column: { property?: string }) {
  if (!column.property || typeof localStorage === 'undefined') return
  localStorage.setItem(
    getColumnStorageKey(props.connId, props.database, column.property),
    String(newWidth),
  )
}
</script>

<style scoped>
.result-table-wrap { height: 100%; overflow: auto; }
.affected { padding: 16px; color: var(--el-text-color-secondary); }
.limit-notice { margin: 8px; width: auto; }
</style>
