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
        <div class="empty-panel">
          <div class="empty-badge">工作区</div>
          <div class="empty-graphic">
            <svg width="72" height="72" viewBox="0 0 24 24" fill="none">
              <ellipse cx="12" cy="5" rx="8" ry="2.5" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.38" />
              <path d="M4 5v5c0 1.38 3.58 2.5 8 2.5s8-1.12 8-2.5V5" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.38" />
              <path d="M4 10v5c0 1.38 3.58 2.5 8 2.5s8-1.12 8-2.5v-5" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.18" />
            </svg>
          </div>
          <div class="empty-copy">
            <p class="empty-title">从连接开始，打开你的数据工作区</p>
            <p class="empty-hint">左侧选择一个数据库连接后，可以浏览表结构，或在上方新建 SQL 编辑页继续工作。</p>
          </div>
          <div class="empty-steps">
            <div class="step-item">
              <span class="step-index">1</span>
              <span class="step-text">在左侧连接区选择一个数据库</span>
            </div>
            <div class="step-item">
              <span class="step-index">2</span>
              <span class="step-text">打开数据表或点击右上角新建编辑器</span>
            </div>
          </div>
        </div>
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
  background:
    radial-gradient(circle at top, var(--glow-blue) 0%, transparent 45%),
    var(--bg-primary);
}

.tab-pane {
  height: 100%;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 32px;
}

.empty-panel {
  width: min(560px, 100%);
  padding: 28px 30px;
  border: 1px solid var(--border-default);
  border-radius: 20px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12);
}

.empty-badge {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-blue);
  background: var(--glow-blue);
  border: 1px solid rgba(9, 105, 218, 0.18);
}

.empty-graphic {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 88px;
  height: 88px;
  margin: 18px 0 16px;
  border-radius: 22px;
  color: var(--accent-blue);
  background: var(--bg-tertiary);
  border: 1px solid rgba(9, 105, 218, 0.16);
}

.empty-copy {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 18px;
}

.empty-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  line-height: 1.35;
  color: var(--text-primary);
}

.empty-hint {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.empty-steps {
  display: grid;
  gap: 10px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 48px;
  padding: 0 14px;
  border-radius: 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-muted);
}

.step-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 999px;
  background: var(--glow-blue);
  color: var(--accent-blue);
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.step-text {
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
