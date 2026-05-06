# DBLens Tabbar Overflow Design

**Date**: 2026-04-24
**Status**: Drafted for review
**Scope**: Multi-tab overflow handling and tabbar layout polish for the existing DBLens workbench

## 1. Goal

Improve the top tabbar so it remains usable and visually clear when many tabs are open.

This pass focuses on tab management and layout only:

- Make many tabs easier to scan and switch
- Improve the visual quality of the tabbar
- Add lightweight tab management affordances
- Keep the current tab model and overall page layout intact

This pass does not include:

- Changing the editor or table content model
- Rebuilding the page shell
- Introducing complex workspace concepts beyond the current tab system

## 2. Success Criteria

The work is successful when:

- The tabbar still feels organized when many tabs are open
- The active tab remains easy to identify
- Users can quickly navigate hidden tabs without awkward horizontal scrolling
- Users can open a compact list of all tabs and perform common close actions
- Existing open, switch, and close behavior continues to work

## 3. Visual Direction

### Visual thesis

The tabbar should feel like a calm, premium strip of working items: compact, pill-shaped, and deliberately managed rather than a crowded row of tiny file tabs.

### Layout thesis

The bar is split into three zones:

- left controls for horizontal tab navigation
- center tab track for visible tabs
- right-side management entry for the full tab list

### Interaction thesis

- Navigation controls should scroll by meaningful chunks, not tiny increments
- The active tab should auto-scroll into view when selected or opened
- The tab list panel should make overflow manageable without replacing the main tabbar

## 4. Design Decisions

### 4.1 Tabbar Structure

The tabbar becomes a three-part workbench control:

- Left: previous/next scroll buttons
- Center: horizontally scrollable track of visible tabs
- Right: a list button that opens the full-tab panel

Rationale:

This solves overflow without making the center track responsible for every management action.

### 4.2 Tab Visual Style

Tabs should move from plain strip items toward compact pills:

- rounded shape
- clearer active state
- lighter inactive state
- restrained icon and close affordance

The active tab should feel selected but not overly heavy.

Rationale:

When many tabs are visible, stronger item boundaries improve scanning more effectively than tighter spacing alone.

### 4.3 Overflow Navigation

The center track remains scrollable, but the primary way to move through overflow becomes explicit controls.

Behavior:

- left/right buttons scroll by one visible chunk
- opening or activating a tab should ensure it is visible in the track
- manual wheel/trackpad scrolling may still work, but is no longer the only method

Rationale:

Users should not need fine-grained horizontal scrolling to find hidden tabs.

### 4.4 Tab List Panel

The right-side list button opens a compact panel containing all tabs.

Panel content:

- each tab with icon, title, and active state
- single-tab close affordance
- common batch actions such as close others and close all

Optional action:

- close right may be included only if the current store can support it simply

Rationale:

This gives users a reliable overflow escape hatch without forcing the entire tab interaction into a secondary UI.

## 5. Component Impact

Primary file expected to change:

- `frontend/src/components/common/TabBar.vue`

Secondary file may be updated if simple helper methods are needed:

- `frontend/src/stores/tabs.ts`

No other layout components are required for this change unless implementation reveals a small integration need.

## 6. Implementation Constraints

- Keep the existing tab data model
- Prefer adding small helpers over store refactors
- Keep styling aligned with the current polished workbench shell
- Avoid adding heavy animation or modal behavior
- Keep the tab list panel lightweight and fast

## 7. Testing and Verification

Implementation should be verified by checking:

- few-tab state still looks clean
- many-tab state remains usable
- opening a new tab keeps the active tab visible
- clicking list entries switches tabs correctly
- close current, close others, and close all behave correctly
- layout still works at narrower desktop widths

## 8. Risks and Mitigations

Risk: tab controls may become visually noisy if too many actions are added.

Mitigation:

- keep left/right controls minimal
- keep list entry as the main management affordance
- include only the most common batch actions

Risk: tab list behavior may drift from the current store behavior.

Mitigation:

- reuse existing open/close/switch methods wherever possible
- add only minimal store helpers if required

## 9. Out of Scope

- Saved tab groups
- Multi-row tab layouts
- Drag-and-drop tab reordering
- Cross-window tab management
- Editor content changes

## 10. Recommended Next Step

Create a short implementation plan focused on:

1. refactoring the tabbar layout into left/center/right zones
2. adding overflow scroll controls
3. adding the all-tabs list panel
4. adding minimal batch close actions
5. verifying few-tab and many-tab states
