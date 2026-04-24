<template>
  <div class="tab-bar">
    <!-- 左侧溢出下拉（tab 过多时显示） -->
    <el-dropdown v-if="overflowCount > 0" trigger="click" @command="onSelectTab">
      <div class="tab-overflow-btn">
        <el-icon><MoreFilled /></el-icon>
        <span class="overflow-count">{{ overflowCount }}</span>
      </div>
      <template #dropdown>
        <el-dropdown-menu class="tab-overflow-menu">
          <el-dropdown-item
            v-for="tab in overflowTabs"
            :key="tab.id"
            :command="tab.id"
            :class="{ 'is-active': tab.id === activeTabId }"
          >
            <el-icon class="tab-icon" :size="11">
              <EditPen v-if="tab.type === 'editor'" />
              <Grid v-else />
            </el-icon>
            <span class="tab-label">{{ tab.title }}</span>
            <el-icon class="close-icon" :size="10" @click.stop="tabsStore.closeTab(tab.id)"><Close /></el-icon>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 可见 tabs 区域（只渲染可见的 tab） -->
    <div class="tabs-scroll" ref="scrollRef">
      <div
        v-for="tab in visibleTabs"
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

    <!-- 右侧操作区 -->
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
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { EditPen, Grid, Close, Plus, QuestionFilled, MoreFilled } from '@element-plus/icons-vue'
import { useTabsStore } from '@/stores/tabs'
import { useConnectionsStore } from '@/stores/connections'

const TAB_EST_WIDTH = 120  // 每个 tab 的估算宽度（px）
const ACTION_WIDTH = 160    // 右侧 action 区宽度（px）

const tabsStore = useTabsStore()
const { tabs, activeTabId } = storeToRefs(tabsStore)
const connStore = useConnectionsStore()
const scrollRef = ref<HTMLElement>()

function newEditor() {
  tabsStore.openEditorTab(connStore.activeConnId ?? '')
}

function onSelectTab(tabId: string) {
  tabsStore.activeTabId = tabId
}

// 基于容器宽度估算能显示多少个 tab
const visibleCount = computed(() => {
  const containerW = scrollRef.value?.clientWidth ?? 0
  const availW = containerW - ACTION_WIDTH
  if (availW <= 0) return 0
  return Math.max(0, Math.floor(availW / TAB_EST_WIDTH))
})

const overflowCount = computed(() => Math.max(0, tabs.value.length - visibleCount.value))
const overflowTabs = computed(() => tabs.value.slice(0, overflowCount.value))
const visibleTabs = computed(() => tabs.value.slice(overflowCount.value))
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
  min-width: 0;
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
  flex-shrink: 0;
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

/* 左侧溢出按钮 */
.tab-overflow-btn {
  display: flex;
  align-items: center;
  gap: 3px;
  margin: 6px 4px 6px 0;
  padding: 0 8px;
  height: 28px;
  border: 1px solid var(--border-muted);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  flex-shrink: 0;
  transition: all 0.12s ease;
}
.tab-overflow-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}
.overflow-count {
  font-size: 10px;
  font-weight: 600;
  background: var(--bg-tertiary);
  padding: 0 4px;
  border-radius: 999px;
  min-width: 16px;
  text-align: center;
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
  background: var(--bg-teriary);
  border-color: var(--border-muted);
  color: var(--text-secondary);
}
.action-btn:focus-visible {
  outline: 2px solid var(--glow-blue);
  outline-offset: 1px;
}
.action-btn .btn-label {
  font-size: 12px;
  white-space: nowrap;
  margin-left: 4px;
}
</style>

<style>
.tab-overflow-menu .el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 160px;
  padding: 6px 10px;
  font-size: 12.5px;
  color: var(--text-secondary);
  background: transparent !important;
}
.tab-overflow-menu .el-dropdown-menu__item .tab-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
}
.tab-overflow-menu .el-dropdown-menu__item .close-icon {
  opacity: 0;
  color: var(--text-muted);
  transition: opacity 0.1s;
  flex-shrink: 0;
}
.tab-overflow-menu .el-dropdown-menu__item:hover {
  background: var(--el-color-primary) !important;
  color: #fff !important;
  border-radius: 6px;
}
.tab-overflow-menu .el-dropdown-menu__item:hover .tab-label,
.tab-overflow-menu .el-dropdown-menu__item:hover .close-icon {
  color: #fff !important;
}
.tab-overflow-menu .el-dropdown-menu__item:hover .close-icon {
  opacity: 1;
}
.tab-overflow-menu .el-dropdown-menu__item.is-active {
  background: var(--bg-tertiary) !important;
}
.tab-overflow-menu .el-dropdown-menu__item.is-active .tab-label {
  color: var(--accent-blue);
  font-weight: 600;
}
</style>
