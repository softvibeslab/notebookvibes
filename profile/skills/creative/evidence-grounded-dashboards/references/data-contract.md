# Dashboard Data Contract

Use this compact structure before implementation.

```yaml
source:
  title: ""
  url: ""
  system: "notion | open-notebook | document | other"
  retrieved_at: "RFC3339"
  visibility: "public | private | integration-scoped"
  limitations: []

facts:
  metadata:
    status: null
    owner: null
    dates: null
    priority: null
    relations: []
  counts: {}
  direct_claims: []

derived:
  central_entity: ""
  branches:
    - key: ""
      label: ""
      summary: ""
      concepts: []
      evidence_refs: []

assessment:
  scale:
    min: 0
    max: 4
    caveat: "Heuristic assessment of source detail; not measured performance."
  dimensions:
    - label: ""
      score: 0
      rationale: ""
      evidence_refs: []
  gaps:
    - label: ""
      basis: "missing source field or operational definition"
      next_step: ""
```

## Evidence rules

- `facts` must be copied or normalized from retrieved source data.
- `derived` may reorganize source material but must not add unsupported claims.
- `assessment` is explicitly editorial and must include rationale.
- Null values remain null or render as “No definido”; never impute them.
- Counts must declare their unit and accessible scope.

## Dashboard copy rules

Prefer:

- “1 accessible page” over “Notion has 1 page”.
- “No owner assigned” over a guessed owner.
- “Definition grade: 2/4” over “40% complete”.
- “Suggested next step” over “Required action” unless the source itself mandates it.
