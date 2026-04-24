# Frontend Workbench Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish the DBLens front-end shell so the sidebar, tab workspace, and empty state feel more refined without changing workflow or business logic.

**Architecture:** This is a presentation-only pass across the existing Vue shell. The implementation stays inside current layout components and the shared theme stylesheet, using the repo's existing CSS-variable approach so both light and dark themes stay aligned.

**Tech Stack:** Vue 3 SFCs, TypeScript, Pinia, Element Plus, Vite, CSS custom properties

---

## File Map

- Modify: `frontend/src/style.css`
  - Shared theme tokens, shell surface variables, button polish, and app-wide interaction rhythm
- Modify: `frontend/src/components/layout/AppLayout.vue`
  - Outer shell layering, sidebar framing, and resize-handle visual refinement
- Modify: `frontend/src/components/layout/Sidebar.vue`
  - Sidebar header hierarchy, primary action styling, and navigation-region spacing
- Modify: `frontend/src/components/common/TabBar.vue`
  - Tab strip surface treatment and action cluster polish
- Modify: `frontend/src/components/layout/MainArea.vue`
  - Workspace background treatment and upgraded empty state

## Task 1: Refine Global Theme Tokens

**Files:**
- Modify: `frontend/src/style.css`

- [ ] **Step 1: Update the shared shell tokens**

Add a small set of shell-specific variables near the existing root theme tokens:

```css
:root {
  --surface-shell: #f3f6f9;
  --surface-panel: #ffffff;
  --surface-panel-muted: #f6f8fa;
  --surface-hover: rgba(9, 105, 218, 0.06);
  --shadow-soft: 0 10px 30px rgba(15, 23, 42, 0.06);
  --shadow-panel: 0 6px 18px rgba(15, 23, 42, 0.08);
}

.theme-dark {
  --surface-shell: #0f141b;
  --surface-panel: #161b22;
  --surface-panel-muted: #1c2128;
  --surface-hover: rgba(88, 166, 255, 0.08);
  --shadow-soft: 0 14px 30px rgba(0, 0, 0, 0.22);
  --shadow-panel: 0 8px 24px rgba(0, 0, 0, 0.28);
}
```

- [ ] **Step 2: Apply the new tokens to the app-wide shell**

Replace the current page background usage with the shell tokens and keep the viewport behavior intact:

```css
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
  font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--surface-shell);
  color: var(--text-primary);
}

#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: var(--surface-shell);
}
```

- [ ] **Step 3: Tighten shared control polish without changing behavior**

Extend the existing button rules so the UI feels more consistent:

```css
.el-button {
  font-family: 'IBM Plex Sans', sans-serif;
  font-weight: 500;
  border-radius: var(--radius-md);
  border-color: var(--border-default);
  background: var(--surface-panel);
  transition: background-color 200ms ease, color 200ms ease, border-color 200ms ease, transform 200ms ease, box-shadow 200ms ease;
}

.el-button:hover {
  border-color: var(--accent-blue);
}

.el-button--primary {
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.06) inset;
}
```

- [ ] **Step 4: Verify the stylesheet still builds**

Run: `npm run build`

Expected: Vite build completes successfully with no CSS parse errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/style.css
git commit -m "style: refine shared shell theme tokens"
```

## Task 2: Polish the App Shell Framing

**Files:**
- Modify: `frontend/src/components/layout/AppLayout.vue`

- [ ] **Step 1: Refine the outer shell container styles**

Update the shell styles so the main frame uses softer layering and less aggressive shadow:

```css
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, var(--surface-hover), transparent 32%),
    var(--surface-shell);
}

.sidebar {
  position: relative;
  background: var(--surface-panel-muted);
  border-right: 1px solid var(--border-default);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.04);
  flex-shrink: 0;
}

.main-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--surface-shell);
}
```

- [ ] **Step 2: Make the resize handle easier to discover**

Adjust only the presentation of the existing resize affordance:

```css
.drag-handle {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: col-resize;
  background: linear-gradient(180deg, transparent 0%, var(--surface-hover) 50%, transparent 100%);
  opacity: 0;
  transition: opacity 0.15s ease, background-color 0.15s ease;
  z-index: 10;
}

.sidebar:hover .drag-handle,
.drag-handle:hover {
  opacity: 1;
}
```

- [ ] **Step 3: Verify layout behavior still works**

Run: `npm run build`

Expected: PASS. The component compiles without template or style errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/layout/AppLayout.vue
git commit -m "style: polish app shell framing"
```

