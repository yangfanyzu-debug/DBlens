# DBLens Frontend Workbench Polish Design

**Date**: 2026-04-24
**Status**: Drafted for review
**Scope**: Conservative front-end layout and visual polish for the existing DB workbench UI

## 1. Goal

Improve the front-end layout and styling without changing product structure, workflow, or business logic.

This pass is intentionally conservative:

- Keep the current GitHub/IDE-inspired visual language
- Improve hierarchy, spacing, and surface consistency
- Make the sidebar and work area feel more deliberate and more polished
- Upgrade the empty state so first-use guidance feels complete

This pass does not include:

- Rebuilding navigation or information architecture
- Adding new product features
- Turning the interface into a marketing-style landing page
- Refactoring unrelated components

## 2. Success Criteria

The work is successful when:

- The first screen reads clearly as a two-region workbench: navigation on the left, active workspace on the right
- The sidebar header feels like a stable application anchor instead of a plain toolbar
- Buttons, borders, shadows, radii, and spacing feel consistent across the visible shell
- The empty state gives users a clearer starting point without adding extra workflow steps
- Existing interactions continue to work as they do now

## 3. Visual Direction

### Visual thesis

DBLens should feel like a focused desktop data tool: calm, precise, and slightly refined, with stronger surface hierarchy rather than stronger decoration.

### Content plan

- Sidebar: application anchor, connection entry point, schema navigation
- Main workspace: tabbed working surface
- Empty state: orient the user, explain the next action, reduce first-use ambiguity

### Interaction thesis

- Subtle hover and focus feedback should make controls feel more intentional
- Surface transitions should stay restrained and fast
- The resize handle should remain discoverable without pulling attention away from the workspace

## 4. Design Decisions

### 4.1 App Shell

The existing left-right split remains unchanged.

Changes:

- Refine app shell background layering so the sidebar, tab strip, and content surface feel related but distinct
- Reduce any overly heavy shadow treatment that makes the shell feel boxed in
- Improve the resize affordance so it is easier to notice and use

Rationale:

The current structure is already appropriate for a database tool. The issue is not layout choice but layout finish.

### 4.2 Sidebar

The sidebar remains the navigation and entry zone for database work.

Changes:

- Strengthen the header as a product anchor with a more deliberate logo block, title treatment, and balanced spacing
- Keep the primary action visible, but make it lighter and less visually competitive with the product name
- Add more rhythm between the header and the scrollable tree area
- Improve visual grouping between connection list content and schema tree content without wrapping everything in cards

Rationale:

The sidebar should feel dependable and scannable. It needs clearer structure, not more UI chrome.

### 4.3 Main Workspace

The main area remains a tab-driven workspace.

Changes:

- Clarify separation between the tab bar and the active content region
- Add a slightly more intentional background/surface relationship so the workspace feels like a single product plane
- Preserve density and operational feel; do not add hero content or decorative feature blocks

Rationale:

This is a productivity surface. The polish should improve orientation, not reduce usable space.

### 4.4 Empty State

The current empty state will be upgraded into a lightweight onboarding panel.

Changes:

- Keep a compact visual mark or graphic
- Replace the minimal placeholder with a clearer title, short explanation, and one or two concrete starting cues
- Present the message as part of the workspace surface rather than as floating decorative content

Rationale:

When no tabs are open, the interface currently feels under-explained. A stronger empty state improves usability without changing flow.

## 5. Component Impact

Primary files expected to change during implementation:

- `frontend/src/style.css`
- `frontend/src/components/layout/AppLayout.vue`
- `frontend/src/components/layout/Sidebar.vue`
- `frontend/src/components/layout/MainArea.vue`

Secondary files may be touched only if needed for shell consistency:

- `frontend/src/components/common/TabBar.vue`

No business-logic stores or API files are part of this design scope.

## 6. Implementation Constraints

- Match the current code style and component structure
- Keep edits surgical and traceable to this visual polish scope
- Avoid broad refactors or component extraction unless a file becomes harder to maintain without it
- Reuse the existing theme token approach in `frontend/src/style.css`
- Preserve current dark/light theme behavior

## 7. Testing and Verification

Implementation should be verified by checking:

- App shell layout still fills the viewport correctly
- Sidebar resize still works if already present in the current branch
- Sidebar header remains readable in both light and dark themes
- Empty state spacing, copy hierarchy, and action cues read well at common desktop widths
- No overflow regressions appear in the main work area

If local UI verification is available, compare:

- no-tab empty state
- populated sidebar with connection tree
- tabbed workspace with content active

## 8. Risks and Mitigations

Risk: polishing shell styles may accidentally clash with existing in-progress edits in the same files.

Mitigation:

- Limit changes to layout shell, spacing, and presentation
- Review the current file state before editing
- Avoid rewriting unrelated sections

Risk: overusing shadows or gradients could break the intended conservative direction.

Mitigation:

- Prefer borders, spacing, and tonal contrast before adding stronger decoration
- Keep accent usage limited to the existing blue action/focus language

## 9. Out of Scope

- New navigation modes
- New onboarding flows or guided tours
- Query editor feature changes
- Table/grid behavior changes
- Data model, store, or API changes

## 10. Recommended Next Step

Create a short implementation plan focused on:

1. global shell tokens and spacing polish
2. sidebar header and body refinement
3. main workspace and empty-state upgrade
4. visual verification in light and dark themes
