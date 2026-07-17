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
        @row-contextmenu="onRowContextMenu"
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
      <div v-if="contextRow" class="result-sql-menu" :style="contextMenuStyle">
        <template v-if="inferredTable">
          <button type="button" @click="copyRowInsert">复制本行 INSERT（{{ inferredTable }}）</button>
          <button type="button" @click="copyRowUpdate">复制本行 UPDATE（{{ inferredTable }}）</button>
        </template>
        <template v-else>
          <button type="button" disabled>无法识别单一目标表</button>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { QueryResult } from '@/stores/query'
import { formatCellValue } from '@/utils/displayFormat'
import { getColumnStorageKey, getResultLimitNotice } from '@/utils/resultTableUx'
import { buildInsertSql, buildUpdateSql } from '@/utils/rowSql'
import { inferSingleSelectTableName } from '@/utils/sqlTableName'
import { copyTextToClipboard } from '@/utils/clipboard'

const props = defineProps<{ stmt: QueryResult; connId: string; database: string }>()
const contextRow = ref<Record<string, any> | null>(null)
const contextMenuStyle = ref<Record<string, string>>({})

const tableData = computed(() =>
  props.stmt.rows.map(row => {
    const obj: Record<string, any> = {}
    props.stmt.columns.forEach((col, i) => { obj[col] = row[i] })
    return obj
  })
)
const limitNotice = computed(() => getResultLimitNotice(props.stmt))
const inferredTable = computed(() => inferSingleSelectTableName(props.stmt.sql))

onMounted(() => {
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})

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

function closeContextMenu() {
  contextRow.value = null
}

function onRowContextMenu(row: Record<string, any>, _column: any, event: MouseEvent) {
  event.preventDefault()
  contextRow.value = row
  contextMenuStyle.value = { top: `${event.clientY}px`, left: `${event.clientX}px` }
}

async function copySql(sql: string) {
  if (!sql) {
    ElMessage.warning('没有可复制的 SQL')
    return
  }
  try {
    await copyTextToClipboard(sql)
    ElMessage.success('SQL 已复制')
    closeContextMenu()
  } catch (e: any) {
    ElMessage.error(e.message || '复制失败')
  }
}

function copyRowInsert() {
  if (!contextRow.value || !inferredTable.value) return
  copySql(buildInsertSql(inferredTable.value, props.stmt.columns, [contextRow.value]))
}

function copyRowUpdate() {
  if (!contextRow.value || !inferredTable.value) return
  copySql(buildUpdateSql(inferredTable.value, props.stmt.columns, [contextRow.value]))
}
</script>

<style scoped>
.result-table-wrap { height: 100%; overflow: auto; }
.affected { padding: 16px; color: var(--el-text-color-secondary); }
.limit-notice { margin: 8px; width: auto; }

.result-sql-menu {
  position: fixed;
  z-index: 3000;
  min-width: 196px;
  padding: 6px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
}

.result-sql-menu button {
  display: block;
  width: 100%;
  border: 0;
  border-radius: 4px;
  padding: 7px 9px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  text-align: left;
  cursor: pointer;
}

.result-sql-menu button:hover:not(:disabled) {
  background: var(--glow-blue);
  color: var(--text-primary);
}

.result-sql-menu button:disabled {
  color: var(--text-muted);
  cursor: not-allowed;
}
</style>