## Task 3: Refine Sidebar Hierarchy

**Files:**
- Modify: `frontend/src/components/layout/Sidebar.vue`

- [ ] **Step 1: Restructure the sidebar header markup for stronger hierarchy**

Replace the current header block with a title cluster and lighter action placement:

```vue
<div class="sidebar-header">
  <div class="brand-block">
    <div class="logo-mark">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <ellipse cx="12" cy="6" rx="9" ry="3" stroke="#58a6ff" stroke-width="1.5" />
        <path d="M3 6v6c0 1.66 4.03 3 9 3s9-1.34 9-3V6" stroke="#58a6ff" stroke-width="1.5" />
        <path d="M3 12v6c0 1.66 4.03 3 9 3s9-1.34 9-3v-6" stroke="#58a6ff" stroke-width="1.5" stroke-opacity="0.5" />
      </svg>
    </div>
    <div class="brand-copy">
      <span class="eyebrow">Workspace</span>
      <span class="title">DBLens</span>
    </div>
  </div>
  <el-button size="small" type="primary" @click="showForm = true" class="new-btn">
    <Plus style="width:14px;height:14px" />
    新建
  </el-button>
</div>
```

- [ ] **Step 2: Add shell-aligned sidebar styles**

Replace the current sidebar-scoped styles with a more structured version:

```css
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--surface-panel-muted);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 18px 14px;
  border-bottom: 1px solid var(--border-default);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.06) 0%, transparent 100%),
    var(--surface-panel-muted);
  flex-shrink: 0;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.eyebrow {
  font-size: 11px;
  line-height: 1;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.title {
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.02em;
  color: var(--text-primary);
}

.logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: var(--glow-blue);
  border: 1px solid color-mix(in srgb, var(--accent-blue) 24%, transparent);
  box-shadow: var(--shadow-soft);
  flex-shrink: 0;
}

.new-btn {
  gap: 4px;
  padding-inline: 12px;
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px 0 18px;
}
```

- [ ] **Step 3: Verify the sidebar still renders**

Run: `npm run build`

Expected: PASS. Vue compiles the updated template and scoped styles cleanly.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/layout/Sidebar.vue
git commit -m "style: refine sidebar header hierarchy"
```

## Task 4: Tighten the Tab Workspace Surface

**Files:**
- Modify: `frontend/src/components/common/TabBar.vue`

- [ ] **Step 1: Upgrade the tab strip background and spacing**

Update the tab bar styles so the strip reads as part of the same workbench system:

```css
.tab-bar {
  display: flex;
  align-items: stretch;
  height: 42px;
  background: color-mix(in srgb, var(--surface-panel) 86%, var(--surface-shell));
  border-bottom: 1px solid var(--border-default);
  box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.03);
  overflow: hidden;
  flex-shrink: 0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-muted);
  border-right: 1px solid var(--border-muted);
  border-bottom: 2px solid transparent;
  white-space: nowrap;
  user-select: none;
  transition: color 0.12s ease, background-color 0.12s ease, border-color 0.12s ease;
  position: relative;
}

.tab-item:hover {
  color: var(--text-secondary);
  background: var(--surface-hover);
}

.tab-item.active {
  color: var(--text-primary);
  background: var(--surface-panel);
  border-bottom-color: var(--accent-blue);
}
```

- [ ] **Step 2: Refine the tab action cluster**

Use lighter action styling so utility buttons do not overpower the tabs:

```css
.tab-actions {
  display: flex;
  align-items: center;
  padding: 0 10px;
  border-left: 1px solid var(--border-muted);
  background: color-mix(in srgb, var(--surface-panel-muted) 80%, transparent);
  flex-shrink: 0;
  gap: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  border-radius: 8px;
  transition: all 0.12s ease;
}

.action-btn:hover {
  background: var(--surface-hover);
  border-color: var(--border-default);
  color: var(--accent-blue);
}
```

- [ ] **Step 3: Verify the tab bar still compiles**

Run: `npm run build`

Expected: PASS. No template or style regression.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/common/TabBar.vue
git commit -m "style: polish tab workspace surface"
```

## Task 5: Upgrade the Main Empty State

**Files:**
- Modify: `frontend/src/components/layout/MainArea.vue`

- [ ] **Step 1: Replace the minimal placeholder markup with a guided empty state**

