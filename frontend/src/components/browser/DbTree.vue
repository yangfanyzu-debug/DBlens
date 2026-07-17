<template>
  <div class="db-tree">
    <div class="db-tree-search">
      <el-input
        v-model="filterText"
        placeholder="搜索库 / 表 / 视图"
        size="small"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <button
        class="tree-refresh-btn"
        type="button"
        title="刷新表树"
        aria-label="刷新表树"
        :disabled="refreshingTree"
        @click="refreshTree"
      >
        <el-icon :class="{ spinning: refreshingTree }"><Refresh /></el-icon>
      </button>
    </div>
    <transition name="db-loading-fade">
      <div v-if="loadingRoot" class="db-tree-loading" role="status" aria-live="polite">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>加载数据库...</span>
      </div>
    </transition>
    <el-tree
      :key="treeKey"
      ref="treeRef"
      node-key="id"
      :data="treeData"
      :props="{ label: 'label', children: 'children', isLeaf: 'isLeaf' }"
      lazy
      :load="loadNode"
      :filter-node-method="filterNode"
      :node-contextmenu="onContextMenu"
      @node-click="onNodeClick"
      highlight-current
      :expand-on-click-node="true"
    >
      <template #default="{ node, data }">
        <span class="tree-node">
          <el-icon v-if="data.nodeType === 'database'" class="node-icon db"><Grid /></el-icon>
          <el-icon v-else-if="data.nodeType === 'table'" class="node-icon tbl"><Document /></el-icon>
          <el-icon v-else-if="data.nodeType === 'view'" class="node-icon view"><View /></el-icon>
          <span class="node-label">
            <template v-for="(part, index) in splitTreeSearchLabel(node.label, filterText)" :key="index">
              <mark v-if="part.match" class="search-hit">{{ part.text }}</mark>
              <span v-else>{{ part.text }}</span>
            </template>
          </span>
        </span>
      </template>
    </el-tree>

    <div v-if="menuData" class="ctx-menu" :style="menuStyle">
      <div class="ctx-item" @click="openData"><el-icon><Document /></el-icon> 查看数据</div>
      <div class="ctx-item" @click="openStructure"><el-icon><InfoFilled /></el-icon> 查看结构</div>
      <div class="ctx-divider" />
      <div class="ctx-item" @click="copyName"><el-icon><CopyDocument /></el-icon> 复制表名</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Grid, Document, View, InfoFilled, CopyDocument, Search, Loading, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as dbApi from '@/api/databases'
import { useTabsStore } from '@/stores/tabs'
import { useConnectionsStore } from '@/stores/connections'
import { useSchemaStore } from '@/stores/schema'
import { collapseTreeNode, expandTreeNode, getTreeStoreRoot, matchesTreeSearch, splitTreeSearchLabel } from '@/utils/treeSearch'
import { onDbSchemaChanged } from '@/utils/schemaRefresh'

const props = defineProps<{ connId: string }>()
const tabsStore = useTabsStore()
const connectionsStore = useConnectionsStore()
const schemaStore = useSchemaStore()

const treeData = ref<any[]>([])
const menuData = ref<any>(null)
const menuStyle = ref({})
const treeRef = ref<any>(null)
const filterText = ref('')
const loadingRoot = ref(false)
const refreshingTree = ref(false)
const treeKey = ref(0)
let removeSchemaChangedListener: (() => void) | null = null

onMounted(() => {
  removeSchemaChangedListener = onDbSchemaChanged(detail => {
    if (detail.connId !== props.connId) return
    refreshDatabaseNode(detail.database)
  })
})

onUnmounted(() => {
  removeSchemaChangedListener?.()
})

watch(() => props.connId, () => {
  treeData.value = []
  filterText.value = ''
})

watch(filterText, async (value, previousValue) => {
  await nextTick()
  const query = value.trim()
  if (query) expandAllDatabases()
  treeRef.value?.filter(value)
  if (!query && previousValue?.trim()) collapseAllDatabases()
})

function expandAllDatabases() {
  if (!treeRef.value?.store) return
  const root = getTreeStoreRoot(treeRef.value.store)
  if (!root) return
  for (const child of root.childNodes) {
    expandTreeNode(treeRef.value.store, child)
  }
}

