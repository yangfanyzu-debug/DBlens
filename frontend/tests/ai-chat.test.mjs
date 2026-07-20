import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const editorTab = readFileSync(new URL('../src/components/editor/EditorTab.vue', import.meta.url), 'utf8')
const aiChatPanel = readFileSync(new URL('../src/components/editor/AiChatPanel.vue', import.meta.url), 'utf8')
const monacoEditor = readFileSync(new URL('../src/components/editor/MonacoEditor.vue', import.meta.url), 'utf8')

test('editor tab mounts a floating streaming AI chat panel', () => {
  assert.match(editorTab, /AiChatPanel/)
  assert.match(editorTab, /ai-panel-open/)
  assert.match(editorTab, /currentAiContext/)
  assert.match(editorTab, /@insert-sql="insertAiSql"/)
  assert.match(editorTab, /@replace-sql="replaceAiSql"/)
})

test('AI floating entry is docked at the lower right of the workbench', () => {
  assert.match(editorTab, /\.ai-floating-trigger\s*\{[^}]*right:\s*24px[^}]*bottom:\s*24px/s)
  assert.doesNotMatch(editorTab, /\.ai-floating-trigger\s*\{[^}]*top:\s*92px/s)
  assert.match(editorTab, /ai-orbit-icon/)
  assert.match(editorTab, /ai-orbit-core/)
})

test('AI chat panel exposes refined assistant interaction regions', () => {
  assert.match(aiChatPanel, /ai-context-strip/)
  assert.match(aiChatPanel, /ai-prompt-rail/)
  assert.match(aiChatPanel, /ai-stream-indicator/)
  assert.match(aiChatPanel, /ai-sql-toolbar/)
  assert.match(aiChatPanel, /ai-prompt-icon/)
  assert.match(aiChatPanel, /component :is="prompt.icon"/)
})

test('monaco editor exposes selected text separately for AI context', () => {
  assert.match(monacoEditor, /function getSelectedText\(\)/)
  assert.match(monacoEditor, /defineExpose\(\{[^}]*getSelectedText/s)
})
