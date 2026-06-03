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

test('connection tree wires search and copy without list timestamps', () => {
  assert.match(connectionTree, /搜索连接、主机、库名/)
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
  assert.match(editorTab, /applySelectedSql/)
  assert.match(editorTab, /insertSelectedSql/)
  assert.match(editorTab, /copySelectedSql/)
  assert.match(editorTab, /executeSelectedSql/)
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

test('export dialog displays target table, format, and total rows', () => {
  assert.match(exportDialog, /{{ tab\.database }} \/ {{ tab\.table }}/)
  assert.match(exportDialog, /{{ total }} 行/)
})
