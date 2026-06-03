import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const tree = readFileSync(new URL('../src/components/connection/ConnectionTree.vue', import.meta.url), 'utf8')
const form = readFileSync(new URL('../src/components/connection/ConnectionForm.vue', import.meta.url), 'utf8')
const editor = readFileSync(new URL('../src/components/editor/EditorTab.vue', import.meta.url), 'utf8')
const sidebar = readFileSync(new URL('../src/components/layout/Sidebar.vue', import.meta.url), 'utf8')

test('connection tree empty state offers a new connection action', () => {
  assert.match(tree, /new-connection/)
  assert.match(sidebar, /@new-connection="showForm = true"/)
})

test('connection tree shows inferred environment tags', () => {
  assert.match(tree, /getConnectionEnvironment/)
  assert.match(tree, /env-tag/)
})

test('connection form renders detailed test feedback', () => {
  assert.match(form, /testFeedback/)
  assert.match(form, /getTestFeedback/)
})

test('editor asks for confirmation before risky SQL execution', () => {
  assert.match(editor, /assessSqlRisk/)
  assert.match(editor, /ElMessageBox\.confirm/)
})
