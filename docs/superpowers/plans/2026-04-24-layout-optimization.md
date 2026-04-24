# DBLens 布局优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实施 Sidebar、编辑器、DataGrid、主布局四处视觉/CSS 优化

**Architecture:** 纯 CSS/模板改动，不涉及 JS 逻辑变更，无测试覆盖，按文件分解任务

**Tech Stack:** Vue 3 (SFC), Element Plus, CSS custom properties (dark/light theme)

---

## 文件变更总览

| 任务 | 文件 | 改动类型 |
|---|---|---|
| 1 | `frontend/src/components/connection/ConnectionTree.vue` | CSS 微调 |
| 2 | `frontend/src/components/browser/DbTree.vue` | CSS 微调 |
| 3 | `frontend/src/components/editor/EditorToolbar.vue` | CSS 阴影 |
| 4 | `frontend/src/components/editor/EditorTab.vue` | CSS 分隔条 |
| 5 | `frontend/src/components/table/DataGrid.vue` | CSS + 模板 |
| 6 | `frontend/src/components/layout/AppLayout.vue` | CSS + 拖动逻辑 |

---

## Task 1: ConnectionTree 行高微调

**文件:** `frontend/src/components/connection/ConnectionTree.vue`

- [ ] **Step 1: 修改连接项行高**

编辑 `.conn-item` 样式，将行高从隐式 26px 增至 28px：

```css
.conn-item {
  /* ... existing properties ... */
  padding: 7px 14px 7px 20px;  /* 6px → 7px 垂直 padding */
  min-height: 28px;
}
```

- [ ] **Step 2: 增加组间间距**

在 `.group` 容器下增加下边距：

```css
.group {
  margin-bottom: 8px;
}
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/connection/ConnectionTree.vue
git commit -m "style: ConnectionTree row height micro-adjustments"
```

---

## Task 2: DbTree 节点高度调整

**文件:** `frontend/src/components/browser/DbTree.vue`

- [ ] **Step 1: 调整节点高度**

编辑 `:deep(.el-tree-node__content)` 样式：

```css
:deep(.el-tree-node__content) {
  height: 28px;  /* 26px → 28px */
  /* ... existing properties ... */
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/components/browser/DbTree.vue
git commit -m "style: DbTree node height alignment with ConnectionTree"
```

---

## Task 3: EditorToolbar 底部阴影

**文件:** `frontend/src/components/editor/EditorToolbar.vue`

- [ ] **Step 1: 给工具栏加底部阴影**

在 `.editor-toolbar` 中添加 `box-shadow`：

```css
.editor-toolbar {
  /* ... existing properties ... */
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/components/editor/EditorToolbar.vue
git commit -m "style: EditorToolbar bottom shadow for visual separation"
```

---

## Task 4: EditorTab 分隔条加宽

**文件:** `frontend/src/components/editor/EditorTab.vue`

- [ ] **Step 1: 分隔条加宽并增强 hover 效果**

```css
.resize-handle {
  height: 10px;  /* 6px → 10px */
  background: var(--el-border-color);
  cursor: row-resize;
  flex-shrink: 0;
  transition: background-color 0.15s ease;
}
.resize-handle:hover {
  background: var(--accent-blue);  /* 加深 hover 色 */
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/components/editor/EditorTab.vue
git commit -m "style: EditorTab resize handle wider and more visible"
```

---

## Task 5: DataGrid 工具栏分组 + 分页 + 表格样式

**文件:** `frontend/src/components/table/DataGrid.vue`

- [ ] **Step 1: 工具栏按钮分组（模板改动）**

将工具栏按钮分为三组，加竖线分隔：

```html
<div class="toolbar">
  <!-- 第一组 -->
  <el-button size="small" @click="loadData">刷新</el-button>
  <el-button size="small" type="primary" @click="addRow">+ 新增行</el-button>

  <span class="toolbar-sep" />

  <!-- 第二组 -->
  <el-button size="small" type="danger" :disabled="!selectedRows.length" @click="deleteRows">删除选中</el-button>
  <el-button size="small" type="success" :disabled="!pendingChanges.length" @click="showPreview">提交变更</el-button>

  <span class="toolbar-sep" />

  <!-- 第三组 -->
  <el-button size="small" @click="showExport = true">导出</el-button>

  <span class="total-info">共 {{ total }} 条</span>
</div>
```

