<template>
  <div class="tab-bar">
    <div class="tab-scroll-control">
      <button
        type="button"
        class="chrome-btn"
        :disabled="!canScrollLeft"
        aria-label="向左滚动标签"
        @click="scrollTabs('left')"
      >
        <el-icon><ArrowLeftBold /></el-icon>
      </button>
    </div>

    <div class="tab-track-shell">
      <div ref="trackRef" class="tab-track" @scroll="updateScrollState">
        <div class="tab-track-inner">
          <button
            v-for="tab in tabs"
            :ref="el => setTabRef(tab.id, el)"
            :key="tab.id"
            type="button"
            class="tab-item"
            :class="{ active: tab.id === activeTabId }"
            @click="activateTab(tab.id)"
          >
            <el-icon class="tab-icon" :size="13">
              <EditPen v-if="tab.type === 'editor'" />
              <Grid v-else />
            </el-icon>
            <span class="tab-title">{{ tab.title }}</span>
            <el-icon class="close-btn" :size="12" @click.stop="closeTab(tab.id)"><Close /></el-icon>
          </button>
        </div>
      </div>
    </div>

    <div class="tab-scroll-control">
      <button
        type="button"
        class="chrome-btn"
        :disabled="!canScrollRight"
        aria-label="向右滚动标签"
        @click="scrollTabs('right')"
      >
        <el-icon><ArrowRightBold /></el-icon>
      </button>
    </div>

    <div class="tab-actions">
      <el-tooltip content="新建查询" placement="bottom">
        <button type="button" class="action-btn" @click="newEditor">
          <el-icon :size="14"><Plus /></el-icon>
          <span class="btn-label">新建查询</span>
        </button>
      </el-tooltip>
      <el-tooltip content="问题记录" placement="bottom">
        <a :href="issueLogUrl" target="_blank" rel="noopener" class="action-btn" aria-label="问题记录">
          <el-icon :size="14"><QuestionFilled /></el-icon>
        </a>
      </el-tooltip>
    </div>

    <div class="tab-panel-zone">
      <el-popover
        v-model:visible="panelVisible"
        trigger="click"
        placement="bottom-end"
        :width="320"
        popper-class="tab-list-popover"
      >
        <template #reference>
          <button
            type="button"
            class="chrome-btn tab-list-btn"
            :class="{ active: panelVisible }"
            aria-label="查看全部标签"
          >
            <el-icon><Operation /></el-icon>
            <span class="tab-count">{{ tabs.length }}</span>
          </button>
        </template>

        <div class="tab-list-panel">
          <div class="tab-list-header">
            <div class="tab-list-title">
              <span>全部标签</span>
              <span class="tab-list-subtitle">{{ tabs.length }} 个</span>
            </div>
            <button
              type="button"
              class="panel-action"
              :disabled="tabs.length === 0"
              @click="closeAllTabs"
            >
              关闭全部
            </button>
          </div>

          <div v-if="tabs.length > 0" class="tab-list-body">
            <div
              v-for="tab in tabs"
              :key="`panel-${tab.id}`"
              class="tab-list-row"
              :class="{ active: tab.id === activeTabId }"
              @click="activateTab(tab.id, true)"
            >
              <el-icon class="tab-icon" :size="13">
                <EditPen v-if="tab.type === 'editor'" />
                <Grid v-else />
              </el-icon>
              <span class="tab-list-label">{{ tab.title }}</span>
              <button
                v-if="tabs.length > 1"
                type="button"
                class="row-action"
                @click.stop="closeOtherTabs(tab.id)"
              >
                关闭其他
              </button>
              <button
                type="button"
                class="row-close"
                aria-label="关闭标签"
                @click.stop="closeTab(tab.id)"
              >
                <el-icon :size="12"><Close /></el-icon>
              </button>
            </div>
          </div>

          <div v-else class="tab-list-empty">
            暂无打开标签
          </div>
        </div>
      </el-popover>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch, type ComponentPublicInstance } from 'vue'
import { storeToRefs } from 'pinia'
import { ArrowLeftBold, ArrowRightBold, EditPen, Grid, Close, Operation, Plus, QuestionFilled } from '@element-plus/icons-vue'
import { useTabsStore } from '@/stores/tabs'
import { useConnectionsStore } from '@/stores/connections'

