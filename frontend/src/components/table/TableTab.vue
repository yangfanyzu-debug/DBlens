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
.table-tab { height: 100%; display: flex; flex-direction: column; }
.sub-tabs { height: 100%; display: flex; flex-direction: column; }
:deep(.el-tabs__content) { flex: 1; overflow: hidden; }
:deep(.el-tab-pane) { height: 100%; }
</style>
