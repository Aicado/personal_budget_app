## 2025-05-15 - [Tab Navigation Accessibility]
**Learning:** Adding redundant `aria-label` or `title` attributes to buttons that already contain visible text causes screen readers to announce the label twice, creating a poor user experience. ARIA labels should be reserved for icon-only elements or to provide missing context.
**Action:** Always check if a component has visible text before adding `aria-label`. Ensure `tabpanel` elements are focusable if they contain large amounts of content to aid keyboard navigation.

## 2025-05-16 - [Responsive Label Accessibility]
**Learning:** Using `display: none` to hide text labels on mobile (leaving only icons) makes elements inaccessible to screen readers. A "visually-hidden" CSS pattern should be used instead to keep the text in the accessibility tree while hiding it from the screen.
**Action:** Use absolute positioning and clipping to hide text labels on small viewports instead of `display: none`. Revert to `static` positioning on larger screens where labels should be visible.

## 2025-05-17 - [Loading States and Decorative Emoji Accessibility]
**Learning:** Asynchronous actions like "Refresh" need immediate visual feedback (e.g., a spinner) to prevent users from double-clicking or assuming the app is frozen. Additionally, decorative emojis in headers and stats cards create unnecessary noise for screen readers and should be hidden.
**Action:** Implement a CSS-based `.spinner` class for consistent loading feedback. Wrap all decorative emojis in `<span aria-hidden="true">`.