type TabElement = Element | ComponentPublicInstance | null
type ScrollDirection = 'left' | 'right'
type ScrollBehaviorMode = 'auto' | 'smooth'

const tabsStore = useTabsStore()
const { tabs, activeTabId } = storeToRefs(tabsStore)
const connectionsStore = useConnectionsStore()

const trackRef = ref<HTMLElement>()
const panelVisible = ref(false)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
const issueLogUrl = 'https://www.baidu.com'

const tabRefs = new Map<string, HTMLElement>()
let resizeObserver: ResizeObserver | null = null

function setTabRef(id: string, el: TabElement) {
  if (el instanceof HTMLElement) {
    tabRefs.set(id, el)
    return
  }

  tabRefs.delete(id)
}

function updateScrollState() {
  const track = trackRef.value
  if (!track) {
    canScrollLeft.value = false
    canScrollRight.value = false
    return
  }

  canScrollLeft.value = track.scrollLeft > 1
  canScrollRight.value = track.scrollLeft + track.clientWidth < track.scrollWidth - 1
}

function scrollTabs(direction: ScrollDirection) {
  const track = trackRef.value
  if (!track) return

  const offset = Math.max(track.clientWidth * 0.7, 180)
  const delta = direction === 'left' ? -offset : offset
  track.scrollBy({ left: delta, behavior: 'smooth' })
}

function scrollTabIntoView(tabId: string, behavior: ScrollBehaviorMode = 'smooth') {
  const track = trackRef.value
  const tabEl = tabRefs.get(tabId)
  if (!track || !tabEl) return

  const padding = 12
  const tabLeft = tabEl.offsetLeft
  const tabRight = tabLeft + tabEl.offsetWidth
  const viewLeft = track.scrollLeft
  const viewRight = viewLeft + track.clientWidth

  if (tabLeft < viewLeft + padding) {
    track.scrollTo({ left: Math.max(0, tabLeft - padding), behavior })
    return
  }

  if (tabRight > viewRight - padding) {
    track.scrollTo({ left: tabRight - track.clientWidth + padding, behavior })
  }
}

function activateTab(tabId: string, closePanel = false) {
  tabsStore.activeTabId = tabId

  if (closePanel) {
    panelVisible.value = false
  }
}

function closeTab(tabId: string) {
  tabsStore.closeTab(tabId)
}

function closeOtherTabs(tabId: string) {
  tabsStore.closeOtherTabs(tabId)
}

function closeAllTabs() {
  tabsStore.closeAllTabs()
  panelVisible.value = false
}

function newEditor() {
  tabsStore.openEditorTab(connectionsStore.activeConnId ?? '')
}

onMounted(() => {
  nextTick(() => {
    if (activeTabId.value) {
      scrollTabIntoView(activeTabId.value, 'auto')
    }
    updateScrollState()
  })

  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => updateScrollState())

    if (trackRef.value) {
      resizeObserver.observe(trackRef.value)
      const inner = trackRef.value.firstElementChild
      if (inner instanceof HTMLElement) {
        resizeObserver.observe(inner)
      }
    }
  }

  window.addEventListener('resize', updateScrollState)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  window.removeEventListener('resize', updateScrollState)
})

watch(
  activeTabId,
  async (tabId) => {
    await nextTick()
    updateScrollState()
    if (tabId) {
      scrollTabIntoView(tabId)
    }
  },
  { flush: 'post' }
)

watch(
  () => tabs.value.map(tab => tab.id).join('|'),
  async () => {
    await nextTick()
    updateScrollState()
    if (activeTabId.value) {
      scrollTabIntoView(activeTabId.value)
    }
  },
  { flush: 'post' }
)
</script>

<style scoped>
.tab-bar {
  display: flex;
  align-items: stretch;
  height: 42px;
  padding: 0 10px;
  background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  border-bottom: 1px solid var(--border-muted);
  overflow: hidden;
  flex-shrink: 0;
}

