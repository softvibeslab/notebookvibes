# Notion through Composio

## Establish workspace identity

Use a read-only identity tool first when available. Record the workspace name and integration/bot identity, not tokens.

## Inventory accessible content

Run broad search separately for:

1. pages (`filter_property=object`, `filter_value=page`);
2. databases/data sources (`filter_value=database`).

Use an empty query and the largest safe page size, then follow `has_more` / `next_cursor`. Deduplicate by object ID.

A page result whose parent is a database can remain readable even when the parent database itself is not shared with the integration.

## Read and summarize

For selected pages:

- retrieve metadata to extract title, status, dates, owner, relations, archive/trash state, and public URL;
- use the page-Markdown tool for readable content;
- clearly separate page properties from your synthesis of the body.

## Permission diagnostics

An empty database search or `object_not_found`/404 for a known parent commonly means the Notion page/database was not shared with the Composio integration. It does not prove the database was deleted or the workspace is empty.

Tell the user how to expand visibility: in Notion, open the page/database, use the `...` menu, choose `Connect to`, and select the Composio integration. Do not request that credentials be pasted into chat.

## Reporting

Say “the integration can currently access…” rather than “your Notion contains only…”. Include accessible item counts, titles, important properties, links when available, and a concise content summary. Explicitly mention visibility limitations.
