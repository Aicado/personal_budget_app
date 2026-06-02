## 2025-05-15 - [Tab Navigation Accessibility]
**Learning:** Adding redundant `aria-label` or `title` attributes to buttons that already contain visible text causes screen readers to announce the label twice, creating a poor user experience. ARIA labels should be reserved for icon-only elements or to provide missing context.
**Action:** Always check if a component has visible text before adding `aria-label`. Ensure `tabpanel` elements are focusable if they contain large amounts of content to aid keyboard navigation.

## 2025-05-16 - [Responsive Label Accessibility]
**Learning:** Using `display: none` to hide text labels on mobile (leaving only icons) makes elements inaccessible to screen readers. A "visually-hidden" CSS pattern should be used instead to keep the text in the accessibility tree while hiding it from the screen.
**Action:** Use absolute positioning and clipping to hide text labels on small viewports instead of `display: none`. Revert to `static` positioning on larger screens where labels should be visible.

## 2025-05-20 - [Contextual Redundancy Reduction]
**Learning:** In dashboards with persistent summary sections (e.g., "Items needing attention"), displaying the summary while an active filter is already focusing on those exact items is redundant and adds visual noise. Conditionally hiding these sections based on the active filter state streamlines the interface.
**Action:** Identify and hide summary widgets or headers that repeat the information already highlighted by the current view filter.

## 2025-05-17 - [Data Visualization Accessibility]
**Learning:** For static data visualizations representing a measurement within a known range (e.g., spending categories), `role="meter"` is more semantic than `role="progressbar"`. Adding `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and a descriptive `aria-label` ensures these visual elements are accessible to screen reader users.
**Action:** Use `role="meter"` for static visualizations and `role="progressbar"` for ongoing tasks. Always provide quantitative values via ARIA attributes and a clear text label.

## 2025-05-18 - [Contrast and Contextual UI]
**Learning:** Text colors like #7f8c8d on white backgrounds often fail WCAG AA contrast standards (4.02:1). Also, showing "Data Needed" summary alerts when a "Needs Data" filter is already active creates redundant UI noise.
**Action:** Use #65758a for secondary text to ensure >4.5:1 contrast. Conditionally hide summary sections when the user has already applied a filter that targets that exact state to improve clarity.

## 2026-05-23 - [Interactive List Accessibility and Feedback]
**Learning:** Scrollable containers for data (like transaction tables) must be explicitly focusable via `tabIndex={0}` and labeled with `role="region"` and `aria-label` to be navigable by keyboard users. Additionally, asynchronous actions within lists (like expanding an item that requires a fetch) should provide per-item visual feedback (loading spinners) and disable the specific trigger to prevent redundant requests and clarify state.
**Action:** Always wrap scrollable data regions with appropriate ARIA roles and labels. Ensure every async interaction has a corresponding loading state and disabled state on its trigger.

## 2025-05-24 - [Skip Link and Alert Accessibility]
**Learning:** Keyboard users and screen reader users need a "Skip to main content" link to efficiently bypass repetitive navigation. Furthermore, dynamic error messages must have `role="alert"` to be immediately announced by screen readers. Heading hierarchy (h1 -> h2 -> h3) is crucial for screen reader users to navigate the page structure via the rotor.
**Action:** Always include a visually-hidden (on focus, visible) skip link in dashboards. Ensure all error message containers use `role="alert"`. Audit heading levels in nested components to ensure they follow a logical sequence.

## 2025-05-25 - [Robust Financial Visualizations]
**Learning:** Visualizing mixed income and expenses requires using absolute values for sorting and bar magnitudes to ensure the most significant items are highlighted regardless of sign. Pair this with semantic coloring (green/purple) and explicit ARIA labels that specify the transaction type (income/expense) for clarity.
**Action:** Always use Math.abs() for sorting and width calculations in financial charts. Include the transaction nature in aria-labels.
