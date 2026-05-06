# Tabbar Overflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the DBLens tabbar so many open tabs remain easy to scan, navigate, and manage without changing the existing tab model.

**Architecture:** Keep the current Pinia tab store and main workbench structure. Implement the overflow experience primarily inside `frontend/src/components/common/TabBar.vue`, with only small store helpers if batch-close actions are needed. Use explicit left/right scroll controls plus a lightweight all-tabs panel instead of slicing tabs by estimated width.

**Tech Stack:** Vue 3 SFCs, TypeScript, Pinia, Element Plus, CSS

---

## File Map

- Modify: `frontend/src/components/common/TabBar.vue`
  - Rebuild the tabbar into left/center/right zones, add scroll controls, add the all-tabs panel, and keep tab interactions intact
- Modify: `frontend/src/stores/tabs.ts`
  - Add minimal helper methods for batch closing if needed by the tab list panel

## Task 1: Add Minimal Batch-Close Store Helpers

**Files:**
- Modify: `frontend/src/stores/tabs.ts`

- [ ] **Step 1: Add the failing store test script**

Create a quick one-off verification script first so the expected batch-close behavior is explicit:

```ts
import { createPinia, setActivePinia } from 'pinia'
import { useTabsStore } from './src/stores/tabs'

setActivePinia(createPinia())
const store = useTabsStore()

const a = store.openEditorTab('conn-a')
const b = store.openEditorTab('conn-a')
const c = store.openEditorTab('conn-a')

store.closeOtherTabs(b)
if (store.tabs.map(t => t.id).join(',') !== b) {
  throw new Error('closeOtherTabs should keep only the target tab')
}

store.openEditorTab('conn-a')
store.openEditorTab('conn-a')
store.closeAllTabs()
if (store.tabs.length !== 0 || store.activeTabId !== null) {
  throw new Error('closeAllTabs should clear all tabs and activeTabId')
}
```

- [ ] **Step 2: Run the script to verify it fails**

Run: `npx tsx temp-tab-store-check.ts`

Expected: FAIL because `closeOtherTabs` and `closeAllTabs` do not exist yet.

- [ ] **Step 3: Add the minimal store helpers**

Extend `frontend/src/stores/tabs.ts` with only the required methods:

```ts
function closeOtherTabs(id: string) {
  tabs.value = tabs.value.filter(t => t.id === id)
  activeTabId.value = tabs.value[0]?.id ?? null
}

function closeAllTabs() {
  tabs.value = []
  activeTabId.value = null
}
```

Return them from the store:

```ts
return {
  tabs,
  activeTabId,
  openEditorTab,
  openTableTab,
  closeTab,
  closeOtherTabs,
  closeAllTabs,
  renameTab,
}
```

- [ ] **Step 4: Run the script to verify it passes**

Run: `npx tsx temp-tab-store-check.ts`

Expected: PASS with no output.

- [ ] **Step 5: Remove the temp script**

Run: `Remove-Item temp-tab-store-check.ts`

Expected: The temporary verification file is deleted.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/stores/tabs.ts
git commit -m "feat: add tab batch close helpers"
```

## Task 2: Rebuild TabBar Layout for Overflow Navigation

**Files:**
- Modify: `frontend/src/components/common/TabBar.vue`

- [ ] **Step 1: Replace width-estimation logic with scroll-based state**

Remove the current `TAB_EST_WIDTH`, `ACTION_WIDTH`, `visibleTabs`, `overflowTabs`, and `overflowCount` approach. Replace it with scroll refs and computed button state:

```ts
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const tabsScrollRef = ref<HTMLElement | null>(null)
const listOpen = ref(false)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)

function updateScrollState() {
  const el = tabsScrollRef.value
  if (!el) return
  canScrollLeft.value = el.scrollLeft > 0
  canScrollRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 1
}

