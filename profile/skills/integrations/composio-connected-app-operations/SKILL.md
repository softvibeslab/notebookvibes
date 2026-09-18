---
name: composio-connected-app-operations
description: Use when reading or acting through connected Composio apps.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [composio, gmail, google-calendar, google-drive, google-meet, notion, clickup, meta-ads, instagram, tiktok, tiktok-ads, social-analytics, oauth]
---

# Composio Connected App Operations

## Purpose

Operate connected SaaS accounts through the Composio CLI with explicit scope, verification, and provider-aware handling. This umbrella covers discovery, read-only inspection, authorized mutations, and audit verification across Gmail, Google Calendar, Notion, and similar toolkits.

Use this when a user asks what is in a connected account, requests an email or other external action, or asks for an agenda derived from multiple calendars. It complements UI/onboarding skills; it does not manage Telegram Mini App deployment.

## Core Workflow

1. **Resolve the live account context.** Run a read-only identity/profile tool before material actions when multiple connections may exist.
2. **Discover before execution.** Use `composio search '<use case>' --toolkits <slug>` to retrieve the current tool slug, schema example, plan, and pitfalls.
3. **Keep reads and writes distinct.** Read-only inventory can proceed directly. Sending, editing, creating, deleting, or moving requires explicit user intent in the current conversation.
4. **Build the smallest valid payload.** Omit optional file/path fields instead of passing empty strings. Avoid extra recipients, attachments, or HTML unless requested.
5. **Execute a mutation once.** Record returned IDs and do not blindly retry a non-idempotent action after an ambiguous timeout.
6. **Verify independently.** Query the provider's sent/list/search endpoint and match the returned ID, recipient, subject, or other stable handle.
7. **Report scope and limits.** State which account/workspace was used, what was found or changed, and whether permissions limited coverage.

## Safety Rules

- Never expose OAuth tokens, connection IDs, login URLs, or credential files.
- Treat an explicit request such as “envía un correo a X diciendo Y” as authorization for that exact send, not for future sends or related mutations.
- Preserve read-only behavior when the user asks only “qué tengo” or “dime mis eventos”.
- Never infer that an empty result means an empty account until connection status, sharing, pagination, and per-source errors have been checked.
- For non-idempotent tools, a transport failure is not proof that the provider rejected the request. Search for the intended artifact before retrying.

## Provider Playbooks

- **Gmail:** follow `references/gmail.md` for sender resolution, strict payload construction, and Sent verification.
- **Google Calendar:** follow `references/google-calendar.md` for account-local day boundaries, all-calendar coverage, and summary handling.
- **Google Drive / Meet recordings:** follow `references/google-drive-meet-recordings.md` for live access verification, folder traversal, pagination, large-response files, and calendar correlation.
- **Notion:** follow `references/notion.md` for accessible-inventory discovery, Markdown retrieval, and sharing diagnostics.
- **Meta Ads:** follow `references/meta-ads-system-user-tokens.md` for system-user prerequisites, asset assignment, token lifetime mismatches, least-privilege handling, and tutorial-video vetting.
- **Instagram Business analytics:** follow `references/instagram-business-analytics.md` for live identity verification, follower-roster limits, aggregate demographics, metric compatibility, media pagination, and defensible niche inference.
- **ClickUp hierarchy and task operations:** follow `references/clickup.md` for live workspace discovery, complete hierarchy traversal, folderless-list coverage, read-before-write task mutations, and independent verification.
- **GitHub repository publishing:** follow `references/github-repository-publishing.md` when Git credentials are unavailable but a connected GitHub toolkit can initialize an empty repository, batch a complete tree, and verify the remote independently.
- **TikTok and TikTok Ads:** follow `references/tiktok-and-ads.md` for capability discovery without an active connection, organic publishing constraints, Ads OAuth prerequisites, reporting-first rollout, and approval gates for spend-affecting mutations.
- **Scheduled cross-app briefs:** follow `references/scheduled-cross-app-briefs.md` for connection inventories, bounded parallel collectors, read-only ranking, graceful degradation, timezone-safe Hermes cron setup, and execution verification.

