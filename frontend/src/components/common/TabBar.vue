<template>
  <div class="tab-bar">
    <div class="tabs-scroll">
      <div
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-item"
        :class="{ active: tab.id === activeTabId }"
        @click="tabsStore.activeTabId = tab.id"
      >
        <el-icon class="tab-icon" :size="13">
          <EditPen v-if="tab.type === 'editor'" />
          <Grid v-else />
        </el-icon>
        <span class="tab-title">{{ tab.title }}</span>
        <el-icon class="close-btn" :size="12" @click.stop="tabsStore.closeTab(tab.id)"><Close /></el-icon>
      </div>
    </div>
    <div class="tab-actions">
      <el-tooltip content="新建查询" placement="bottom">
        <button class="action-btn" @click="newEditor">
          <Plus style="width:14px;height:14px" />
          <span class="btn-label">新建查询</span>
        </button>
      </el-tooltip>
      <el-tooltip content="问题记录" placement="bottom">
        <a href="https://www.baidu.com" target="_blank" rel="noopener" class="action-btn">
          <QuestionFilled style="width:14px;height:14px" />
        </a>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { EditPen, Grid, Close, Plus, QuestionFilled } from '@element-plus/icons-vue'
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
  align-items: stretch;
  height: 42px;
  padding: 0 8px 0 10px;
  background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  border-bottom: 1px solid var(--border-muted);
  overflow: hidden;
  flex-shrink: 0;
}
.tabs-scroll {
  display: flex;
  align-items: stretch;
  overflow-x: auto;
  flex: 1;
  gap: 6px;
  scrollbar-width: none;
}
.tabs-scroll::-webkit-scrollbar { display: none; }

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 6px 0;
  padding: 0 12px;
  cursor: pointer;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-muted);
  border: 1px solid transparent;
  border-radius: 10px;
  white-space: nowrap;
  user-select: none;
  transition: color 0.12s ease, background 0.12s ease, border-color 0.12s ease, box-shadow 0.12s ease;
  position: relative;
}
.tab-item:hover {
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  border-color: var(--border-muted);
}
.tab-item.active {
  color: var(--text-primary);
  background: var(--bg-primary);
  border-color: var(--el-color-primary-light-5);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}
.tab-item.active::before {
  content: '';
  position: absolute;
  left: 10px;
  right: 10px;
  top: 0;
  height: 2px;
  border-radius: 999px;
  background: var(--accent-blue);
}
.tab-icon { opacity: 0.7; flex-shrink: 0; }
.tab-item.active .tab-icon { opacity: 1; }
.tab-title { max-width: 140px; overflow: hidden; text-overflow: ellipsis; }

.close-btn {
  opacity: 0;
  margin-left: 4px;
  padding: 2px;
  border-radius: 3px;
  color: var(--text-muted);
  transition: all 0.1s ease;
}
.tab-item:hover .close-btn,
.tab-item.active .close-btn { opacity: 0.7; }
.close-btn:hover {
  opacity: 1 !important;
  background: rgba(248, 81, 73, 0.15);
  color: var(--accent-red);
}

.tab-actions {
  display: flex;
  align-items: center;
  margin: 6px 0 6px 10px;
  padding-left: 10px;
  border-left: 1px solid var(--border-muted);
  flex-shrink: 0;
  gap: 6px;
}
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  padding: 0 8px;
  border: 1px solid transparent;
  background: var(--bg-primary);
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.12s ease;
  text-decoration: none;
}
.action-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--border-muted);
  color: var(--text-secondary);
}
.action-btn:focus-visible {
  outline: 2px solid var(--glow-blue);
  outline-offset: 1px;
}

/* 新建查询按钮支持文字 */
.action-btn .btn-label {
  font-size: 12px;
  white-space: nowrap;
  margin-left: 4px;
}
</style>