function collapseAllDatabases() {
  if (!treeRef.value?.store) return
  const root = getTreeStoreRoot(treeRef.value.store)
  if (!root) return
  for (const child of root.childNodes) {
    collapseTreeNode(treeRef.value.store, child)
  }
}

async function loadNode(node: any, resolve: (data: any[]) => void) {
  if (node.level === 0) {
    loadingRoot.value = true
    try {
      const dbs = await dbApi.listDatabases(props.connId)
      resolve(dbs.map(createDatabaseNode))
    } catch (e: any) {
      ElMessage.error(e.message || '加载数据库失败')
      resolve([])
    } finally {
      loadingRoot.value = false
    }
    return
  }
  if (node.data.nodeType === 'database') {
    connectionsStore.setActiveDatabase(props.connId, node.data.database)
    resolve(await loadTableNodes(node.data.database))
    await nextTick()
    treeRef.value?.filter(filterText.value)
    return
  }
  resolve([])
}

function databaseNodeKey(database: string) {
  return `${props.connId}:db:${database}`
}

function tableNodeKey(database: string, table: string) {
  return `${props.connId}:table:${database}:${table}`
}

function createDatabaseNode(database: string) {
  return { id: databaseNodeKey(database), label: database, nodeType: 'database', connId: props.connId, database }
}

function createTableNode(database: string, table: { name: string; type: string }) {
  return {
    id: tableNodeKey(database, table.name),
    label: table.name,
    nodeType: table.type === 'VIEW' ? 'view' : 'table',
    connId: props.connId,
    database,
    table: table.name,
    isLeaf: true,
  }
}

async function loadTableNodes(database: string) {
  const tables = await dbApi.listTables(props.connId, database)
  schemaStore.loadSchema(props.connId, database)
  return tables.map((table: any) => createTableNode(database, table))
}

async function refreshDatabaseNode(database: string) {
  const key = databaseNodeKey(database)
  const node = treeRef.value?.store?.getNode?.(key)
  if (!node?.loaded) return false

  schemaStore.clearDatabase(props.connId, database)
  try {
    const children = await loadTableNodes(database)
    if (treeRef.value?.updateKeyChildren) {
      treeRef.value.updateKeyChildren(key, children)
    } else if (node.doCreateChildren) {
      node.childNodes = []
      node.doCreateChildren(children)
    }
    await nextTick()
    treeRef.value?.filter(filterText.value)
    return true
  } catch (e: any) {
    ElMessage.error(e.message || '刷新表列表失败')
    return false
  }
}

function getLoadedDatabaseNodes() {
  const root = treeRef.value?.store ? getTreeStoreRoot(treeRef.value.store) : null
  return (root?.childNodes ?? []).filter((node: any) => node?.data?.nodeType === 'database' && node.loaded)
}

async function refreshTree() {
  if (refreshingTree.value) return
  refreshingTree.value = true
  try {
    const loadedNodes = getLoadedDatabaseNodes()
    const activeDatabase = connectionsStore.activeDatabaseByConn[props.connId]
    const activeNode = loadedNodes.find((node: any) => node.data.database === activeDatabase)
    let refreshed = false

    if (activeNode) {
      refreshed = await refreshDatabaseNode(activeDatabase)
    } else if (loadedNodes.length) {
      const results = await Promise.all(loadedNodes.map((node: any) => refreshDatabaseNode(node.data.database)))
      refreshed = results.some(Boolean)
    } else {
      schemaStore.clearConnection(props.connId)
      treeKey.value += 1
      await nextTick()
      refreshed = true
    }
    if (refreshed) ElMessage.success('表树已刷新')
  } finally {
    refreshingTree.value = false
  }
}

function loadedDescendantMatches(node: any, query: string): boolean {
  return (node?.childNodes ?? []).some((child: any) =>
    matchesTreeSearch(child.data?.label, query) || loadedDescendantMatches(child, query)
  )
}

function filterNode(value: string, data: any, node: any) {
  if (!value.trim()) return true
  return matchesTreeSearch(data.label, value) || loadedDescendantMatches(node, value)
}

function onContextMenu(e: MouseEvent, data: any) {
  if (data.nodeType !== 'table' && data.nodeType !== 'view') return
  e.preventDefault()
  menuData.value = data
  menuStyle.value = { top: e.clientY + 'px', left: e.clientX + 'px' }
}