Update the empty state block to include a surface, clearer text, and lightweight next steps:

```vue
<div v-if="!tabs.length" class="empty-state">
  <div class="empty-panel">
    <div class="empty-graphic">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
        <ellipse cx="12" cy="5" rx="8" ry="2.5" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.4" />
        <path d="M4 5v5c0 1.38 3.58 2.5 8 2.5s8-1.12 8-2.5V5" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.4" />
        <path d="M4 10v5c0 1.38 3.58 2.5 8 2.5s8-1.12 8-2.5v-5" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.2" />
      </svg>
    </div>
    <p class="empty-eyebrow">Workspace ready</p>
    <h2 class="empty-title">从左侧选择连接，开始浏览数据库</h2>
    <p class="empty-hint">打开一个连接后，你可以查看结构、预览数据，或者新建 SQL 编辑器继续工作。</p>
    <ul class="empty-actions">
      <li>在左侧连接列表中选择一个数据库连接</li>
      <li>使用右上角的 “+” 新建 SQL 编辑器标签页</li>
    </ul>
  </div>
</div>
```

- [ ] **Step 2: Add the corresponding empty-state styles**

Replace the current empty-state styles with a surface-based layout:

```css
.main-area-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--surface-shell);
}

.tab-content {
  flex: 1;
  overflow: hidden;
  position: relative;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0%, transparent 22%),
    var(--surface-shell);
}

.empty-state {
  display: grid;
  place-items: center;
  height: 100%;
  padding: 32px;
}

.empty-panel {
  max-width: 560px;
  padding: 32px 36px;
  border: 1px solid var(--border-default);
  border-radius: 20px;
  background: color-mix(in srgb, var(--surface-panel) 94%, transparent);
  box-shadow: var(--shadow-panel);
}

.empty-eyebrow {
  margin: 0 0 10px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-blue);
}

.empty-title {
  margin: 0 0 12px;
  font-size: 28px;
  line-height: 1.2;
  color: var(--text-primary);
}

.empty-hint {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.empty-actions {
  margin: 18px 0 0;
  padding-left: 18px;
  color: var(--text-secondary);
}
```

- [ ] **Step 3: Verify the workspace view still builds**

Run: `npm run build`

Expected: PASS. The new markup and styles compile without Vue SFC errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/layout/MainArea.vue
git commit -m "style: upgrade main workspace empty state"
```

## Task 6: Final Verification

**Files:**
- Verify only:
  - `frontend/src/style.css`
  - `frontend/src/components/layout/AppLayout.vue`
  - `frontend/src/components/layout/Sidebar.vue`
  - `frontend/src/components/common/TabBar.vue`
  - `frontend/src/components/layout/MainArea.vue`

- [ ] **Step 1: Run the production build**

Run: `npm run build`

Expected: PASS. Vite outputs the production bundle successfully.

- [ ] **Step 2: Review the final diff scope**

Run: `git diff -- frontend/src/style.css frontend/src/components/layout/AppLayout.vue frontend/src/components/layout/Sidebar.vue frontend/src/components/common/TabBar.vue frontend/src/components/layout/MainArea.vue`

Expected: The diff contains only shell/layout/visual changes. No store, API, or data-grid logic changes appear.

- [ ] **Step 3: Review changed files summary**

Run: `git diff --stat`

Expected: Only the planned shell/layout files and the plan/spec docs appear in this polish pass.

- [ ] **Step 4: Create the final implementation commit**

```bash
git add frontend/src/style.css frontend/src/components/layout/AppLayout.vue frontend/src/components/layout/Sidebar.vue frontend/src/components/common/TabBar.vue frontend/src/components/layout/MainArea.vue
git commit -m "style: polish frontend workbench shell"
```

## Self-Review

- Spec coverage:
  - App shell layering and resize affordance: Task 2
  - Sidebar product anchor and body rhythm: Task 3
  - Main workspace shell consistency: Tasks 4 and 5
  - Empty state guidance upgrade: Task 5
  - Light/dark verification and scope guardrails: Task 6
- Placeholder scan:
  - No `TBD`, `TODO`, or deferred implementation notes remain
  - Each task includes exact files, concrete code, and an explicit verification step
- Consistency check:
  - All tasks use the same shell variable names: `--surface-shell`, `--surface-panel`, `--surface-panel-muted`, `--surface-hover`, `--shadow-soft`, `--shadow-panel`
  - The implementation stays inside the five planned files throughout the document
