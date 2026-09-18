# TikTok and TikTok Ads via Composio

## Separate the products

Treat these as distinct toolkits and OAuth connections:

- `tiktok`: authenticated creator profile, public-video inventory, upload/publishing, and publish-status checks.
- `tiktok_ads`: advertisers, campaigns, ad groups, ads, audiences, creatives, catalogs, Business Centers, billing, transactions, and reporting.

Never infer that one connection authorizes the other.

## Capability discovery without a connection

`composio search ... --toolkits <slug>` can fail before search when a toolkit requires an auth config that does not exist. That failure does **not** mean the toolkit or tools are unavailable.

Use developer metadata and tool inventory instead:

```bash
composio dev --mode on toolkits info tiktok
composio dev --mode on toolkits info tiktok_ads
composio tools list tiktok
composio tools list tiktok_ads
```

Inspect live `tools_count`, `triggers_count`, auth modes, managed-auth availability, tags, and descriptions. Do not hard-code historical counts or assume event triggers exist.

## Organic TikTok workflow

1. Confirm a live `tiktok` connection and authenticated identity.
2. Read profile statistics with the current user-stats tool.
3. List only the authenticated user's public videos; private, friends-only, and draft content may be absent by API design.
4. Before direct posting, query creator options and use an actually returned privacy level.
5. Distinguish upload from publication. Publishing is asynchronous; retain the returned publish ID and poll the status tool with backoff.
6. Photo URLs may need to come from a TikTok-verified domain.
7. Unaudited applications can be restricted to `SELF_ONLY`; report that as an app-review limitation rather than an execution bug.
8. Publishing or uploading requires explicit approval for the exact asset, caption, privacy, interaction settings, and account.

## TikTok Ads workflow

1. Confirm a separate active `tiktok_ads` connection and resolve accessible advertiser/Business Center identities.
2. Start read-only: advertisers → campaigns → ad groups → ads → reports and balances.
3. Record the reporting window, currency, timezone, attribution basis, and provider-returned metric names.
4. Build anomaly alerts and recommendations before enabling mutations.
5. For creation/update actions, present advertiser, objective, targeting, creative, budget, schedule, bid strategy, and initial operation status.
6. Prefer disabled/draft resources where the tool supports them. Verify nested defaults: copying a disabled campaign can still create enabled child resources.
7. Re-read every created or changed resource and confirm operation status and budget before reporting success.

## Approval boundary

The following always require explicit current-conversation approval:

- publish organic content;
- create, enable, pause, copy, or delete ads/campaign resources;
- change targeting, bids, budgets, schedules, identities, or Business Center assignments;
- submit appeals or irreversible export/compliance requests.

A request for analysis authorizes reads and recommendations, not spend-affecting mutations.

## Authentication pitfall

Some toolkits expose OAuth2 tools but have no auto-creatable managed auth configuration. In that case, create/select the provider app's auth config and complete OAuth; do not interpret the search-session error as absence of the product. Never ask the user to paste access tokens into chat.
