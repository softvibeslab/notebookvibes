# Instagram Business analytics reference

## Capability boundary

The official Instagram professional-account API can expose profile counters, aggregate audience demographics, account-level insights, media lists, media insights, comments, and conversations when permissions allow. It does **not** provide a complete nominal roster of followers. Do not replace that boundary with scraping.

If a user needs a complete follower/following export, direct them to Instagram/Accounts Center → Your information and permissions → Download your information → Followers and following → JSON. Analyze the user-provided export after receipt.

## Read-only access probe

Use a minimal profile call against `me` and request only supported fields such as:

- username and name;
- account type;
- follower/following/media counts.

A connected-toolkit listing is not evidence of access. Treat 401/403, OAuth code 190, or an unexpected identity as a stop condition.

## Metric grouping patterns

Instagram insight calls are sensitive to period, aggregation type, breakdown, and timeframe. Isolate groups rather than requesting everything in one call.

### Demographics

Typical shape:

- metric: `follower_demographics`
- period: `lifetime`
- metric type: `total_value`
- timeframe: `this_month` or `this_week`
- breakdown: one of `age`, `gender`, `country`, or `city`

Run one breakdown per call. Report the returned cohort total and calculate coverage against the current follower count. Do not assume demographic rows cover every follower.

### Recent activity

For a 28–30 day window, use integer Unix timestamps and request compatible day/total metrics such as:

- reach;
- accounts engaged;
- total interactions;
- likes, comments, shares, saves, replies;
- views and profile views;
- website clicks and profile-link taps.

A successful call can omit unsupported or empty metrics. Omission means unavailable, not zero.

### Follower movement

Request follower-count and follows/unfollows metrics separately. A breakdown may use provider labels whose meaning is not self-evident. Confirm the action description and returned structure before calling categories “gained” or “lost.” Calculate net change only after semantics are confirmed.

### Online followers

A day/time-series response may represent followers online during each day rather than hourly peaks. A trailing zero can be an incomplete current day; do not present it as a sudden collapse without checking the timestamp and reporting window.

## Media sampling

Request a bounded page of recent media with:

- caption;
- timestamp;
- media type and product type;
- public permalink;
- likes and comments;
- views, saves, and shares when supported.

Reels may appear as `media_type=VIDEO` with `media_product_type=REELS`. Optional fields can be absent. Paginate with the opaque cursor only; do not persist or echo a provider-generated `paging.next` URL because it can contain sensitive parameters.

## Niche analysis

A defensible niche analysis should:

1. cluster captions, hashtags, formats, and visual themes;
2. retain supporting post links or IDs internally;
3. compare response within comparable time/format cohorts;
4. label results as editorial hypotheses;
5. distinguish the account's content themes from individual followers' interests;
6. avoid sensitive-trait inference.

Visible likes/comments alone are a preliminary signal. Without per-media reach, do not call them normalized engagement rates.

## Knowledge-base contract

Recommended sections:

- account identity and cutoff;
- source and permission boundary;
- demographic coverage;
- geography;
- recent activity and follower movement;
- content sample and top posts;
- inferred niches with confidence;
- strategic hypothesis;
- minimum validation experiment;
- methodology, limitations, and privacy statement.

## Delivery lessons

- Verify every remote write with a returned item ID and read-back/listing.
- Drive folder creation can succeed while later uploads fail because storage quota is full; report the partial state precisely.
- For Open Notebook, propose the exact digest and destination first, obtain explicit approval, then create/add and report notebook/source IDs.
- An Open Notebook source with status `new` or `queued` exists but is not yet processed; verify source count and report the asynchronous state honestly.
