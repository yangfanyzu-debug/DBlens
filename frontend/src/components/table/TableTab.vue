<template>
  <div class="table-tab">
    <el-tabs v-model="activeSubTab" class="sub-tabs">
      <el-tab-pane label="数据" name="data">
        <DataGrid :tab="tab" />
      </el-tab-pane>
      <el-tab-pane label="结构" name="structure">
        <StructureView :tab="tab" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Tab } from '@/stores/tabs'
import DataGrid from './DataGrid.vue'
import StructureView from './StructureView.vue'

defineProps<{ tab: Tab }>()
const activeSubTab = ref('data')
</script>

<style scoped>
.table-tab {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.sub-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.el-tabs__header) {
  margin: 0;
  padding: 0 16px;
  background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  border-bottom: 1px solid var(--border-default);
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  height: 40px;
  font-weight: 600;
  color: var(--text-secondary);
}

:deep(.el-tabs__item.is-active) {
  color: var(--accent-blue);
}

:deep(.el-tabs__active-bar) {
  background: var(--accent-blue);
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  background: var(--bg-primary);
}

:deep(.el-tab-pane) {
  height: 100%;
}
</style>
