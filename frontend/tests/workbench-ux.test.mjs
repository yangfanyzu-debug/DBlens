import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const connectionTree = readFileSync(new URL('../src/components/connection/ConnectionTree.vue', import.meta.url), 'utf8')
const connectionForm = readFileSync(new URL('../src/components/connection/ConnectionForm.vue', import.meta.url), 'utf8')
const sidebar = readFileSync(new URL('../src/components/layout/Sidebar.vue', import.meta.url), 'utf8')
const dbTree = readFileSync(new URL('../src/components/browser/DbTree.vue', import.meta.url), 'utf8')
const editorTab = readFileSync(new URL('../src/components/editor/EditorTab.vue', import.meta.url), 'utf8')
const resultTable = readFileSync(new URL('../src/components/editor/ResultTable.vue', import.meta.url), 'utf8')
const exportDialog = readFileSync(new URL('../src/components/common/ExportDialog.vue', import.meta.url), 'utf8')
const tabBar = readFileSync(new URL('../src/components/common/TabBar.vue', import.meta.url), 'utf8')
const connectionsStore = readFileSync(new URL('../src/stores/connections.ts', import.meta.url), 'utf8')
const structureView = readFileSync(new URL('../src/components/table/StructureView.vue', import.meta.url), 'utf8')
const databaseApi = readFileSync(new URL('../src/api/databases.ts', import.meta.url), 'utf8')
const editorToolbar = readFileSync(new URL('../src/components/editor/EditorToolbar.vue', import.meta.url), 'utf8')

test('connection tree wires search and copy without list timestamps', () => {
  assert.match(connectionTree, /搜索连接、主机、库名/)
  assert.match(connectionTree, /connection-section-title/)
  assert.match(connectionTree, /createConnectionCopy/)
  assert.doesNotMatch(connectionTree, /formatLastUsed|last-used/)
})

test('sidebar reduces duplicate search boxes after a connection is active', () => {
  assert.match(sidebar, /:compact="Boolean\(activeConnId\)"/)
  assert.match(connectionTree, /toggle-search-btn/)
  assert.match(connectionTree, /v-if="!compact \|\| searchOpen"/)
})

test('sidebar opens the database panel with a transition after connection click', () => {
  assert.match(sidebar, /db-panel-slide/)
  assert.match(sidebar, /dbPanelOpen\.value = true/)
})

test('database tree shows an animated loading state while root databases load', () => {
  assert.match(dbTree, /loadingRoot/)
  assert.match(dbTree, /db-tree-loading/)
  assert.match(dbTree, /Loading/)
})

test('new query uses the database opened in the left tree when available', () => {
  assert.match(connectionsStore, /activeDatabaseByConn/)
  assert.match(dbTree, /setActiveDatabase\(props\.connId, node\.data\.database\)/)
  assert.match(dbTree, /setActiveDatabase\(data\.connId, data\.database\)/)
  assert.match(tabBar, /openEditorTab\(connId, connectionsStore\.activeDatabaseByConn\[connId\]\)/)
  assert.match(tabBar, /new-query-btn/)
})

test('each editor only reflects its own running query', () => {
  assert.match(editorTab, /:query-id="currentQueryId"/)
  assert.match(editorToolbar, /getResult\(props\.queryId\)\?\.status === 'running'/)
  assert.doesNotMatch(editorToolbar, /Object\.keys\(queryStore\.results\)/)
})

test('connection form explains edit-password behavior and offers database shortcut', () => {
  assert.match(connectionForm, /留空表示不修改已保存的密码/)
  assert.match(connectionForm, /同连接名/)
})

test('editor exposes query history and saved query controls', () => {
  assert.match(editorTab, /assistMode/)
  assert.match(editorTab, /recordHistory/)
  assert.match(editorTab, /toggleSaved/)
})

test('editor query library keeps large history and saved lists manageable', () => {
  assert.match(editorTab, /query-library-drawer/)
  assert.match(editorTab, /library-search/)
  assert.match(editorTab, /ASSIST_LIMIT/)
  assert.match(editorTab, /visibleHistory/)
  assert.match(editorTab, /visibleSavedQueries/)
  assert.match(editorTab, /removeSavedSql/)
  assert.match(editorTab, /library-list/)
  assert.match(editorTab, /selectedQuery/)
  assert.doesNotMatch(editorTab, /library-preview-actions/)
  assert.doesNotMatch(editorTab, /query-chip/)
})

test('editor query library opens as a right drawer without resizing the editor body', () => {
  assert.match(editorTab, /query-assist-shell/)
  assert.match(editorTab, /\.query-assist-shell\s*\{[^}]*position:\s*relative/s)
  assert.match(editorTab, /\.query-library-drawer\s*\{[^}]*position:\s*absolute/s)
  assert.match(editorTab, /\.query-library-drawer\s*\{[^}]*right:/s)
  assert.match(editorTab, /\.query-library-drawer\s*\{[^}]*width:\s*clamp/s)
  assert.match(editorTab, /\.query-library-drawer\s*\{[^}]*z-index:/s)
  assert.match(editorTab, /onAssistOutsideClick/)
})

test('result table remembers column widths and warns about likely row limits', () => {
  assert.match(resultTable, /getColumnStorageKey/)
  assert.match(resultTable, /limitNotice/)
})

test('result table exposes row context menu for copying SQL from inferred table', () => {
  assert.match(resultTable, /@row-contextmenu="onRowContextMenu"/)
  assert.match(resultTable, /inferSingleSelectTableName/)
  assert.match(resultTable, /dbApi\.listColumns/)
  assert.match(resultTable, /复制本行 INSERT/)
  assert.match(resultTable, /复制本行 UPDATE/)
  assert.match(resultTable, /无法识别单一目标表/)
})

test('result table guards copied SQL with table columns and primary key', () => {
  assert.match(resultTable, /invalidResultColumns/)
  assert.match(resultTable, /primaryKeyColumn/)
  assert.match(resultTable, /canCopyInsert/)
  assert.match(resultTable, /canCopyUpdate/)
  assert.match(resultTable, /结果列不是目标表原始字段/)
  assert.match(resultTable, /结果中缺少主键字段/)
  assert.match(resultTable, /buildUpdateSql\(inferredTable\.value, props\.stmt\.columns, \[contextRow\.value\], primaryKeyColumn\.value\)/)
})

test('export dialog displays target table, format, and total rows', () => {
  assert.match(exportDialog, /{{ tab\.database }} \/ {{ tab\.table }}/)
  assert.match(exportDialog, /{{ total }} 行/)
})

test('data grid exposes row context menu for copying SQL', () => {
  const dataGrid = readFileSync(new URL('../src/components/table/DataGrid.vue', import.meta.url), 'utf8')
  assert.match(dataGrid, /@row-contextmenu="onRowContextMenu"/)
  assert.match(dataGrid, /复制本行 INSERT/)
  assert.match(dataGrid, /复制选中行 UPDATE/)
  assert.match(dataGrid, /buildInsertSql/)
  assert.match(dataGrid, /buildUpdateSql/)
})

test('table structure view lazily loads and copies the create table schema', () => {
  assert.match(structureView, /label="建表语句"/)
  assert.match(structureView, /loadTableDdl/)
  assert.match(structureView, /copyTableDdl/)
  assert.match(structureView, /copyTextToClipboard/)
  assert.match(databaseApi, /tables\/\$\{table\}\/ddl/)
})
