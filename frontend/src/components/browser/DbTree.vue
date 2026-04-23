<template>
  <div class="db-tree">
    <el-tree
      :data="treeData"
      :props="{ label: 'label', children: 'children', isLeaf: 'isLeaf' }"
      lazy
      :load="loadNode"
      @node-contextmenu="onContextMenu"
      @node-click="onNodeClick"
    >
      <template #default="{ node, data }">
        <span class="tree-node">
          <el-icon v-if="data.nodeType === 'database'"><Grid /></el-icon>
          <el-icon v-else-if="data.nodeType === 'table'"><Document /></el-icon>
          <el-icon v-else-if="data.nodeType === 'view'"><View /></el-icon>
          <span>{{ node.label }}</span>
        </span>
      </template>
    </el-tree>

    <div v-if="menuData" class="ctx-menu" :style="menuStyle" @mouseleave="menuData = null">
      <div class="ctx-item" @click="openData">查看数据</div>
      <div class="ctx-item" @click="openStructure">查看结构</div>
      <div class="ctx-item" @click="copyName">复制表名</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Grid, Document, View } from '@element-plus/icons-vue'
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

watch(() => props.connId, () => { treeData.value = [] })

async function loadNode(node: any, resolve: (data: any[]) => void) {
  if (node.level === 0) {
    const dbs = await dbApi.listDatabases(props.connId)
    resolve(dbs.map((d: string) => ({ label: d, nodeType: 'database', connId: props.connId, database: d })))
    return
  }
  if (node.data.nodeType === 'database') {
    const tables = await dbApi.listTables(props.connId, node.data.database)
    // preload schema for autocomplete
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
.tree-node { display: flex; align-items: center; gap: 4px; font-size: 13px; }
.ctx-menu { position: fixed; background: var(--el-bg-color); border: 1px solid var(--el-border-color); border-radius: 4px; box-shadow: var(--el-box-shadow-light); z-index: 9999; min-width: 120px; }
.ctx-item { padding: 8px 16px; cursor: pointer; font-size: 13px; }
.ctx-item:hover { background: var(--el-fill-color-light); }
</style>