function scrollTabs(direction: 'left' | 'right') {
  const el = tabsScrollRef.value
  if (!el) return
  const delta = Math.max(220, Math.floor(el.clientWidth * 0.65))
  el.scrollBy({ left: direction === 'left' ? -delta : delta, behavior: 'smooth' })
}
```

- [ ] **Step 2: Add active-tab visibility syncing**

Add a helper so the selected tab is always brought back into view:

```ts
function ensureActiveTabVisible() {
  const el = tabsScrollRef.value
  const active = el?.querySelector<HTMLElement>('[data-active="true"]')
  if (!el || !active) return
  const activeLeft = active.offsetLeft
  const activeRight = activeLeft + active.offsetWidth
  const viewLeft = el.scrollLeft
  const viewRight = viewLeft + el.clientWidth

  if (activeLeft < viewLeft) {
    el.scrollTo({ left: activeLeft - 12, behavior: 'smooth' })
  } else if (activeRight > viewRight) {
    el.scrollTo({ left: activeRight - el.clientWidth + 12, behavior: 'smooth' })
  }
}

watch(() => tabs.value.map(t => t.id).join(','), async () => {
  await nextTick()
  updateScrollState()
  ensureActiveTabVisible()
})

watch(activeTabId, async () => {
  await nextTick()
  ensureActiveTabVisible()
})
```

- [ ] **Step 3: Replace the template with left/center/right zones**

Use this structure instead of the current overflow dropdown + estimated slicing:

```vue
<div class="tab-bar">
  <div class="tab-nav">
    <button class="nav-btn" :disabled="!canScrollLeft" @click="scrollTabs('left')">
      <el-icon :size="14"><ArrowLeft /></el-icon>
    </button>
    <button class="nav-btn" :disabled="!canScrollRight" @click="scrollTabs('right')">
      <el-icon :size="14"><ArrowRight /></el-icon>
    </button>
  </div>

  <div class="tabs-track" ref="tabsScrollRef" @scroll="updateScrollState">
    <div
      v-for="tab in tabs"
      :key="tab.id"
      class="tab-pill"
      :class="{ active: tab.id === activeTabId }"
      :data-active="tab.id === activeTabId"
      @click="tabsStore.activeTabId = tab.id"
    >
      <el-icon class="tab-icon" :size="13">
        <EditPen v-if="tab.type === 'editor'" />
        <Grid v-else />
      </el-icon>
      <span class="tab-title">{{ tab.title }}</span>
      <el-icon class="close-btn" :size="12" @click.stop="tabsStore.closeTab(tab.id)">
        <Close />
      </el-icon>
    </div>
  </div>

  <div class="tab-actions">
    <el-popover
      placement="bottom-end"
      :width="320"
      trigger="click"
      v-model:visible="listOpen"
      popper-class="tab-list-popover"
    >
      <template #reference>
        <button class="list-btn">
          <el-icon :size="14"><Operation /></el-icon>
          <span>列表</span>
        </button>
      </template>

      <div class="tab-list-panel">
        <div class="tab-list-header">
          <span>全部标签</span>
          <div class="tab-list-ops">
            <button class="text-btn" @click="activeTabId && tabsStore.closeOtherTabs(activeTabId)">关闭其他</button>
            <button class="text-btn danger" @click="tabsStore.closeAllTabs()">关闭全部</button>
          </div>
        </div>
        <div class="tab-list-body">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-list-item"
            :class="{ active: tab.id === activeTabId }"
            @click="tabsStore.activeTabId = tab.id; listOpen = false"
          >
            <el-icon class="tab-icon" :size="13">
              <EditPen v-if="tab.type === 'editor'" />
              <Grid v-else />
            </el-icon>
            <span class="tab-list-title">{{ tab.title }}</span>
            <el-icon class="close-btn" :size="12" @click.stop="tabsStore.closeTab(tab.id)">
              <Close />
            </el-icon>
          </button>
        </div>
      </div>
    </el-popover>
  </div>
