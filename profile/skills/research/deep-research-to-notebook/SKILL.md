---
name: deep-research-to-notebook
description: "Use when researching deeply and proposing sources for Open Notebook."
version: 1.0.0
metadata:
  hermes:
    tags: [deep-research, web-search, scraping, source-verification, open-notebook]
---

# Deep Research to Open Notebook

## Trigger

Use when the user asks to investigate a topic, compare claims, find reliable sources, scrape public evidence, digest information, or save research into Open Notebook.

## Workflow

### 1. Frame the investigation

Write a compact research brief containing:

- exact question;
- intended decision or output;
- geography, time range and cutoff date;
- inclusion/exclusion criteria;
- what would count as sufficient evidence.

Ask only when missing context materially changes the answer. Otherwise state reasonable assumptions.

### 2. Build a search matrix

Generate multiple query families: exact terms, synonyms, primary-source domains, contrary evidence, dates, file types and named entities. Search independently enough to avoid anchoring on the first result.

### 3. Retrieve and classify evidence

Use web search and extraction first. Use browser automation only for public dynamic pages that cannot be extracted otherwise. Never bypass access controls.

Classify every candidate:

- Tier A: official or primary.
- Tier B: peer-reviewed or institutional.
- Tier C: reputable secondary reporting.
- Tier D: discovery-only opinion/community material.

Reject pages with unclear provenance, copied claims without a primary link, material date mismatch, or inaccessible supporting content.

### 4. Keep a claim-evidence ledger

For each material claim record:

- claim;
- exact supporting URL(s);
- source authority tier;
- publication/update date and retrieval date;
- direct evidence versus inference;
- contradictions and limitations;
- confidence: high, medium or low.

A search-result snippet is not final evidence. Open/extract the underlying source before relying on it.

### 5. Cross-check and digest

Prefer primary sources and corroborate consequential claims with two independent sources where feasible. When evidence conflicts, show both sides and explain precedence. Preserve uncertainty and state what remains unknown.

Produce:

1. executive answer;
2. findings with inline source links;
3. evidence ledger;
4. contradictions and gaps;
5. practical implications;
6. ranked sources proposed for Open Notebook;
7. next minimum research action.

### 6. Approval gate before Open Notebook writes

Do not save automatically.

1. List the exact URLs and/or digest title proposed for saving.
2. Name the destination notebook.
3. Ask for explicit approval.
4. Only after approval, call the `open-notebook` MCP mutation with `approved=true`.
5. Return the real source ID and processing status.

Approval applies only to the exact proposed items and destination. If any item changes, request approval again.

## Tool routing

- General web: `web_search`, then `web_extract` or equivalent retrieval.
- Academic papers: load the `arxiv` skill when relevant; verify publication status separately.
- Official API capability claims: load `official-api-capability-research`.
- YouTube evidence: load `youtube-content`, cite the video and timestamp when possible.
- News/feed monitoring: load `blogwatcher` if recurring monitoring is requested.
- Complex independent workstreams: use delegation for parallel retrieval, then synthesize centrally.
- Open Notebook: use only the typed `open-notebook` MCP tools.

## Failure behavior

- If retrieval fails, say which source could not be opened and do not infer its contents from the title.
- If only low-authority evidence exists, label the result provisional.
- If a source cannot legally or technically be scraped, provide its public URL and explain the access limitation.
- If Open Notebook rejects a write, report the actual error and leave the item unsaved.

## Verification checklist

- [ ] Scope and date cutoff are explicit.
- [ ] Material claims link to retrieved sources.
- [ ] Primary sources were prioritized.
- [ ] Contradictions and uncertainty are visible.
- [ ] No fabricated citation, date or quote.
- [ ] Proposed notebook writes were shown before approval.
- [ ] Added items have real IDs/statuses from the API.
