---
name: social-audience-intelligence
description: Use when auditing social audiences, niches, and content.
version: 1.0.0
metadata:
  hermes:
    tags: [social-media, audience, analytics, instagram, dashboard, privacy]
---

# Social Audience Intelligence

## Purpose

Turn authorized social-platform data into a privacy-preserving audience audit, content taxonomy, actionable dashboard, and reusable knowledge base. Use official APIs and connected accounts; never substitute scraping or session-cookie automation for missing API capabilities.

## Core principles

1. **Verify access before claiming it.** Execute a harmless profile read and report the authenticated identity, account type, and fields actually returned.
2. **Separate API availability from actual retrieval.** A toolkit search or schema does not prove account access.
3. **Use aggregate audience data.** Do not promise a follower roster when the official API exposes only counts and demographics.
4. **Separate observation from inference.** Demographics and engagement are observed; niches and positioning are editorial hypotheses.
5. **Respect time windows and metric semantics.** Unique reach, profile visits, views, interactions, and follower changes are not interchangeable.
6. **Ship verified artifacts.** Dashboards must be executed, inspected at desktop/mobile widths, and packaged with source data and methodology.

## Workflow

### 1. Establish the account context

Run a read-only profile query and capture username, display name, professional account type, follower/following/media counts, retrieval timestamp, timezone, and permission limitations. Do not expose internal account IDs unless technically necessary.

### 2. Define the analysis window

Use a bounded recent window, normally 28–30 days, plus a clearly labeled lifetime or current-month demographic snapshot. Convert dates to provider-required Unix timestamps with a real calculation tool. Record start/end dates, timezone, whether the end date is partial, and provider aggregation period/type.

### 3. Retrieve independent evidence groups

Keep calls small enough to isolate incompatible metric combinations:

- profile counters;
- age, gender, country, and city demographics;
- reach, views, profile visits, interactions, and link activity;
- follows and unfollows;
- recent media with captions, formats, timestamps, and visible engagement;
- per-media insights only when the API and media type support them.

If a provider silently omits a metric, report it as unavailable rather than zero.

### 4. Normalize and preserve evidence

Create a portable bundle:

- `social_data.json` — consolidated responses and methodology;
- `audience_metrics.csv` — long-form aggregate metrics;
- `recent_media_sample.csv` — content sample and visible engagement;
- `README.md` — scope, findings, caveats, and recommendations;
- `index.html` — self-contained dashboard;
- `VERIFICATION.md` — execution and visual QA evidence.

Never store OAuth tokens, pagination URLs with embedded credentials, cookies, or private API secrets.

### 5. Calculate defensible derived metrics

Use an execution tool for arithmetic. Good measures include demographic coverage, distribution percentages, net follower change, growth rate relative to a declared denominator, and engagement by content theme or format when fields are comparable. Do not calculate a conversion rate across metrics with incompatible definitions; profile visits can be non-unique while reach is unique.

### 6. Infer niches carefully

Build niches from captions, hashtags, visual themes, formats, and performance. Label them as **editorial inferences**, not facts about individual followers. For each niche record supporting posts, observed response, confidence, competing explanation, and the minimum experiment needed to validate it. Never infer sensitive personal attributes.

### 7. Build a Monitor-style dashboard

Use a dense, glanceable Monitor surface. Include account/data cutoff, KPI rail, demographic distributions, geography ranking, recent activity/growth, interactive knowledge map, top-content table, facts/inferences boundary, limits, and recommended experiment. Follow the evidence-grounded dashboard verification workflow.

### 8. Verify delivery

1. Parse HTML and count expected sections.
2. Extract JavaScript and run a syntax check.
3. Serve locally and require HTTP 200.
4. Test at least one interaction.
5. Capture desktop and mobile screenshots.
6. Assert no horizontal overflow.
7. Inspect console errors.
8. Package artifacts and list archive contents.

For connected storage, create the destination and verify it by returned ID. Upload files one by one and verify metadata. A created folder does not prove upload success. If storage quota blocks upload, preserve the folder, report the exact provider error, and deliver the bundle through an available local/chat attachment path rather than deleting user files.

### 9. Add to Open Notebook only after approval

Before writing: list notebooks; name the exact destination; present the exact digest title and sections; obtain explicit approval; create the notebook if approved and absent; add the digest with `approved=true`; report real notebook/source IDs; verify source count and asynchronous status without claiming completion while queued.

## Reporting standard

Distinguish **Observed**, **Derived**, **Inferred**, and **Unavailable**. Include the analysis window, coverage, sample size, account type, and major API limitations.

## Instagram-specific reference

See `references/instagram-business-analytics.md` for metric-grouping patterns, capability boundaries, and interpretation pitfalls discovered during an authenticated Instagram Business audit.
