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
      <ConnectionTree @open-db-tree="onOpenDbTree" />
      <DbTree v-if="activeConnId" :key="activeConnId" :conn-id="activeConnId" />
    </div>
    <ConnectionForm v-model:visible="showForm" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { useConnectionsStore } from '@/stores/connections'
import { storeToRefs } from 'pinia'
import ConnectionTree from '@/components/connection/ConnectionTree.vue'
import DbTree from '@/components/browser/DbTree.vue'
import ConnectionForm from '@/components/connection/ConnectionForm.vue'

const showForm = ref(false)
const store = useConnectionsStore()
const { activeConnId } = storeToRefs(store)

function onOpenDbTree(connId: string) {
  store.activeConnId = connId
}
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
  flex-direction: column;
  align-items: stretch;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--border-default);
  background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  flex-shrink: 0;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  background: var(--glow-blue);
  border: 1px solid rgba(88, 166, 255, 0.2);
  flex-shrink: 0;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.title {
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.3px;
  line-height: 1.2;
  color: var(--text-primary);
}

.subtitle {
  font-size: 12px;
  line-height: 1.2;
  color: var(--text-secondary);
}

.header-actions {
  display: flex;
  justify-content: flex-end;
}

.new-btn {
  font-size: 12px;
  gap: 4px;
  padding-inline: 12px;
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 0 14px;
}
</style>