.tab-scroll-control,
.tab-actions,
.tab-panel-zone {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.tab-scroll-control,
.tab-actions,
.tab-panel-zone {
  margin-left: 10px;
  padding-left: 10px;
  border-left: 1px solid var(--border-muted);
}

.tab-scroll-control:first-child {
  margin-left: 0;
  padding-left: 0;
  border-left: none;
}

.tab-actions {
  gap: 8px;
}

.chrome-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  border: 1px solid var(--border-muted);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.12s ease, background 0.12s ease, border-color 0.12s ease;
}

.chrome-btn:hover:not(:disabled),
.chrome-btn.active {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-color: var(--el-color-primary-light-5);
}

.chrome-btn:disabled {
  opacity: 0.45;
  cursor: default;
}

.chrome-btn:focus-visible,
.action-btn:focus-visible,
.tab-item:focus-visible,
.panel-action:focus-visible,
.row-action:focus-visible,
.row-close:focus-visible {
  outline: 2px solid var(--glow-blue);
  outline-offset: 1px;
}

.tab-track-shell {
  flex: 1;
  min-width: 0;
  display: flex;
}

.tab-track {
  flex: 1;
  display: flex;
  justify-content: flex-start;
  min-width: 0;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
}

.tab-track::-webkit-scrollbar {
  display: none;
}

.tab-track-inner {
  display: flex;
  align-items: stretch;
  gap: 6px;
  min-width: max-content;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 30px;
  margin: 6px 0;
  padding: 0 12px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  white-space: nowrap;
  user-select: none;
  font-size: 12.5px;
  font-weight: 500;
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

.tab-icon {
  opacity: 0.7;
  flex-shrink: 0;
}

.tab-item.active .tab-icon,
.tab-list-row.active .tab-icon {
  opacity: 1;
}

.tab-title {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-btn {
  opacity: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 4px;
  padding: 2px;
  border-radius: 3px;
  color: var(--text-muted);
  transition: opacity 0.1s ease, background 0.1s ease, color 0.1s ease;
}

.tab-item:hover .close-btn,
.tab-item.active .close-btn {
  opacity: 0.7;
}

.close-btn:hover {
  opacity: 1 !important;
  background: rgba(248, 81, 73, 0.15);
  color: var(--accent-red);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 30px;
  padding: 0 10px;
  border: 1px solid var(--border-muted);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-muted);
  cursor: pointer;
  text-decoration: none;
  transition: color 0.12s ease, background 0.12s ease, border-color 0.12s ease;
}

.action-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-color: var(--el-color-primary-light-5);
}

.btn-label {
  margin-left: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.tab-list-btn {
  gap: 4px;
  width: auto;
  padding: 0 10px;
}

.tab-count {
  min-width: 16px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--bg-tertiary);
  font-size: 10px;
  font-weight: 600;
  line-height: 16px;
  text-align: center;
}

.tab-list-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tab-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.tab-list-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.tab-list-subtitle {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
}

.panel-action {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: color 0.12s ease;
}

.panel-action:hover:not(:disabled),
.row-action:hover {
  color: var(--text-primary);
}

.panel-action:disabled {
  opacity: 0.45;
  cursor: default;
}

.tab-list-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.tab-list-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.12s ease, color 0.12s ease;
}

.tab-list-row:hover {
  background: var(--bg-tertiary);
}

.tab-list-row.active {
  background: rgba(64, 158, 255, 0.12);
  color: var(--text-primary);
}

.tab-list-label {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12.5px;
  font-weight: 500;
}

.row-action,
.row-close {
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.12s ease, opacity 0.12s ease, background 0.12s ease;
}

.row-action {
  opacity: 0;
  font-size: 11px;
  white-space: nowrap;
}

.row-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border-radius: 6px;
}

.tab-list-row:hover .row-action,
.tab-list-row:hover .row-close,
.tab-list-row.active .row-action,
.tab-list-row.active .row-close {
  opacity: 0.8;
}

.row-close:hover {
  opacity: 1 !important;
  background: rgba(248, 81, 73, 0.15);
  color: var(--accent-red);
}

.tab-list-empty {
  padding: 18px 12px;
  border-radius: 10px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  text-align: center;
  font-size: 12px;
}
</style>

<style>
.tab-list-popover {
  padding: 12px !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: 14px !important;
  background: var(--bg-primary) !important;
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.22) !important;
}
</style>
