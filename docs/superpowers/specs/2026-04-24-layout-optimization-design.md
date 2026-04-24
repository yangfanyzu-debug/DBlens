# DBLens M1 布局优化设计

**日期**: 2026-04-24
**范围**: Sidebar、编辑器区域、表格/数据网格、主布局

---

## 1. 目标

在不改变现有交互逻辑的前提下，通过视觉和布局微调提升 DBLens 的精致度和可用性。

---

## 2. Area A — Sidebar 布局优化

**选择**: A — 保持堆叠结构 + 微调

### 改动点

| 位置 | 现状 | 改动 |
|---|---|---|
| ConnectionTree 分组标题 | padding: 5px 14px, 字号 11px | 保持，增加组间间距 |
| ConnectionTree 连接项 | padding: 6px 14px 6px 20px | 行高从 26px 增至 28px |
| DbTree 节点 | 节点高度 26px | 增至 28px，与连接项对齐 |
| 整体留白 | 较紧凑 | sidebar-body padding 适当增加 |

### 文件
- `frontend/src/components/connection/ConnectionTree.vue`
- `frontend/src/components/browser/DbTree.vue`

---

## 3. Area B — 编辑器区域布局优化

**选择**: D — 工具栏加底部阴影 + 加宽分隔条

### 改动点

| 位置 | 现状 | 改动 |
|---|---|---|
| EditorToolbar | 底部无分隔 | `box-shadow: 0 1px 4px rgba(0,0,0,0.15)` |
| resize-handle | height: 6px | 增至 10px |
| resize-handle hover | `var(--el-color-primary-light-7)` | 颜色加深，更醒目 |

### 文件
- `frontend/src/components/editor/EditorToolbar.vue`
- `frontend/src/components/editor/EditorTab.vue`

---

## 4. Area C — 表格/数据网格优化

**选择**: D — 全部三个方面

### 4.1 工具栏按钮分组

- 按钮分为三组：**[刷新] [+ 新增] | [删除选中] [提交变更] | [导出]**，组间用 1px 竖线分隔
- 总计信息（"共 N 条"）右对齐，字体加粗

### 4.2 分页器优化

- 当前页码按钮加深背景色（accent-blue）
- 总条数信息移至分页器左侧，与分页控件同行

### 4.3 表格视觉

- 列宽策略：`min-width` 保持，列数超过 10 时允许横向滚动
- 单元格内边距：`padding: 4px 8px`
- 修改单元格高亮：`cell-modified` 背景从 `#fffbe6` 改为更醒目的黄色 `#fef3c7`（浅色主题）/ `#854d0e33`（暗色主题）
- 表头：`font-weight: 600`，背景 `var(--bg-tertiary)`

### 文件
- `frontend/src/components/table/DataGrid.vue`

---

## 5. Area D — 主布局优化

**选择**: A — 侧边栏宽度可拖动调整

### 改动点

- AppLayout 侧边栏右侧增加 4px 宽的 drag handle（垂直虚线，hover 时高亮）
- 拖动改变 sidebar width（在 min: 220px / max: 400px 约束内）
- 添加 `user-select: none` 防止拖动时选中文本
- 保存宽度到 `localStorage`，刷新后恢复

### 文件
- `frontend/src/components/layout/AppLayout.vue`

---

## 6. 改动量估算

| 文件 | 改动量 |
|---|---|
| `ConnectionTree.vue` | ~10 行 CSS |
| `DbTree.vue` | ~5 行 CSS |
| `EditorToolbar.vue` | ~2 行 CSS |
| `EditorTab.vue` | ~3 行 CSS |
| `DataGrid.vue` | ~25 行 CSS + 少量模板调整 |
| `AppLayout.vue` | ~40 行（drag handle + resize 逻辑） |

---

## 7. 测试要点

- [ ] 深色/浅色主题下各改动均正常显示
- [ ] 侧边栏拖动后宽度在 min/max 范围内约束
- [ ] DataGrid 列数多时横向滚动正常
- [ ] 修改单元格高亮在两种主题下均清晰可见
