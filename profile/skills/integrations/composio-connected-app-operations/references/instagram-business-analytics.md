# Instagram Business Analytics via Composio

Use this playbook for read-only verification, audience analysis, media analysis, and honest capability boundaries for connected Instagram Business or Creator accounts.

## 1. Verify live access

A toolkit listed as connected is not enough. Perform a harmless profile read:

```bash
composio search 'verify access to my Instagram account and read profile' --toolkits instagram --limit 10
composio tools info INSTAGRAM_GET_USER_INFO
composio execute INSTAGRAM_GET_USER_INFO -d '{"fields":"id,user_id,username,name,account_type,followers_count,follows_count,media_count","ig_user_id":"me","graph_api_version":"v21.0"}'
```

Report only fields actually returned. Confirm the username and `account_type`; analytics require an eligible Business or Creator account. Do not claim access from Gmail, Facebook, Meta Ads, or a merely connected toolkit.

## 2. Full follower rosters are not available

The official Instagram professional-account API exposes follower counts and aggregate audience insights, not a complete follower roster with usernames. Do not substitute:

- DM participants;
- commenters;
- likers;
- accounts found through search.

Those are interaction subsets, not followers.

If the user needs a person-level roster, direct them to Meta Accounts Center → Your information and permissions → Download your information → select the Instagram account → Followers and following → JSON. Analyze the user-supplied export as CSV/XLSX only after it is provided. Never use scraping, session cookies, or evasive browser automation.

## 3. Discover the current insight schema

```bash
composio tools info INSTAGRAM_GET_USER_INSIGHTS
```

Do not reuse metric names or periods from memory. Meta retires combinations. Current wrappers may describe date strings as acceptable while validating `since` and `until` strictly as Unix integer seconds; inspect the live schema and convert date boundaries explicitly.

Run incompatible metric classes separately. One failed broad request should be reduced to one metric or one breakdown per call.

### Demographics

Typical shape:

```json
{
  "metric": ["follower_demographics"],
  "period": "lifetime",
  "timeframe": "this_month",
  "metric_type": "total_value",
  "breakdown": "age",
  "ig_user_id": "<numeric IG user id>",
  "graph_api_version": "v21.0"
}
```

Repeat separately for `gender`, `country`, and `city`. Supported timeframes and breakdowns must come from the live schema. Sum returned demographic buckets and compare with `followers_count`; report coverage because Meta may suppress or omit part of the audience. Treat absent data as unavailable, not zero.

### Account activity

For a bounded interval, query compatible daily metrics such as:

- reach;
- accounts_engaged;
- total_interactions;
- likes, comments, shares, saves, replies;
- views and profile_views;
- website_clicks and profile_links_taps.

Use `period=day`, integer Unix timestamps, and the aggregation type required by the current schema. Preserve Meta's distinction between unique reach, non-unique views, and profile visits; do not create invalid funnel conversion rates from incompatible denominators.

### Growth and online followers

Query `follower_count`, `follows_and_unfollows`, and `online_followers` separately. Cross-check ambiguous breakdown labels against daily series before calling values gains or losses. A zero on the current or final day may mean the day is incomplete; do not describe it as an audience collapse without corroboration.

## 4. Content and niche analysis

Discover and execute `INSTAGRAM_GET_IG_USER_MEDIA` with a minimal field projection such as:

```json
{
  "ig_user_id": "me",
  "limit": 25,
  "fields": "id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count",
  "graph_api_version": "v21.0"
}
```

For larger analyses, paginate with `paging.cursors.after`. Never persist or echo `paging.next`, because it may contain tokenized query parameters.

A defensible niche workflow:

1. Cluster captions, hashtags, alt text, and visible media themes.
2. Separate content pillars from audience attributes.
3. Rank themes by comparable metrics and format.
4. Normalize for reach, age of post, paid promotion, and media type when those fields are available.
5. Label clusters as inferred themes, not facts about individual followers.
6. Never infer sensitive traits such as religion, health, ethnicity, sexuality, or political beliefs.

When only recent posts are sampled, say so and give the sample size. Likes/comments alone are directional; they do not prove the best niche without reach and per-media insights. Mention long posting gaps when interpreting low recent activity.

## 5. Reporting structure

Keep these layers distinct:

- **Returned facts:** account identity, counts, demographic buckets, dates, media metrics.
- **Derived calculations:** percentages, coverage, growth, engagement; calculate with a tool and show the denominator.
- **Inferences:** likely content pillars or positioning, explicitly labeled preliminary.
- **Recommendations:** experiments, posting cadence, formats, and measurement plan.

Useful outputs include audience geography, age/gender coverage, growth/churn, reach and engagement trends, format comparison, top content, inferred content niches, and a 30-day experiment plan. A dashboard is appropriate only after the source range, metric definitions, and coverage are documented.

## Safety

- Read-only profile and insight queries may proceed for an inventory request.
- Publishing, replying, messaging, deleting, or modifying profile/content requires explicit current-session authorization.
- Do not expose tokens, cursor URLs, connection IDs, or private media URLs.
- Do not claim a complete follower list from partial interaction data.