## General Verification Checklist

- [ ] Connected toolkit appears in discovery output
- [ ] Live account or workspace identity is known
- [ ] Current tool schema/example was retrieved
- [ ] Operation stayed within the user's requested scope
- [ ] Optional path/file fields were omitted unless populated
- [ ] Pagination and per-source errors were checked
- [ ] Mutation returned a real provider handle
- [ ] Mutation was verified through a separate read operation
- [ ] Final response distinguishes accessible data from potentially unshared data

## Common Pitfalls

1. **Using stale tool names from memory.** Discover the current tool and payload first.
2. **Passing `"attachment": ""`.** Some Gmail wrappers interpret it as a file path and fail with `ENOENT`; omit the field.
3. **Using host time for “tomorrow.”** Resolve the connected calendar's timezone before calculating date boundaries.
4. **Ignoring `summary_view`.** Minimal calendar responses may intentionally omit the full events array.
5. **Treating Notion 404 as deletion.** It often means the integration was not connected to the parent page or database.
6. **Assuming a connected toolkit exposes the whole workspace.** Provider sharing rules still limit visibility.
7. **Trusting one broad Drive query.** Traverse known recording folders by parent, recurse into nested folders, and follow every page token before concluding that recordings are absent.
8. **Ignoring `storedInFile`.** Large Composio responses may be written to `outputFilePath`; parse that file instead of treating missing inline data as an empty result.
9. **Identifying recordings by timestamp alone.** Correlate Calendar title, timezone, conference ID, organizer, and Drive metadata; label merely time-adjacent videos as unconfirmed.
10. **Repeating a provider form's token-lifetime claim as universal fact.** Meta may recommend or require expiring system-user tokens even when an integration asks for “non-expiring”; verify the current provider documentation and explain the rotation consequence.
11. **Recommending a generic Graph API Explorer tutorial for a server integration.** Confirm that the tutorial actually covers Business Manager system users, asset assignment, and the required Marketing API scopes.
12. **Treating a connected Instagram toolkit as proof of account access.** Run a read-only profile query and confirm the returned username and professional account type.
13. **Promising an Instagram follower roster.** The professional-account API provides counts and aggregate demographics, not a complete list of follower usernames; interaction participants are not a substitute.
14. **Sending date strings when the live wrapper validates Unix integers.** Inspect `composio tools info` and convert bounded dates to integer seconds when required, even if descriptive text mentions ISO dates.
15. **Calling content themes follower interests.** Report niche clusters as inferences from posts and performance, document the sample and denominator, and avoid sensitive individual profiling.
16. **Equating an active connection with event-driven automation.** Inspect toolkit triggers separately; when no suitable trigger exists, use a scheduled poll with explicit time bounds.
17. **Using an open-ended LLM cron prompt for a routine multi-app report.** Tool discovery and one slow provider can consume the run; prefer a tested, read-only collector with concurrent calls, per-source timeouts, graceful degradation, and `--no-agent` delivery when deterministic rules are sufficient.
18. **Trusting process exit code alone.** A Composio command may return JSON that reports `successful: false` or contains a nonempty `error`; validate transport status, JSON parsing, and provider status before treating a source as healthy.
19. **Running several full collectors concurrently.** A collector may already fan out into multiple Composio subprocesses; starting several such collectors in parallel can create nested contention and false empty reports. Parallelize bounded leaf reads inside one collector, but serialize top-level reports that each perform their own fan-out.
20. **Making polling monitors noisy.** Persist a semantic fingerprint for each event, emit only new or changed items, and produce empty stdout when there is nothing actionable; a Hermes `--no-agent` job then stays silent instead of sending repetitive “no changes” messages.
21. **Using `CLICKUP_GET_TEAMS` as workspace discovery because of its name.** Inspect its live schema; some wrappers require a known `team_id`. Prefer the authorized-workspaces action, then traverse spaces, folders, embedded lists, and folderless lists.
22. **Treating an auth-config search error as proof that TikTok tooling is absent.** Inspect toolkit metadata and the static tool inventory without executing; then distinguish organic TikTok OAuth from the separate TikTok Ads OAuth connection.
