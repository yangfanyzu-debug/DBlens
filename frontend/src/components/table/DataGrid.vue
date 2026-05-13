<template>
  <div class="data-grid">
    <div class="toolbar">
      <!-- 第一组 -->
      <el-button size="small" @click="loadData">刷新</el-button>
      <el-button size="small" type="primary" @click="addRow">+ 新增行</el-button>

      <span class="toolbar-sep" />

      <!-- 第二组 -->
      <el-button size="small" type="danger" :disabled="!selectedRows.length" @click="deleteRows">删除选中</el-button>
      <el-button size="small" type="success" :disabled="!pendingChanges.length" @click="showPreview">提交变更</el-button>

      <span class="toolbar-sep" />

      <!-- 第三组 -->
      <el-button size="small" @click="showExport = true">导出</el-button>

      <span class="total-info">共 {{ total }} 条</span>
    </div>

    <el-table
      ref="tableRef"
      :data="rows"
      size="small"
      border
      height="calc(100% - 80px)"
      @selection-change="selectedRows = $event"
      v-loading="loading"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column
        v-for="col in columns"
        :key="col.name"
        :prop="col.name"
        :label="col.name"
        min-width="120"
        sortable
        @sort-change="onSort"
      >
        <template #default="{ row, $index }">
          <div
            class="cell-content"
            @dblclick="startEdit($index, col.name)"
          >
            <template v-if="editCell?.row === $index && editCell?.col === col.name">
              <el-input
                v-model="editValue"
                size="small"
                autofocus
                @blur="commitEdit($index, col.name, row)"
                @keyup.enter="commitEdit($index, col.name, row)"
                @keyup.esc="cancelEdit"
              />
            </template>
            <template v-else>
              <span :class="{ 'cell-modified': isCellModified($index, col.name) }">
                {{ formatCellValue(row[col.name]) }}
              </span>
            </template>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <span class="total-label">共 {{ total }} 条</span>
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[50, 100, 200, 500]"
        layout="sizes, prev, pager, next"
        small
        @change="loadData"
      />
    </div>

    <!-- Change Preview Dialog -->
    <el-dialog v-model="previewVisible" title="变更预览" width="700px">
      <div v-for="(item, i) in previewSqls" :key="i" class="preview-sql">
        <el-tag :type="item.type === 'DELETE' ? 'danger' : item.type === 'INSERT' ? 'success' : 'warning'" size="small">
          {{ item.type }}
        </el-tag>
        <code>{{ item.sql }}</code>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">取消</el-button>
        <el-button type="primary" @click="commitChanges" :loading="committing">确认执行</el-button>
      </template>
    </el-dialog>

    <!-- Export Dialog -->
    <ExportDialog v-model:visible="showExport" :tab="tab" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { Tab } from '@/stores/tabs'
import * as dataApi from '@/api/data'
import ExportDialog from '@/components/common/ExportDialog.vue'
import { formatCellValue } from '@/utils/displayFormat'

const props = defineProps<{ tab: Tab }>()

