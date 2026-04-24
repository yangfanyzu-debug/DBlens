<template>
  <div class="db-tree">
    <el-tree
      ref="treeRef"
      :data="treeData"
      :props="{ label: 'label', children: 'children', isLeaf: 'isLeaf' }"
      lazy
      :load="loadNode"
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
          <span class="node-label">{{ node.label }}</span>
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
import { ref, watch, nextTick, onMounted } from 'vue'
import { Grid, Document, View, InfoFilled, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as dbApi from '@/api/databases'
import { useTabsStore } from '@/stores/tabs'
import { useSchemaStore } from '@/stores/schema'

const props = defineProps<{ connId: string }>()
const tabsStore = useTabsStore()
const schemaStore = useSchemaStore()

const treeData = ref<any[]>([])
const menuData = ref<any>(null)
const menuStyle = ref({})
const treeRef = ref<any>(null)

watch(() => props.connId, () => { treeData.value = [] })

onMounted(async () => {
  // Initial level-0 load (databases) happens via lazy load trigger.
  // Wait for render then auto-expand all database nodes.
  await nextTick()
  expandAllDatabases()
})

function expandAllDatabases() {
  if (!treeRef.value?.store) return
  const root = treeRef.value.store.state.root
  if (!root) return
  for (const child of root.childNodes) {
    treeRef.value.store.expandNode(child)
  }
}

async function loadNode(node: any, resolve: (data: any[]) => void) {
  if (node.level === 0) {
    const dbs = await dbApi.listDatabases(props.connId)
    resolve(dbs.map((d: string) => ({ label: d, nodeType: 'database', connId: props.connId, database: d })))
    await nextTick()
    expandAllDatabases()
    return
  }
  if (node.data.nodeType === 'database') {
    const tables = await dbApi.listTables(props.connId, node.data.database)
    schemaStore.loadSchema(props.connId, node.data.database)
    resolve(tables.map((t: any) => ({
      label: t.name,
      nodeType: t.type === 'VIEW' ? 'view' : 'table',
      connId: props.connId,
      database: node.data.database,
      table: t.name,
      isLeaf: true,
    })))
    return
  }
  resolve([])
}

function onContextMenu(e: MouseEvent, data: any) {
  if (data.nodeType !== 'table' && data.nodeType !== 'view') return
  e.preventDefault()
  menuData.value = data
  menuStyle.value = { top: e.clientY + 'px', left: e.clientX + 'px' }
}

function onNodeClick(data: any) {
  menuData.value = null
  if (data.nodeType === 'table' || data.nodeType === 'view') {
    tabsStore.openTableTab(data.connId, data.database, data.table)
  }
}

function openData() {
  if (!menuData.value) return
  tabsStore.openTableTab(menuData.value.connId, menuData.value.database, menuData.value.table)
  menuData.value = null
}

function openStructure() {
  if (!menuData.value) return
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
.tree-node { display: flex; align-items: center; gap: 5px; font-size: 13px; }
.node-icon { font-size: 12px; }
.node-icon.db { color: var(--accent-purple); }
.node-icon.tbl { color: var(--accent-blue); }
.node-icon.view { color: var(--accent-orange); }
.node-label { color: var(--text-secondary); }
.node-label:hover { color: var(--text-primary); }

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
