<template>
  <div class="tab-bar">
    <div
      v-for="tab in tabs"
      :key="tab.id"
      class="tab-item"
      :class="{ active: tab.id === activeTabId }"
      @click="tabsStore.activeTabId = tab.id"
    >
      <el-icon v-if="tab.type === 'editor'"><EditPen /></el-icon>
      <el-icon v-else><Grid /></el-icon>
      <span class="tab-title">{{ tab.title }}</span>
      <el-icon class="close-btn" @click.stop="tabsStore.closeTab(tab.id)"><Close /></el-icon>
    </div>
    <div class="tab-actions">
      <el-tooltip content="新建 SQL 编辑器">
        <el-icon class="action-btn" @click="newEditor"><Plus /></el-icon>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { EditPen, Grid, Close, Plus } from '@element-plus/icons-vue'
import { useTabsStore } from '@/stores/tabs'
import { useConnectionsStore } from '@/stores/connections'

const tabsStore = useTabsStore()
const { tabs, activeTabId } = storeToRefs(tabsStore)
const connStore = useConnectionsStore()

function newEditor() {
  tabsStore.openEditorTab(connStore.activeConnId ?? '')
}
</script>

<style scoped>
.tab-bar {
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--el-border-color);
  background: var(--el-bg-color-page);
  overflow-x: auto;
  min-height: 36px;
}
.tab-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 12px;
  height: 36px;
  cursor: pointer;
  font-size: 13px;
  border-right: 1px solid var(--el-border-color);
  white-space: nowrap;
  user-select: none;
}
.tab-item:hover { background: var(--el-fill-color-light); }
.tab-item.active { background: var(--el-bg-color); border-bottom: 2px solid var(--el-color-primary); }
.tab-title { max-width: 120px; overflow: hidden; text-overflow: ellipsis; }
.close-btn { margin-left: 4px; opacity: 0.5; }
.close-btn:hover { opacity: 1; color: var(--el-color-danger); }
.tab-actions { margin-left: auto; padding: 0 8px; }
.action-btn { cursor: pointer; color: var(--el-text-color-secondary); }
.action-btn:hover { color: var(--el-color-primary); }
</style>
