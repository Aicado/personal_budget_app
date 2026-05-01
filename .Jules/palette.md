## 2025-05-15 - [Tab Navigation Accessibility]
**Learning:** Adding redundant `aria-label` or `title` attributes to buttons that already contain visible text causes screen readers to announce the label twice, creating a poor user experience. ARIA labels should be reserved for icon-only elements or to provide missing context.
**Action:** Always check if a component has visible text before adding `aria-label`. Ensure `tabpanel` elements are focusable if they contain large amounts of content to aid keyboard navigation.

## 2025-05-16 - [Responsive Label Accessibility]
**Learning:** Using `display: none` to hide text labels on mobile (leaving only icons) makes elements inaccessible to screen readers. A "visually-hidden" CSS pattern should be used instead to keep the text in the accessibility tree while hiding it from the screen.
**Action:** Use absolute positioning and clipping to hide text labels on small viewports instead of `display: none`. Revert to `static` positioning on larger screens where labels should be visible.

## 2025-05-17 - [Data Visualization Accessibility]
**Learning:** For static data visualizations representing a measurement within a known range (e.g., spending categories), `role="meter"` is more semantic than `role="progressbar"`. Adding `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and a descriptive `aria-label` ensures these visual elements are accessible to screen reader users.
**Action:** Use `role="meter"` for static visualizations and `role="progressbar"` for ongoing tasks. Always provide quantitative values via ARIA attributes and a clear text label.

## 2025-05-24 - [Empty State Recovery Pattern]
**Learning:** When a filter results in an empty state (e.g., "Needs Data" filter showing 0 accounts), users can feel stuck or confused. Providing an immediate "Show All" or "Reset Filters" recovery action directly within the empty state message prevents a navigation dead-end and improves usability.
**Action:** Always include a recovery action in empty states that result from user-initiated filtering or searching. Use a secondary button style to provide a clear way back to the full data set.
