<template>
  <div class="app-layout">
    <aside class="sidebar" :style="{ width: sidebarWidth + 'px' }">
      <Sidebar />
      <div class="drag-handle" @mousedown="startResize" />
    </aside>
    <main class="main-area">
      <MainArea />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import MainArea from './MainArea.vue'

const MIN_W = 220
const MAX_W = 400
const stored = localStorage.getItem('sidebar-width')
const sidebarWidth = ref(stored ? parseInt(stored) : 260)

let resizing = false
let startX = 0
let startW = 0

function startResize(e: MouseEvent) {
  resizing = true
  startX = e.clientX
  startW = sidebarWidth.value
  document.addEventListener('mousemove', doResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'
}

function doResize(e: MouseEvent) {
  if (!resizing) return
  const delta = e.clientX - startX
  sidebarWidth.value = Math.max(MIN_W, Math.min(MAX_W, startW + delta))
}

function stopResize() {
  resizing = false
  document.removeEventListener('mousemove', doResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
  localStorage.setItem('sidebar-width', String(sidebarWidth.value))
}
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(180deg, var(--shell-backdrop-soft) 0%, var(--shell-backdrop) 120px);
}
.sidebar {
  position: relative;
  /* width/min-width/max-width handled by inline style */
  background: linear-gradient(180deg, var(--shell-sidebar-tint) 0%, var(--shell-sidebar-bg) 100%);
  border-right: 1px solid var(--border-default);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shell-shadow-strong);
  flex-shrink: 0;
}
.drag-handle {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  cursor: col-resize;
  background: transparent;
  transition: background-color 0.15s ease, opacity 0.15s ease;
  z-index: 10;
}
.drag-handle::before {
  content: '';
  position: absolute;
  top: 12px;
  bottom: 12px;
  left: 50%;
  width: 2px;
  transform: translateX(-50%);
  border-radius: 999px;
  background: rgba(139, 148, 158, 0.55);
  opacity: 0.55;
}
.drag-handle:hover {
  background: var(--glow-blue);
}
.drag-handle:hover::before {
  background: var(--accent-blue);
  opacity: 0.95;
}
.main-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, var(--shell-main-tint) 0%, var(--shell-main-bg) 100%);
}
</style>
