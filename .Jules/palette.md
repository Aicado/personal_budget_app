## 2025-05-15 - [Tab Navigation Accessibility]
**Learning:** Adding redundant `aria-label` or `title` attributes to buttons that already contain visible text causes screen readers to announce the label twice, creating a poor user experience. ARIA labels should be reserved for icon-only elements or to provide missing context.
**Action:** Always check if a component has visible text before adding `aria-label`. Ensure `tabpanel` elements are focusable if they contain large amounts of content to aid keyboard navigation.

## 2025-05-16 - [Responsive Label Accessibility]
**Learning:** Using `display: none` to hide text labels on mobile (leaving only icons) makes elements inaccessible to screen readers. A "visually-hidden" CSS pattern should be used instead to keep the text in the accessibility tree while hiding it from the screen.
**Action:** Use absolute positioning and clipping to hide text labels on small viewports instead of `display: none`. Revert to `static` positioning on larger screens where labels should be visible.

## 2025-05-17 - [Data Visualization Accessibility]
**Learning:** For static data visualizations representing a measurement within a known range (e.g., spending categories), `role="meter"` is more semantic than `role="progressbar"`. Adding `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and a descriptive `aria-label` ensures these visual elements are accessible to screen reader users.
**Action:** Use `role="meter"` for static visualizations and `role="progressbar"` for ongoing tasks. Always provide quantitative values via ARIA attributes and a clear text label.

## 2025-05-18 - [Secondary Text Contrast]
**Learning:** Secondary text (labels, descriptions, and status messages) often uses light gray shades (like `#7f8c8d`) for visual hierarchy that fail WCAG AA contrast requirements (3.42:1). These small details significantly impact legibility for users with visual impairments.
**Action:** Audit "gray" text across the application. Replace `#7f8c8d` with `#546e7a` (or similar) to achieve a 4.5:1+ contrast ratio on light backgrounds while maintaining the "secondary" feel.