对应的 CSS：

```css
.toolbar-sep {
  width: 1px;
  height: 18px;
  background: var(--el-border-color);
  margin: 0 4px;
}
.total-info {
  margin-left: auto;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-regular);
}
```

- [ ] **Step 2: 分页器优化 — 总条数移至左侧同行**

```html
<div class="pagination">
  <span class="total-label">共 {{ total }} 条</span>
  <el-pagination
    v-model:current-page="page"
    v-model:page-size="pageSize"
    :total="total"
    :page-sizes="[50, 100, 200, 500]"
    layout="sizes, prev, pager, next"
    small
    @change="loadData"
  />
</div>
```

```css
.total-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-right: 12px;
  align-self: center;
}
.pagination {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-top: 1px solid var(--el-border-color);
  flex-shrink: 0;
}
```

- [ ] **Step 3: 表格视觉优化**

```css
/* 表头加粗 + 背景 */
:deep(.el-table__header-wrapper th) {
  font-weight: 600;
  background: var(--bg-tertiary) !important;
}

/* 单元格内边距 */
:deep(.el-table td .cell) {
  padding: 4px 8px;
}

/* 修改单元格高亮（浅色主题） */
.cell-modified {
  background: #fef3c7;
  border-radius: 2px;
  padding: 0 2px;
}

/* 修改单元格高亮（暗色主题）用 CSS 变量 */
.theme-dark .cell-modified {
  background: #854d0e33;
}
```

**注意:** 当前模板中 `.cell-content` 包裹了双击编辑区域，实际高亮 span 需要应用 `cell-modified` class。由于 `.cell-modified` 直接加在 span 上，需确保样式优先级足够。用 `:deep(.cell-modified)` 覆盖。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/table/DataGrid.vue
git commit -m "style: DataGrid toolbar grouping, pagination and table visual polish"
```

---

## Task 6: AppLayout 可拖动侧边栏

**文件:** `frontend/src/components/layout/AppLayout.vue`

- [ ] **Step 1: 添加 drag handle HTML**

在 `.sidebar` 内添加拖动条：

```html
<aside class="sidebar" :style="{ width: sidebarWidth + 'px' }">
  <Sidebar />
  <div class="drag-handle" @mousedown="startResize" />
</aside>
```

- [ ] **Step 2: 添加 resize 逻辑 script**

```typescript
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
```

- [ ] **Step 3: 添加 drag handle CSS**

```css
.drag-handle {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  cursor: col-resize;
  background: transparent;
  transition: background-color 0.15s ease;
  z-index: 10;
}
.drag-handle:hover {
  background: var(--accent-blue);
}
.sidebar {
  position: relative;
  /* 移除原有的 width/min-width/max-width，改由 JS 控制 */
  width: 260px;
  min-width: 220px;
  max-width: 400px;
}
```

**注意:** 由于 `sidebarWidth` 是响应式的 `ref`，模板中已有 `:style="{ width: sidebarWidth + 'px' }"` 绑定，CSS 中的 width 配合 `!important` 或内联样式生效。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/layout/AppLayout.vue
git commit -m "feat: AppLayout resizable sidebar with drag handle and localStorage persistence"
```

---

## Task 7: 全局验证

- [ ] **Step 1: 验证深色/浅色主题切换正常**
- [ ] **Step 2: 验证侧边栏拖动在 min/max 范围内约束**
- [ ] **Step 3: 验证 DataGrid 列数多时横向滚动正常**
- [ ] **Step 4: 验证修改单元格高亮在两种主题下清晰可见**
- [ ] **Step 5: 一次性提交所有剩余改动并 push**

```bash
git status
git diff --stat
# 确认无意外文件
git push
```

---

## 自检清单

- [ ] spec 覆盖检查：Area A/B/C/D 每项改动均有对应 Task
- [ ] 占位符扫描：无 TBD/TODO/不完整描述
- [ ] 类型一致性：sidebarWidth ref → template `:style` 绑定 → localStorage 读写，逻辑闭环
- [ ] 6 个 Task 均有独立 commit message，commit 粒度合理
