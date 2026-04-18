## 2025-05-15 - [Tab Navigation Accessibility]
**Learning:** Adding redundant `aria-label` or `title` attributes to buttons that already contain visible text causes screen readers to announce the label twice, creating a poor user experience. ARIA labels should be reserved for icon-only elements or to provide missing context.
**Action:** Always check if a component has visible text before adding `aria-label`. Ensure `tabpanel` elements are focusable if they contain large amounts of content to aid keyboard navigation.
