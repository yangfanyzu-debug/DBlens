import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import assert from 'node:assert/strict'

const sidebar = readFileSync(new URL('../src/components/layout/Sidebar.vue', import.meta.url), 'utf8')
const connectionTree = readFileSync(new URL('../src/components/connection/ConnectionTree.vue', import.meta.url), 'utf8')

test('sidebar renders a visible separator before the database tree panel', () => {
  assert.match(sidebar, /class="sidebar-divider"/)
  assert.match(sidebar, /\.sidebar-divider\s*\{/)
})

test('connection groups are collapsed by default', () => {
  assert.match(connectionTree, /expanded\[key\]\s*=\s*false/)
  assert.doesNotMatch(connectionTree, /expanded\[key\]\s*=\s*true/)
})
