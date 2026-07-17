import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import assert from 'node:assert/strict'

const { collapseTreeNode, expandTreeNode, getTreeStoreRoot, matchesTreeSearch, splitTreeSearchLabel } = await import('../src/utils/treeSearch.ts')
const dbTree = readFileSync(new URL('../src/components/browser/DbTree.vue', import.meta.url), 'utf8')

test('matchesTreeSearch matches labels case-insensitively', () => {
  assert.equal(matchesTreeSearch('Order_Detail', 'order'), true)
  assert.equal(matchesTreeSearch('Order_Detail', 'DETAIL'), true)
  assert.equal(matchesTreeSearch('Order_Detail', 'user'), false)
})

test('getTreeStoreRoot tolerates Element Plus tree store shape differences', () => {
  assert.equal(getTreeStoreRoot(undefined), null)
  assert.deepEqual(getTreeStoreRoot({ state: { root: { id: 'state-root' } } }), { id: 'state-root' })
  assert.deepEqual(getTreeStoreRoot({ root: { id: 'direct-root' } }), { id: 'direct-root' })
})

test('expandTreeNode uses the available Element Plus node expansion API', () => {
  let storeExpanded = false
  expandTreeNode({ expandNode: () => { storeExpanded = true } }, {})
  assert.equal(storeExpanded, true)

  let nodeExpanded = false
  expandTreeNode({}, { expand: () => { nodeExpanded = true } })
  assert.equal(nodeExpanded, true)

  assert.doesNotThrow(() => expandTreeNode({}, {}))
})

test('collapseTreeNode uses the available Element Plus node collapse API', () => {
  let storeCollapsed = false
  collapseTreeNode({ collapseNode: () => { storeCollapsed = true } }, {})
  assert.equal(storeCollapsed, true)

  let nodeCollapsed = false
  collapseTreeNode({}, { collapse: () => { nodeCollapsed = true } })
  assert.equal(nodeCollapsed, true)

  const node = { expanded: true }
  collapseTreeNode({}, node)
  assert.equal(node.expanded, false)
})

test('splitTreeSearchLabel returns highlighted match segments', () => {
  assert.deepEqual(splitTreeSearchLabel('user_order_log', 'order'), [
    { text: 'user_', match: false },
    { text: 'order', match: true },
    { text: '_log', match: false },
  ])
})

test('DbTree renders a database object search input', () => {
  assert.match(dbTree, /placeholder="搜索库 \/ 表 \/ 视图"/)
  assert.match(dbTree, /aria-label="刷新表树"/)
  assert.match(dbTree, /node-key="id"/)
  assert.match(dbTree, /filter-node-method="filterNode"/)
})

test('DbTree keeps databases collapsed until the user searches or expands them', () => {
  const expansionCalls = dbTree.match(/expandAllDatabases\(\)/g) ?? []
  assert.equal(expansionCalls.length, 2)
  assert.doesNotMatch(dbTree, /onMounted\(\(\) => \{\s*expandAllDatabases/s)
})

test('DbTree collapses database nodes when search is cleared', () => {
  assert.match(dbTree, /watch\(filterText, async \(value, previousValue\)/)
  assert.match(dbTree, /collapseAllDatabases\(\)/)
  assert.match(dbTree, /if \(!query && previousValue\?\.trim\(\)\) collapseAllDatabases\(\)/)
})

test('DbTree refreshes loaded database nodes after schema changes', () => {
  assert.match(dbTree, /onDbSchemaChanged/)
  assert.match(dbTree, /refreshDatabaseNode/)
  assert.match(dbTree, /schemaStore\.clearDatabase/)
  assert.match(dbTree, /updateKeyChildren/)
})

test('DbTree exposes manual refresh for loaded schema nodes', () => {
  assert.match(dbTree, /@click="refreshTree"/)
  assert.match(dbTree, /refreshingTree/)
  assert.match(dbTree, /getLoadedDatabaseNodes/)
  assert.match(dbTree, /schemaStore\.clearConnection/)
  assert.match(dbTree, /treeKey\.value \+= 1/)
})
