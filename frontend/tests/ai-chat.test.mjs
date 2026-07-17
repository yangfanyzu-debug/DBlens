import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const editorTab = readFileSync(new URL('../src/components/editor/EditorTab.vue', import.meta.url), 'utf8')
const monacoEditor = readFileSync(new URL('../src/components/editor/MonacoEditor.vue', import.meta.url), 'utf8')

test('editor tab mounts a floating streaming AI chat panel', () => {
  assert.match(editorTab, /AiChatPanel/)
  assert.match(editorTab, /ai-panel-open/)
  assert.match(editorTab, /currentAiContext/)
  assert.match(editorTab, /@insert-sql="insertAiSql"/)
  assert.match(editorTab, /@replace-sql="replaceAiSql"/)
})

test('monaco editor exposes selected text separately for AI context', () => {
  assert.match(monacoEditor, /function getSelectedText\(\)/)
  assert.match(monacoEditor, /defineExpose\(\{[^}]*getSelectedText/s)
})
