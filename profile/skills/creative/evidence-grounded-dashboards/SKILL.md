---
name: evidence-grounded-dashboards
description: Use when turning source material into a verified dashboard.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [dashboard, visualization, evidence, mind-map, publishing, caddy]
    related_skills: [claude-design, notion, composio-connected-app-operations]
---

# Evidence-Grounded Dashboards

## Purpose

Turn documents, connected-app records, research digests, or structured notes into a visual dashboard that is traceable to the source, explicit about inference, responsive, executable as a real artifact, and optionally published at a stable URL.

Use this umbrella after source retrieval is complete. It complements `claude-design` (visual craft) and source-specific skills such as `notion` or `composio-connected-app-operations`; it does not replace their retrieval, permission, or mutation rules.

## Core Principles

1. **Start from evidence, not layout.** Build a fact table before drawing metrics.
2. **Separate fact from interpretation.** Source metadata and direct claims must be visually distinct from synthesis, maturity scores, recommendations, and inferred gaps.
3. **Never manufacture business performance.** If the source lacks revenue, completion, staffing, or KPI data, do not create plausible numbers.
4. **Label heuristic scales.** A maturity score is an editorial assessment of source completeness unless measured data proves otherwise.
5. **Use the right surface.** An executive dashboard is a Monitor surface: glanceability, density, hierarchy, and drill-down beat a marketing hero.
6. **Ship a working artifact.** Create the complete HTML, exercise it, inspect screenshots, and verify the published bytes when deployment is requested.

## Workflow

### 1. Establish source scope

Capture:

- source title and authoritative URL or object ID;
- workspace/account identity when relevant;
- retrieval timestamp and timezone;
- accessible object count and permission limits;
- source metadata such as status, owner, dates, priority, and relations;
- the body or digest used for synthesis.

Use phrases such as “the integration can currently access” when provider sharing may hide other content.

Completion criterion: every material dashboard claim can be traced to a source field, source passage, or clearly labeled inference.

### 2. Build the data contract

Create three buckets:

- **Observed facts:** direct source metadata and text.
- **Derived structure:** themes, branches, categories, and relationships extracted from the source.
- **Editorial assessment:** maturity grades, gaps, priorities, and recommendations.

See `references/data-contract.md` for a reusable schema and scoring rules.

### 3. Choose the visual model

For strategic documents, prefer:

- a central mind map for themes and relationships;
- a compact metadata rail for source facts;
- a 0–4 maturity scale for completeness, only when labeled heuristic;
- a maturity ladder that explains what each level means;
- an evidence panel and a separate gaps/actions panel.

Avoid equal-weight card grids, decorative statistics, generic icons, and gradients that obscure hierarchy.

### 4. Implement a portable artifact

Default to one self-contained HTML file:

- embedded CSS and JavaScript;
- semantic sections and accessible labels;
- keyboard-operable mind-map nodes;
- responsive layouts for desktop and narrow mobile widths;
- no remote runtime dependencies unless justified;
- `prefers-reduced-motion` support;
- source links opened with `rel="noopener"`.

Mind-map branches should update a detail inspector instead of forcing all text into the diagram.

### 5. Verify locally

Minimum checks:

1. parse the HTML and assert expected section/node counts;
2. extract JavaScript and run a syntax check;
3. serve locally and require HTTP 200 with the expected content type;
4. capture desktop and mobile screenshots;
5. inspect for clipping, overlap, horizontal overflow, unreadable labels, and missing sections;
6. run the design skill’s anti-slop audit and record the score.

Do not declare completion from source-code inspection alone.

### 6. Publish safely when requested or established as a user preference

Before public deployment:

- confirm the source is safe to expose;
- remove secrets, private IDs, internal URLs, and confidential text;
- choose a stable path that does not displace an existing application;
- preserve the existing web-server configuration;
- validate the proposed site configuration before reload.

For Caddy subpath publishing, follow `references/caddy-subpath-publishing.md`.

### 7. Verify production independently

After deployment:

- require public HTTP 200 and the correct content type;
- verify TLS and security headers when applicable;
- compare the remote artifact hash with the local artifact;
- confirm the existing upstream/root application still returns its expected response;
- capture a screenshot from the public URL;
- report the stable URL, local artifact path, evidence limits, and verification results.

## Mind-Map Guidance

- Keep the center to one entity or strategy.
- Use 4–7 first-level branches; more becomes a taxonomy, not a mind map.
- Give each branch a short title and at most three terse diagram labels.
- Put full concepts in the inspector/detail area.
- Make selected state obvious in both the node and connecting edge.
- On mobile, allow the diagram to scale without horizontal scrolling; keep tap targets at least 44 px where feasible.

## Maturity Scoring

Use a disclosed 0–4 completeness scale:

- **0 — Absent:** not mentioned.
- **1 — Concept:** named but not operationally defined.
- **2 — Planning:** structure or intended approach exists; prioritization is incomplete.
- **3 — Operation-ready:** owners, dates, resources, dependencies, and cadence are specified.
- **4 — Measured/scale:** repeated execution and historical metrics are present.

Score source definition, not business quality. Add a visible note: “Heuristic assessment of source detail; not measured performance.”

## Social Audience Dashboards

When the source is a social-platform API, treat identity, aggregate audience metrics, content performance, and editorial inference as four separate evidence layers. Before designing, record the reporting window, timezone, account type, demographic coverage, platform suppression thresholds, sample size, and whether each metric is unique or non-unique. Never present inferred content niches as personal attributes of individual followers.

For a reusable Instagram/Meta extraction, interpretation, Drive-delivery, and quota-fallback workflow, see `references/social-audience-dashboard.md`.

## Verification Checklist

- [ ] Facts, derived structure, and editorial inference are separated
- [ ] No unsupported performance metric appears
- [ ] Source and retrieval boundary are visible
- [ ] Mind map has 4–7 first-level branches
- [ ] Interactive nodes are keyboard operable
- [ ] Maturity scale and caveat are visible
- [ ] HTML and JavaScript checks pass
- [ ] Desktop and mobile screenshots were inspected
- [ ] No horizontal overflow or clipped content
- [ ] Public source safety was checked
- [ ] Proposed web-server config was validated
- [ ] Existing upstream still works after reload
- [ ] Remote and local hashes match

## Common Pitfalls

1. **Turning missing data into fake metrics.** Show “not defined” and make the gap actionable.
2. **Presenting maturity as objective performance.** Label the scale as heuristic and explain its basis.
3. **Overloading the mind map.** Keep diagram labels short and move detail into an inspector.
4. **Publishing over an existing reverse proxy.** Add a specific `handle_path` before the fallback `handle`.
5. **Validating only the new Caddy fragment.** Validate both the fragment and the complete imported configuration.
6. **Assuming deployment succeeded because reload exited zero.** Fetch the public URL, verify the root app, compare hashes, and inspect a public screenshot.
7. **Leaking source-system identifiers.** Public dashboards rarely need internal object IDs or integration credentials.