</div>
```

- [ ] **Step 4: Update imports for the new controls**

Change imports to match the new UI:

```ts
import { ArrowLeft, ArrowRight, EditPen, Grid, Close, Operation } from '@element-plus/icons-vue'
```

Remove the current `Plus`, `QuestionFilled`, and `MoreFilled` imports because they are outside this feature scope.

- [ ] **Step 5: Replace the styles with the new pill-based layout**

Update the scoped CSS so the tabbar matches the approved design:

```css
.tab-bar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  height: 52px;
  padding: 0 14px;
  background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
}

.tab-nav {
  display: flex;
  gap: 6px;
}

.nav-btn,
.list-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 34px;
  min-width: 34px;
  padding: 0 12px;
  border: 1px solid var(--border-default);
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.tabs-track {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.tabs-track::-webkit-scrollbar {
  display: none;
}

.tab-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 34px;
  min-width: 0;
  max-width: 220px;
  padding: 0 14px;
  border: 1px solid transparent;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.55);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.tab-pill.active {
  background: var(--bg-primary);
  border-color: var(--el-color-primary-light-5);
  color: var(--text-primary);
  box-shadow: 0 4px 14px rgba(9, 105, 218, 0.08);
}

.tab-title,
.tab-list-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
}

.tab-list-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 320px;
  overflow: auto;
}

.tab-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 12px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.tab-list-item.active {
  background: var(--glow-blue);
  color: var(--accent-blue);
}
```

- [ ] **Step 6: Run the frontend build**

Run: `npm run build`

Expected: PASS. No Vue compilation or TypeScript errors from the rebuilt tabbar.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/common/TabBar.vue frontend/src/stores/tabs.ts
git commit -m "feat: improve tabbar overflow management"
```

## Task 3: Verify Few-Tab and Many-Tab States

**Files:**
- Verify only:
  - `frontend/src/components/common/TabBar.vue`
  - `frontend/src/stores/tabs.ts`

- [ ] **Step 1: Verify the base build again**

Run: `npm run build`

Expected: PASS. Production bundle builds successfully.

- [ ] **Step 2: Open the app locally**

Run: `npm run dev -- --host 0.0.0.0`

Expected: Vite dev server starts and prints a local URL such as `http://localhost:5173/`.

- [ ] **Step 3: Manual check for few tabs**

Verify these conditions in the browser:

```text
1. Open 1-3 tabs
2. Confirm tabs stay centered in the main track
3. Confirm nav buttons are present but disabled when no overflow exists
4. Confirm the list button opens the all-tabs panel
```

Expected: Layout looks clean and not overbuilt in the small-tab state.

- [ ] **Step 4: Manual check for many tabs**

Verify these conditions in the browser:

```text
1. Open 8+ tabs
2. Confirm left/right controls scroll by a meaningful chunk
3. Confirm selecting a hidden tab from the list brings it into view
4. Confirm active tab styling remains obvious
```

Expected: Many-tab state remains usable without awkward raw horizontal scrolling.

- [ ] **Step 5: Manual check for management actions**

Verify these conditions in the browser:

```text
1. Use the list panel to switch tabs
2. Close one tab from the panel
3. Use close others
4. Use close all
```

Expected: The panel stays in sync with the store and no broken active-tab state appears.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/common/TabBar.vue frontend/src/stores/tabs.ts
git commit -m "test: verify tabbar overflow interactions"
```

## Self-Review

- Spec coverage:
  - Three-zone tabbar layout: Task 2
  - Explicit overflow navigation controls: Task 2
  - All-tabs list panel: Task 2
  - Batch close actions: Tasks 1 and 2
  - Few-tab and many-tab verification: Task 3
- Placeholder scan:
  - No `TBD`, `TODO`, or deferred instructions remain
  - Each task contains exact files, concrete code, and explicit commands
- Consistency check:
  - The plan uses `closeOtherTabs` and `closeAllTabs` consistently
  - The implementation remains scoped to `TabBar.vue` and `tabs.ts`
