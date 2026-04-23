<template>
  <div class="app-layout">
    <div class="sidebar">
      <Sidebar />
    </div>
    <div class="main-area">
      <MainArea />
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import MainArea from './MainArea.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}
.sidebar {
  width: 260px;
  min-width: 180px;
  max-width: 400px;
  border-right: 1px solid var(--el-border-color);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.main-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