function onNodeClick(data: any) {
  menuData.value = null
  if (data.nodeType === 'database') {
    connectionsStore.setActiveDatabase(data.connId, data.database)
  }
  if (data.nodeType === 'table' || data.nodeType === 'view') {
    connectionsStore.setActiveDatabase(data.connId, data.database)
    tabsStore.openTableTab(data.connId, data.database, data.table)
  }
}

function openData() {
  if (!menuData.value) return
  connectionsStore.setActiveDatabase(menuData.value.connId, menuData.value.database)
  tabsStore.openTableTab(menuData.value.connId, menuData.value.database, menuData.value.table)
  menuData.value = null
}

function openStructure() {
  if (!menuData.value) return
  connectionsStore.setActiveDatabase(menuData.value.connId, menuData.value.database)
  tabsStore.openTableTab(menuData.value.connId, menuData.value.database, menuData.value.table)
  menuData.value = null
}

function copyName() {
  if (!menuData.value) return
  navigator.clipboard.writeText(menuData.value.table)
  ElMessage.success('已复制')
  menuData.value = null
}
</script>

<style scoped>
.db-tree { flex: 1; overflow-y: auto; padding: 4px 0; }
.db-tree-search {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px 8px;
  background: linear-gradient(180deg, var(--bg-secondary) 70%, rgba(0, 0, 0, 0));
}
.db-tree-search :deep(.el-input) {
  flex: 1;
  min-width: 0;
}
.db-tree-search :deep(.el-input__wrapper) {
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 1px var(--border-muted) inset;
}
.db-tree-search :deep(.el-input__inner) {
  font-size: 12px;
}
.tree-refresh-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid var(--border-muted);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  flex-shrink: 0;
}
.tree-refresh-btn:hover:not(:disabled) {
  color: var(--text-primary);
  border-color: var(--border-default);
  background: var(--bg-tertiary);
}
.tree-refresh-btn:disabled {
  cursor: wait;
  opacity: 0.72;
}
.spinning {
  animation: db-loading-spin 0.9s linear infinite;
}
.db-tree-loading {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 2px 10px 8px;
  padding: 6px 8px;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-muted);
  border-radius: var(--radius-md);
}
.loading-icon {
  color: var(--accent-blue);
  animation: db-loading-spin 0.9s linear infinite;
}
.db-loading-fade-enter-active,
.db-loading-fade-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}
.db-loading-fade-enter-from,
.db-loading-fade-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}
@keyframes db-loading-spin {
  to { transform: rotate(360deg); }
}
.tree-node { display: flex; align-items: center; gap: 5px; font-size: 13px; }
.node-icon { font-size: 12px; }
.node-icon.db { color: var(--accent-purple); }
.node-icon.tbl { color: var(--accent-blue); }
.node-icon.view { color: var(--accent-orange); }
.node-label { color: var(--text-secondary); }
.node-label:hover { color: var(--text-primary); }
.search-hit {
  padding: 0 1px;
  border-radius: 3px;
  background: rgba(210, 153, 34, 0.28);
  color: var(--text-primary);
}

/* el-tree overrides for dark theme */
:deep(.el-tree) {
  background: transparent;
  color: var(--text-secondary);
}
:deep(.el-tree-node__content) {
  height: 28px;
  border-radius: var(--radius-sm);
  margin: 1px 6px;
  padding-left: 6px !important;
  transition: background 0.1s;
}
:deep(.el-tree-node__content:hover) {
  background: rgba(88, 166, 255, 0.06);
}
:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: var(--glow-blue) !important;
}
:deep(.el-tree-node__expand-icon) {
  color: var(--text-muted);
  font-size: 10px;
}
:deep(.el-tree-node__expand-icon.is-leaf) {
  color: transparent;
}

/* Context menu */
.ctx-menu {
  position: fixed;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 9999;
  min-width: 150px;
  padding: 4px;
}
.ctx-item {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 12px;
  cursor: pointer;
  font-size: 13px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all 0.1s;
}
.ctx-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.ctx-divider { height: 1px; background: var(--border-muted); margin: 4px 0; }
</style>
