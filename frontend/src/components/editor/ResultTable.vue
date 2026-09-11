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
        ref="resultTable"
        :data="tableData"
        size="small"
        border
        height="100%"
        style="width:100%"
        @header-dragend="onHeaderDragEnd"
        @row-contextmenu="onRowContextMenu"
        @row-dblclick="openRowDetails"
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
        <button type="button" @click="openRowDetails(contextRow)">查看行详情</button>
        <template v-if="inferredTable">
          <button type="button" :disabled="!canCopyInsert" @click="copyRowInsert">复制本行 INSERT（{{ inferredTable }}）</button>
          <button type="button" :disabled="!canCopyUpdate" @click="copyRowUpdate">复制本行 UPDATE（{{ inferredTable }}）</button>
          <div v-if="copyGuardMessage" class="menu-hint">{{ copyGuardMessage }}</div>
        </template>
        <template v-else>
          <button type="button" disabled>无法识别单一目标表</button>
        </template>
      </div>
      <RowDetailsDrawer v-model="detailsVisible" v-model:index="detailsIndex" :columns="stmt.columns" :rows="detailRows" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { QueryResult } from '@/stores/query'
import * as dbApi from '@/api/databases'
import { formatCellValue } from '@/utils/displayFormat'
import { getColumnStorageKey, getResultLimitNotice } from '@/utils/resultTableUx'
import { buildInsertSql, buildUpdateSql } from '@/utils/rowSql'
import { inferSingleSelectTableName } from '@/utils/sqlTableName'
import { copyTextToClipboard } from '@/utils/clipboard'
import RowDetailsDrawer from './RowDetailsDrawer.vue'

const props = defineProps<{ stmt: QueryResult; connId: string; database: string }>()
const contextRow = ref<Record<string, any> | null>(null)
const contextMenuStyle = ref<Record<string, string>>({})
const tableColumns = ref<Array<{ name: string; primary_key?: boolean }>>([])
const schemaLoading = ref(false)
const schemaError = ref('')
const resultTable = ref<any>(null)
const detailsVisible = ref(false)
const detailsIndex = ref(0)
const detailRows = ref<Record<string, any>[]>([])

function openRowDetails(row: Record<string, any>) {
  detailRows.value = [...(resultTable.value?.store?.states?.data?.value ?? tableData.value)]
  detailsIndex.value = detailRows.value.indexOf(row)
  if (detailsIndex.value < 0) return
  detailsVisible.value = true
  closeContextMenu()
}

watch(() => props.stmt, () => {
  detailsVisible.value = false
  detailRows.value = []
  closeContextMenu()
})

const tableData = computed(() =>
  props.stmt.rows.map(row => {
    const obj: Record<string, any> = {}
    props.stmt.columns.forEach((col, i) => { obj[col] = row[i] })
    return obj
  })
)
const limitNotice = computed(() => getResultLimitNotice(props.stmt))
const inferredTable = computed(() => inferSingleSelectTableName(props.stmt.sql))
const tableTarget = computed(() => parseTableTarget(inferredTable.value))
const tableColumnNames = computed(() => new Set(tableColumns.value.map(col => col.name)))
const invalidResultColumns = computed(() => props.stmt.columns.filter(col => !tableColumnNames.value.has(col)))
const primaryKeyColumn = computed(() => tableColumns.value.find(col => col.primary_key)?.name ?? '')
const resultHasPrimaryKey = computed(() => Boolean(primaryKeyColumn.value && props.stmt.columns.includes(primaryKeyColumn.value)))
const resultColumnsMatchTable = computed(() =>
  Boolean(tableColumns.value.length && props.stmt.columns.length && invalidResultColumns.value.length === 0)
)
const canCopyInsert = computed(() => Boolean(inferredTable.value && resultColumnsMatchTable.value && !schemaLoading.value && !schemaError.value))
const canCopyUpdate = computed(() => Boolean(canCopyInsert.value && resultHasPrimaryKey.value))
const copyGuardMessage = computed(() => {
  if (!inferredTable.value) return ''
  if (schemaLoading.value) return '正在校验表结构'
  if (schemaError.value) return schemaError.value
  if (!resultColumnsMatchTable.value) return '结果列不是目标表原始字段，无法安全生成 SQL'
  if (!resultHasPrimaryKey.value) return '结果中缺少主键字段，无法安全生成 UPDATE'
  return ''
})

let schemaRequestId = 0

onMounted(() => {
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})

watch(tableTarget, async target => {
  const requestId = ++schemaRequestId
  tableColumns.value = []
  schemaError.value = ''
  if (!target) return

  schemaLoading.value = true
  try {
    const columns = await dbApi.listColumns(props.connId, target.database, target.table)
    if (requestId !== schemaRequestId) return
    tableColumns.value = columns
  } catch (e: any) {
    if (requestId !== schemaRequestId) return
    schemaError.value = e.message || '表结构校验失败'
  } finally {
    if (requestId === schemaRequestId) schemaLoading.value = false
  }
}, { immediate: true })

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

function parseTableTarget(tableName: string | null) {
  if (!tableName) return null
  const parts = tableName.split('.')
  const table = parts.pop() || ''
  const database = parts.length ? parts.join('.') : props.database
  if (!database || !table) return null
  return { database, table }
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
  if (!contextRow.value || !inferredTable.value || !canCopyInsert.value) {
    if (copyGuardMessage.value) ElMessage.warning(copyGuardMessage.value)
    return
  }
  copySql(buildInsertSql(inferredTable.value, props.stmt.columns, [contextRow.value]))
}

function copyRowUpdate() {
  if (!contextRow.value || !inferredTable.value || !canCopyUpdate.value) {
    if (copyGuardMessage.value) ElMessage.warning(copyGuardMessage.value)
    return
  }
  copySql(buildUpdateSql(inferredTable.value, props.stmt.columns, [contextRow.value], primaryKeyColumn.value))
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

.menu-hint {
  max-width: 220px;
  padding: 5px 8px 2px;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.4;
}
</style>
