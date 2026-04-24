# Sidebar DbTree Collapsible Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap DbTree in a collapsible panel with connection name header, visually separating it from ConnectionTree above.

**Architecture:** Single-file change in Sidebar.vue. Custom collapsible panel (no extra library dependency) using a boolean ref and conditional rendering. A `watch` on `activeConnId` resets the panel to collapsed state when the user switches connections.

**Tech Stack:** Vue 3 Composition API, Element Plus icons, CSS custom properties.

---

## File Map

- Modify: `frontend/src/components/layout/Sidebar.vue`
  - Add `dbPanelOpen` ref and `watch` on `activeConnId`
  - Replace bare `<DbTree>` with collapsible panel markup
  - Add `.db-panel`, `.db-panel-header`, `.db-panel-body` CSS classes

---

### Task 1: Add collapsible panel to Sidebar.vue

**Files:**
- Modify: `frontend/src/components/layout/Sidebar.vue`

- [ ] **Step 1: Add imports and state**

Find the `<script setup lang="ts">` block (line 34) and add `watch` to the import from 'vue'. Add a `ref(false)` for `dbPanelOpen`.

```typescript
import { ref, watch } from 'vue'
```

```typescript
const dbPanelOpen = ref(false)
```

- [ ] **Step 2: Add watcher to reset panel on connection change**

After the `onOpenDbTree` function (around line 48), add:

```typescript
watch(activeConnId, () => {
  dbPanelOpen.value = false
})
```

- [ ] **Step 3: Replace DbTree with collapsible panel markup**

Replace line 28:
```html
      <DbTree v-if="activeConnId" :key="activeConnId" :conn-id="activeConnId" />
```

With:
```html
      <!-- 数据库表树折叠面板 -->
      <div v-if="activeConnId" class="db-panel">
        <div class="db-panel-header" @click="dbPanelOpen = !dbPanelOpen">
          <el-icon class="db-panel-caret" :class="{ open: dbPanelOpen }">
            <CaretBottom />
          </el-icon>
          <span class="db-panel-title">{{ connections.find(c => c.id === activeConnId)?.name }}</span>
          <el-tag size="small" class="db-panel-status">已连接</el-tag>
        </div>
        <div v-show="dbPanelOpen" class="db-panel-body">
          <DbTree :key="activeConnId" :conn-id="activeConnId" />
        </div>
      </div>
```

- [ ] **Step 4: Add imports for icons**

Update the imports from `@element-plus/icons-vue` to include `CaretBottom`:

```typescript
import { Plus, CaretBottom } from '@element-plus/icons-vue'
```

- [ ] **Step 5: Add CSS for the collapsible panel**

Add after the `.section-label` block (after line 139):

```css
/* 数据库表树折叠面板 */
.db-panel {
  margin-top: 16px;
}

.db-panel-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  cursor: pointer;
  border-top: 1px solid var(--border-muted);
  border-bottom: 1px solid var(--border-muted);
  user-select: none;
  transition: background 0.12s ease;
}
.db-panel-header:hover {
  background: var(--shell-hover);
}

.db-panel-caret {
  font-size: 10px;
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}
.db-panel-caret.open {
  transform: rotate(180deg);
}

.db-panel-title {
  flex: 1;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.db-panel-status {
  font-size: 10px;
  background: var(--accent-green);
  color: #fff;
  border: none;
  flex-shrink: 0;
}

.db-panel-body {
  /* tree content area */
}
```

- [ ] **Step 6: Verify in browser**

Refresh the page. Connect to a database. The "已连接" panel should appear below the connection list. Click the header to expand/collapse the table tree. Switch connections — panel should collapse automatically.

---

### Task 2: Commit

- [ ] **Commit the changes**

```bash
git add frontend/src/components/layout/Sidebar.vue
git commit -m "feat: wrap DbTree in collapsible panel with connection header

- Add collapsible panel showing connection name and '已连接' badge
- Panel collapses when switching connections
- Visual separator between ConnectionTree and table tree

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Spec Coverage Check

| Spec requirement | Task step |
|------------------|-----------|
| 折叠面板包裹 DbTree | Step 3 |
| 面板标题为当前连接名称 | Step 3 |
| "已连接"状态标签 | Step 3 |
| 默认折叠 | `dbPanelOpen = ref(false)` |
| 点击展开/折叠 | Step 3 `@click="dbPanelOpen = !dbPanelOpen"` |
| 切换连接自动折叠 | Step 2 watch |
| 1px 分隔线 | `.db-panel-header` border-top + border-bottom |
| 展开时懒加载表结构 | `v-show` keeps tree alive; el-tree lazy load unchanged |
