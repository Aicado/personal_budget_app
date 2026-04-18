## 2025-04-18 - [Tab Accessibility and Hidden Labels]
**Learning:** When using `display: none` to hide text labels on mobile (leaving only icons), the element becomes inaccessible to screen readers as `display: none` removes the content from the accessibility tree. An `aria-label` on the parent button is necessary to maintain accessibility in this state.
**Action:** Always provide an `aria-label` for buttons that rely on icons for their mobile representation, even if they have text labels for desktop that are hidden via `display: none`.
