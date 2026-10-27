---
name: pagination-strategies
description: How to traverse all job listings on a career site, including numbered pages, load-more controls, and infinite scrolling.
---

# Pagination strategies

Career sites commonly use one of three patterns:

1. **Numbered pages or Next/Previous controls.** Follow pages until Next is disabled or the final page is reached. If the page number or offset is visible in the URL, direct navigation is fine.
2. **Load more.** Click the control, wait for additional jobs, and repeat until no new jobs appear.
3. **Infinite scroll.** Scroll to the bottom, wait for new jobs, and repeat until the listing stops growing.

For JavaScript-rendered pages, wait for the job list to appear before assuming the page is empty. Use any displayed result count as a cross-check.

Process each listing page before moving on. Stop only when you have reached the end of the current job listing.