const tableRef = ref()
const loading = ref(false)
const columns = ref<{ name: string; type: string }[]>([])
const rows = ref<Record<string, any>[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(100)
const sortCol = ref<string>()
const sortDir = ref('ASC')
const selectedRows = ref<any[]>([])
const editCell = ref<{ row: number; col: string } | null>(null)
const editValue = ref('')
const pendingChanges = ref<any[]>([])
const previewVisible = ref(false)
const previewSqls = ref<any[]>([])
const committing = ref(false)
const showExport = ref(false)

// Track original values for change detection
const originalRows = ref<Record<string, any>[]>([])

onMounted(loadData)

async function loadData() {
  if (!props.tab.connId || !props.tab.database || !props.tab.table) return
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (sortCol.value) { params.sort_col = sortCol.value; params.sort_dir = sortDir.value }
    const data = await dataApi.getTableData(props.tab.connId, props.tab.database, props.tab.table, params)
    columns.value = data.columns
    rows.value = data.rows.map((row: any[]) => {
      const obj: Record<string, any> = {}
      data.columns.forEach((col: any, i: number) => { obj[col.name] = row[i] })
      return obj
    })
    originalRows.value = rows.value.map(r => ({ ...r }))
    total.value = data.total
    pendingChanges.value = []
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

function onSort({ prop, order }: any) {
  sortCol.value = prop
  sortDir.value = order === 'descending' ? 'DESC' : 'ASC'
  loadData()
}

function startEdit(rowIdx: number, colName: string) {
  editCell.value = { row: rowIdx, col: colName }
  editValue.value = String(rows.value[rowIdx][colName] ?? '')
}

function commitEdit(rowIdx: number, colName: string, row: any) {
  if (!editCell.value) return
  const oldVal = originalRows.value[rowIdx][colName]
  const newVal = editValue.value
  if (String(oldVal) !== newVal) {
    rows.value[rowIdx][colName] = newVal
    // Find primary key column (first column as fallback)
    const pkCol = columns.value[0]?.name
    const existing = pendingChanges.value.findIndex(
      c => c.op === 'update' && c.pk_val === String(originalRows.value[rowIdx][pkCol])
    )
    if (existing >= 0) {
      pendingChanges.value[existing].values[colName] = newVal
    } else {
      pendingChanges.value.push({
        op: 'update',
        pk_col: pkCol,
        pk_val: String(originalRows.value[rowIdx][pkCol]),
        values: { [colName]: newVal },
      })
    }
  }
  editCell.value = null
}

function cancelEdit() {
  editCell.value = null
}

function isCellModified(rowIdx: number, colName: string) {
  return pendingChanges.value.some(
    c => c.op === 'update' && c.pk_val === String(originalRows.value[rowIdx]?.[columns.value[0]?.name])
      && c.values?.[colName] !== undefined
  )
}

function addRow() {
  const newRow: Record<string, any> = {}
  columns.value.forEach(col => { newRow[col.name] = null })
  rows.value.push(newRow)
  originalRows.value.push({ ...newRow })
  pendingChanges.value.push({ op: 'insert', values: newRow })
}

function deleteRows() {
  const pkCol = columns.value[0]?.name
  for (const row of selectedRows.value) {
    pendingChanges.value.push({ op: 'delete', pk_col: pkCol, pk_val: String(row[pkCol]) })
    const idx = rows.value.indexOf(row)
    if (idx >= 0) rows.value.splice(idx, 1)
  }
  selectedRows.value = []
}

async function showPreview() {
  if (!pendingChanges.value.length) return
  const result = await dataApi.previewChanges(
    props.tab.connId!, props.tab.database!, props.tab.table!, pendingChanges.value
  )
  previewSqls.value = result.changes
  previewVisible.value = true
}

async function commitChanges() {
  committing.value = true
  try {
    await dataApi.applyChanges(
      props.tab.connId!, props.tab.database!, props.tab.table!, pendingChanges.value
    )
    ElMessage.success('变更已提交')
    previewVisible.value = false
    await loadData()
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    committing.value = false
  }
}
</script>

<style scoped>
.data-grid {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-default);
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  flex-shrink: 0;
}
.toolbar-sep {
  width: 1px;
  height: 18px;
  background: var(--border-default);
  margin: 0 4px;
}
.total-info {
  margin-left: auto;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}
.pagination {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-top: 1px solid var(--border-default);
  background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  flex-shrink: 0;
}
.total-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-right: 12px;
  align-self: center;
}
.cell-content { min-height: 20px; cursor: default; overflow: hidden; display: block; }
.cell-content span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; line-height: 20px; }
.cell-modified { background: #fef3c7; border-radius: 4px; padding: 1px 4px; }
.preview-sql { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 8px; }
.preview-sql code { font-size: 12px; word-break: break-all; }

:deep(.el-table) {
  --el-table-border-color: var(--border-muted);
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-row-hover-bg-color: var(--glow-blue);
  background: var(--bg-primary);
  table-layout: fixed;
}

/* 表头加粗 + 背景 */
:deep(.el-table__header-wrapper th) {
  font-weight: 600;
  background: var(--bg-secondary) !important;
  color: var(--text-secondary);
}

/* 单元格内边距 */
:deep(.el-table td .cell) {
  padding: 4px 8px;
}

:deep(.el-table td.el-table__cell) {
  color: var(--text-primary);
  overflow: hidden;
}

:deep(.el-table .el-table__inner-wrapper::before) {
  display: none;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-button-bg-color: var(--bg-primary);
  --el-pagination-hover-color: var(--accent-blue);
}
</style>
