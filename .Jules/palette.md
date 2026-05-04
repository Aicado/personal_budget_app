## 2025-05-15 - [Tab Navigation Accessibility]
**Learning:** Adding redundant `aria-label` or `title` attributes to buttons that already contain visible text causes screen readers to announce the label twice, creating a poor user experience. ARIA labels should be reserved for icon-only elements or to provide missing context.
**Action:** Always check if a component has visible text before adding `aria-label`. Ensure `tabpanel` elements are focusable if they contain large amounts of content to aid keyboard navigation.

## 2025-05-16 - [Responsive Label Accessibility]
**Learning:** Using `display: none` to hide text labels on mobile (leaving only icons) makes elements inaccessible to screen readers. A "visually-hidden" CSS pattern should be used instead to keep the text in the accessibility tree while hiding it from the screen.
**Action:** Use absolute positioning and clipping to hide text labels on small viewports instead of `display: none`. Revert to `static` positioning on larger screens where labels should be visible.

## 2025-05-17 - [Data Visualization Accessibility]
**Learning:** For static data visualizations representing a measurement within a known range (e.g., spending categories), `role="meter"` is more semantic than `role="progressbar"`. Adding `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and a descriptive `aria-label` ensures these visual elements are accessible to screen reader users.
**Action:** Use `role="meter"` for static visualizations and `role="progressbar"` for ongoing tasks. Always provide quantitative values via ARIA attributes and a clear text label.

## 2026-05-04 - [Interactive Summary Navigation]
**Learning:** In dashboards where a summary list (e.g., "Items Needing Attention") and a main list (e.g., "All Items") coexist, converting summary items into interactive navigation links significantly improves usability, especially when combined with a temporary visual highlight (flash) to orient the user after scrolling.
**Action:** When providing status summaries, ensure they function as "quick links" to the relevant records and include a focus/highlight animation to provide immediate visual confirmation of the target.

## 2026-05-04 - [Conditional Redundancy Reduction]
**Learning:** Showing a "Needs Data" summary section while the "Needs Data" filter is active creates UI clutter and redundant information.
**Action:** Conditionally hide summary components when the active filter already isolates the exact same subset of data, keeping the interface focused on the filtered results.
