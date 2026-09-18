# Google Calendar through Composio

## Interpret relative dates in account time

For “today” or “tomorrow,” do not use the host timezone blindly.

1. Read the connected account's current time when available.
2. Retrieve the calendar timezone setting (typically setting `timezone`).
3. Compute exact local start/end boundaries in that IANA timezone.
4. Pass ordered RFC 3339 `time_min` and `time_max` values.

A request made after midnight on the host may still belong to the prior local day in the calendar timezone.

## Coverage

Use the all-calendars listing tool when the user asks broadly about “my calendar.” Set recurring expansion (`single_events=true`) and a bounded result limit. Check:

- `calendars_queried` for coverage;
- `errors_by_calendar` before claiming completeness;
- pagination tokens where returned;
- `summary_view` even when `events` is empty.

Minimal response modes may intentionally return only `summary_view`; this is not an empty agenda.

## Presentation

Separate timed events from all-day events. State the interpreted date and timezone. Mention the number of calendars queried and any coverage errors when relevant. Avoid claiming “no events” unless every selected calendar was queried successfully.

## When detail is needed

Fetch an individual event only when the user needs attendees, location, conference URL, description, or authoritative recurrence metadata. Keep ordinary agenda answers concise.
