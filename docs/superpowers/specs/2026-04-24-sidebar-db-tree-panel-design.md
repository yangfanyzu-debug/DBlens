# Sidebar 数据库树折叠面板设计

## 背景

当前 Sidebar 中 ConnectionTree（连接列表）和 DbTree（数据库表树）之间缺少视觉分隔，展开数据库表时两块内容紧贴在一起，层次不清。

## 设计方案

### 方案 B：折叠面板

在 ConnectionTree 和 DbTree 之间增加视觉分隔，通过折叠面板组织 DbTree。

### 具体设计

**结构：**
- DbTree 包裹在折叠面板中，面板标题为当前连接名称
- 面板默认折叠，展开时懒加载数据库表树
- 面板右侧显示展开/折叠箭头图标

**标题样式：**
- 显示当前选中连接的名称（从 `useConnectionsStore` 获取）
- 小标签显示 "已连接" 状态指示
- 点击整个标题栏均可触发展开/折叠

**折叠状态：**
- 收起时只显示标题栏（约 40px 高）
- 展开时显示完整的 el-tree 表结构

**连接切换行为：**
- 切换连接后，面板自动折叠
- 新连接的数据库懒加载推迟到用户手动展开

### 文件改动

- `frontend/src/components/layout/Sidebar.vue` — 添加折叠面板结构
- `frontend/src/components/browser/DbTree.vue` — 保持现有逻辑，仅外层包裹变化

### 视觉风格

- 标题背景：`var(--bg-tertiary)`
- 标题文字：`var(--text-secondary)`
- 展开图标：Element Plus `CaretTop` / `CaretBottom`
- 面板边框分隔：与 ConnectionTree 之间用 1px `var(--border-muted)` 线

### 状态

- `[ ]` 待实现
