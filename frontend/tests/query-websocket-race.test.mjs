import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const websocket = readFileSync(new URL('../src/utils/websocket.ts', import.meta.url), 'utf8')
const editorTab = readFileSync(new URL('../src/components/editor/EditorTab.vue', import.meta.url), 'utf8')

test('QueryWebSocket.connect resolves before executeQuery is called', () => {
  assert.match(websocket, /connect\(\): Promise<void>/)
  assert.match(editorTab, /await wsClient\.connect\(\)/)
  assert.ok(editorTab.indexOf('await wsClient.connect()') < editorTab.indexOf('await queryApi.executeQuery'))
})

test('editor emits schema refresh when returned statements changed schema', () => {
  assert.match(editorTab, /queryResultChangesSchema/)
  assert.match(editorTab, /emitDbSchemaChanged/)
  assert.match(editorTab, /const executionDb = currentDb\.value/)
  assert.doesNotMatch(editorTab, /data\?\.status === 'success' && queryResultChangesSchema/)
  assert.match(websocket, /private onResult/)
  assert.match(websocket, /this\.onResult\?\.\(data\)/)
})
