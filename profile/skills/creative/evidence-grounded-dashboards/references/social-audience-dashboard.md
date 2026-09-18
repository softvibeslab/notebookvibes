# Social Audience Dashboard Workflow

Use this reference when building a dashboard from an authorized Instagram/Meta connection and delivering it through Google Drive or another file surface.

## 1. Prove the connection before analysis

Do not infer Instagram access from Meta Ads, Facebook, Gmail, or another connected toolkit. Execute a read-only profile call and confirm only the fields actually returned:

- username and account name;
- professional account type (Business or Creator);
- follower, following, and media counters;
- managed-account identity.

Stop on an unexpected identity, 401/403, expired token, or missing professional-account context.

## 2. Extract into four evidence layers

Keep these separate in both the data file and the visual design:

1. **Account facts:** profile type and counters.
2. **Aggregate audience facts:** age, gender, country, city, growth, reach, views, profile activity.
3. **Content facts:** media type, timestamp, caption, permalink, and returned engagement fields.
4. **Editorial inference:** topic clusters, niche hypotheses, positioning, and experiments.

Never label a person as belonging to a niche. A niche is an inference about content themes and aggregate response, not a follower attribute.

## 3. Meta/Instagram query discipline

- Demographic metrics usually need `period=lifetime`, `metric_type=total_value`, and a supported `timeframe` such as `this_month` or `this_week`.
- Request one demographic breakdown per call (`age`, `gender`, `country`, or `city`) when mixed breakdowns are rejected or omitted.
- Some wrappers describe `since` and `until` as accepting dates but validate them as integer Unix timestamps. Inspect the live schema and send integers when required.
- Fetch general activity separately from demographics because valid period/metric combinations differ.
- Treat an empty metric as unavailable for that window, not as zero.
- Record the timezone used to construct reporting-window timestamps.
- Paginate media with cursors, cap the pull intentionally, and never persist or expose tokenized `paging.next` URLs.

## 4. Coverage and interpretation rules

- Sum demographic buckets and compare the result with the current follower count. Show both the covered count and coverage percentage.
- Explain that platform thresholds can suppress small cities or cohorts.
- Do not combine unique reach, non-unique profile visits, views, and interactions into a conversion funnel unless their definitions make the calculation valid.
- Show raw counts when denominators are incompatible.
- Distinguish daily follower gains from total follower count; validate follow/unfollow labels against the provider description before computing net growth.
- Rank posts by visible engagement only when per-post reach is unavailable, and label the ranking as unnormalized.
- If the latest available post is old, surface inactivity as a likely explanation for low recent activity, clearly as an interpretation.

## 5. Knowledge-base bundle

Create a portable bundle before any remote write:

- `index.html` — self-contained responsive dashboard;
- `README.md` — narrative knowledge base and methodology;
- `instagram_data.json` — consolidated source data without credentials or paging URLs;
- `audience_metrics.csv` — normalized aggregate rows;
- `recent_media_sample.csv` — bounded content sample;
- `VERIFICATION.md` — checks, evidence limits, and visual audit;
- desktop and mobile screenshots.

The dashboard should identify reporting boundaries and visibly separate facts from inferences.

## 6. Verification

At minimum:

1. parse HTML and count expected panels, branches, links, and tables;
2. extract raw JavaScript and run a syntax check;
3. serve locally and require HTTP 200 plus `text/html`;
4. test at least one interaction;
5. capture desktop and mobile screenshots;
6. verify `scrollWidth <= innerWidth` at both viewports;
7. inspect browser console errors;
8. run the anti-slop audit;
9. inspect screenshots for clipping, overlap, tiny labels, and misleading chart proportions.

When using line-numbered file-reading tools, do not feed their decorated output into HTML or JavaScript parsers. Validate the raw file bytes instead.

## 7. Drive delivery as a transaction

1. Build and verify every local artifact first.
2. Create the destination folder and retain its returned ID and view link.
3. Verify the folder by ID or an exact-name query.
4. Upload one small canary artifact first.
5. If the canary succeeds, upload the remaining files.
6. Verify each uploaded file's parent folder, MIME type, size, and view link.
7. Only then report the Drive delivery as complete.

### Storage-quota fallback

If upload returns `403` because Drive storage quota is exceeded:

- stop subsequent uploads rather than producing repeated failures;
- do not delete user files or empty trash without explicit authorization;
- state precisely that the folder exists but its contents were not uploaded;
- preserve the verified local bundle;
- package it for an alternate delivery surface when available;
- resume upload after the user frees space, then verify every parent/file relationship.

Do not publicly publish private audience analytics merely to bypass Drive storage. Public hosting requires an explicit privacy decision.

## 8. Privacy boundaries

- Do not claim or manufacture a full follower identity list; the professional API generally exposes aggregate counts and insights, not a complete roster.
- Do not infer sensitive traits about individuals.
- Strip account IDs, access tokens, private media URLs, cursor URLs, and integration logs from public artifacts.
- Use only user-facing permalinks when a content link is necessary.
