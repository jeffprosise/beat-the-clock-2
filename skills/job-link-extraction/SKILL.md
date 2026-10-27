---
name: job-link-extraction
description: How to distinguish individual job-detail links from navigation, filters, application links, and other links on a career site.
---

# Job link extraction

Identify links that lead to individual job-detail pages.

Strong signals include:

- A unique job ID in the path or query string.
- A distinct URL for each posting.
- A link associated with a specific job title or job card.

Exclude pagination, filters, category/location pages, login links, general navigation, and "similar jobs" links found on detail pages.

Prefer the company's readable job-detail page over a separate application/login URL when both are present. Use absolute URLs and never invent or guess a URL.
