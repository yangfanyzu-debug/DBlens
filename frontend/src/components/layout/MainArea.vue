<template>
  <div class="main-area-container">
    <TabBar />
    <div class="tab-content">
      <template v-for="tab in tabs" :key="tab.id">
        <div v-show="tab.id === activeTabId" class="tab-pane">
          <EditorTab v-if="tab.type === 'editor'" :tab="tab" />
          <TableTab v-else-if="tab.type === 'table'" :tab="tab" />
        </div>
      </template>
      <div v-if="!tabs.length" class="empty-state">
        <el-empty description="选择左侧连接或表开始使用" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTabsStore } from '@/stores/tabs'
import TabBar from '@/components/common/TabBar.vue'
import EditorTab from '@/components/editor/EditorTab.vue'
import TableTab from '@/components/table/TableTab.vue'

const { tabs, activeTabId } = storeToRefs(useTabsStore())
</script>

<style scoped>
.main-area-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.tab-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}
.tab-pane {
  height: 100%;
}
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
