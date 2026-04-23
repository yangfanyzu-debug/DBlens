<template>
  <div class="sidebar-container">
    <div class="sidebar-header">
      <span class="title">DBLens</span>
      <el-button size="small" type="primary" @click="showForm = true">+ 新建连接</el-button>
    </div>
    <ConnectionTree @open-db-tree="onOpenDbTree" />
    <DbTree v-if="activeConnId" :key="activeConnId" :conn-id="activeConnId" />
    <ConnectionForm v-model:visible="showForm" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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
  background: var(--el-bg-color-page);
}
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid var(--el-border-color);
}
.title {
  font-weight: 600;
  font-size: 15px;
}
</style>
