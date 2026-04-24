<template>
  <div class="sidebar-container">
    <div class="sidebar-header">
      <div class="brand-block">
        <div class="logo-mark">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <ellipse cx="12" cy="6" rx="9" ry="3" stroke="#58a6ff" stroke-width="1.5"/>
            <path d="M3 6v6c0 1.66 4.03 3 9 3s9-1.34 9-3V6" stroke="#58a6ff" stroke-width="1.5"/>
            <path d="M3 12v6c0 1.66 4.03 3 9 3s9-1.34 9-3v-6" stroke="#58a6ff" stroke-width="1.5" stroke-opacity="0.5"/>
          </svg>
        </div>
        <div class="brand-copy">
          <span class="title">DBLens</span>
          <span class="subtitle">数据库工作台</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button size="small" type="primary" @click="showForm = true" class="new-btn">
          <Plus style="width:14px;height:14px" /> 新建
        </el-button>
      </div>
    </div>
    <div class="sidebar-body">
      <div class="section-label">
        <span>连接</span>
      </div>
      <ConnectionTree @open-db-tree="onOpenDbTree" />
      <!-- 数据库表树折叠面板 -->
      <div v-if="activeConnId" class="db-panel">
        <div class="db-panel-header" @click="dbPanelOpen = !dbPanelOpen">
          <el-icon class="db-panel-caret" :class="{ open: dbPanelOpen }">
            <CaretBottom />
          </el-icon>
          <span class="db-panel-title">{{ connections.find(c => c.id === activeConnId)?.name }}</span>
          <el-tag size="small" class="db-panel-status">已连接</el-tag>
        </div>
        <div v-show="dbPanelOpen" class="db-panel-body">
          <DbTree :key="activeConnId" :conn-id="activeConnId" />
        </div>
      </div>
    </div>
    <ConnectionForm v-model:visible="showForm" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, CaretBottom } from '@element-plus/icons-vue'
import { useConnectionsStore } from '@/stores/connections'
import { storeToRefs } from 'pinia'
import ConnectionTree from '@/components/connection/ConnectionTree.vue'
import DbTree from '@/components/browser/DbTree.vue'
import ConnectionForm from '@/components/connection/ConnectionForm.vue'

const showForm = ref(false)
const store = useConnectionsStore()
const { activeConnId, connections } = storeToRefs(store)
const dbPanelOpen = ref(false)

function onOpenDbTree(connId: string) {
  store.activeConnId = connId
}

watch(activeConnId, () => { dbPanelOpen.value = false })
</script>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-secondary);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-default);
  background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  flex-shrink: 0;
  gap: 12px;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-md);
  background: var(--glow-blue);
  border: 1px solid rgba(88, 166, 255, 0.2);
  flex-shrink: 0;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.title {
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0.2px;
  line-height: 1.2;
  color: var(--text-primary);
}

.subtitle {
  font-size: 11px;
  line-height: 1.2;
  color: var(--text-secondary);
}

.header-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.new-btn {
  font-size: 12px;
  gap: 4px;
  padding-inline: 10px;
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px 0 20px;
}

.section-label {
  display: flex;
  align-items: center;
  padding: 0 14px 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

/* 数据库表树折叠面板 */
.db-panel {
  margin-top: 16px;
  border-top: 1px solid var(--border-muted);
}

.db-panel-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  cursor: pointer;
  user-select: none;
  transition: background 0.12s ease;
}
.db-panel-header:hover {
  background: var(--shell-hover);
}

.db-panel-caret {
  font-size: 10px;
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}
.db-panel-caret.open {
  transform: rotate(180deg);
}

.db-panel-title {
  flex: 1;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.db-panel-status {
  font-size: 10px;
  background: var(--accent-green);
  color: #fff;
  border: none;
  flex-shrink: 0;
}
</style>
