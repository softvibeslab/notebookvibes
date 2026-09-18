# Scheduled cross-app executive briefs

Use this pattern for daily or weekly reports that combine several Composio-connected services and must keep running when one provider is slow or unavailable.

## 1. Inventory and scope

1. Run `composio connections list` and classify each toolkit as active, expired, or absent.
2. Verify provider identity with a read-only provider tool (for example Gmail profile, Calendar primary entry, GitHub authenticated user, Notion identity). Do not rely on the global CLI identity alone.
3. List available triggers separately. An active connection does not imply event triggers exist; a toolkit without triggers may require scheduled polling.
4. Record operational blockers independently from connection state. Example: Drive may authenticate and read successfully while writes fail because storage quota is exhausted.

## 2. Prefer a bounded collector for durable briefs

A broad scheduled LLM prompt may spend most of its run discovering tools or waiting on one provider. For recurring operational reports, prefer a deterministic collector script and run it as a Hermes `--no-agent` cron job when the report can be produced with rules.

Collector design:

- Resolve the user's IANA timezone and derive explicit time windows.
- Discover and test current Composio tool schemas during setup; do not hard-code guessed payloads.
- Execute independent provider reads concurrently.
- Give each subprocess a strict timeout.
- Parse all three failure channels: nonzero exit, invalid JSON, and a JSON body with `successful: false` or nonempty `error`.
- Continue when one source fails and include a limits section naming that source.
- Cap records and omit message bodies, tokens, internal connection IDs, and other unnecessary sensitive content.
- Deduplicate repeated alerts by a stable semantic key such as normalized subject + sender.
- Rank actionable signals above provider labels: security alerts, delivery failures, invoices, meetings, and explicit action requests should outrank promotions and social notifications.
- Keep the first version read-only. Sending mail, editing calendars, changing tickets, or posting content requires a separate approval flow.
- Avoid nested fan-out: if individual collectors already launch Composio calls concurrently, run those collectors sequentially in an umbrella report. Otherwise local CLI contention can make healthy sources look empty or unavailable.

### Sparse monitors

For frequent polling jobs such as upcoming-meeting or repository-change alerts:

1. Store a small local state file under the active profile's `runtime/` directory.
2. Fingerprint provider items with a stable semantic key: normalized event title + start time, or resource URL + updated timestamp + state.
3. Prune stale fingerprints so the state file remains bounded.
4. Emit a report only for unseen or changed items.
5. Emit **empty stdout** when nothing changed. In Hermes `--no-agent` mode this keeps the job silent and avoids repetitive Telegram messages.
6. Add a dry-run environment flag that ignores state and widens the lookahead window, so the collector can be exercised without consuming or suppressing a real future alert.

## 3. Hermes scheduling pattern

1. Set or verify the Hermes profile timezone before creating the schedule. Cron expressions are evaluated in the configured Hermes timezone.
2. Put reusable collectors under the active profile's `scripts/` directory.
3. Create a bounded job:

```bash
hermes cron add '0 8 * * *' \
  --name 'Daily executive brief' \
  --deliver origin \
  --script cross_app_brief.py \
  --no-agent
```

4. Verify the displayed `Next run` includes the expected UTC offset.
5. Trigger a real test with `hermes cron run <job-id>`.
6. Confirm both execution and scheduler state:

```bash
hermes cron runs <job-id> --limit 3
hermes cron list
```

A valid verification shows a completed run, `Last run ... ok`, the intended delivery target, and the correct next-run timestamp.

## 4. Retry and recovery

- If parallel discovery calls time out or return transient server errors, stop the fan-out, inspect live processes, and retry discovery sequentially with a narrower query.
- Preserve the lesson as bounded retry/backoff; do not encode a permanent claim that the CLI or toolkit is broken.
- If a manual test is interrupted and leaves a stale run associated with the job, prefer removing and recreating the job rather than editing the execution database directly.
- If a service is temporarily stopped for diagnosis, restart it and verify its active state before continuing.

## 5. Report contract

A useful executive brief should include:

1. Cutoff time and timezone.
2. Three ranked priorities.
3. Calendar window and conflicts.
4. Messages likely to need attention, using subjects/senders rather than full bodies.
5. Technical or project alerts.
6. Knowledge-base or task changes.
7. Per-source limits and failures.
8. One minimal next action.
9. An explicit statement that the collector performed no mutations.
