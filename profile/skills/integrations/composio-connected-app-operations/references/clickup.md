# ClickUp via Composio

## Trigger

Use this playbook when inventorying or mutating a connected ClickUp workspace.

## Complete hierarchy discovery

1. Confirm `clickup` appears as `ACTIVE` in `composio connections list`.
2. Do not start with `CLICKUP_GET_TEAMS`: wrappers may define that action as a lookup requiring `team_id`, despite its name.
3. Discover authorized workspaces with:
   ```bash
   composio execute CLICKUP_GET_AUTHORIZED_TEAMS_WORKSPACES -d '{}'
   ```
   Fallback: discover and use `CLICKUP_AUTHORIZATION_GET_WORK_SPACE_LIST` if the primary tool is unavailable.
4. For each workspace/team ID, call `CLICKUP_GET_SPACES` with `archived:false`.
5. For every space, call both:
   - `CLICKUP_GET_FOLDERS` — folder responses may already embed their lists;
   - `CLICKUP_GET_FOLDERLESS_LISTS` — mandatory for complete coverage.
6. If folder objects do not include enough list detail, call `CLICKUP_GET_LISTS` for each folder.
7. Present the hierarchy as workspace → space → folder → list, including task counts when returned. Distinguish active from archived scope.

## Task reads

- Use `CLICKUP_GET_TASKS` per list and follow pagination until the provider indicates the final page.
- Hydrate selected items with `CLICKUP_GET_TASK` when status, priority, dates, assignees, or custom fields are incomplete.
- Treat missing private spaces/lists as a permission boundary, not proof that they do not exist.

## Safe task mutations

1. Read the task and its list first.
2. Read list metadata to obtain valid status strings.
3. For comments, scan existing comments to prevent duplicates.
4. Show the exact intended task/list, status, assignees, dates, description/comment, and follow-up tasks before executing.
5. Use `CLICKUP_UPDATE_TASK`, `CLICKUP_CREATE_TASK_COMMENT`, or `CLICKUP_CREATE_TASK` only after explicit approval.
6. Re-read the task or list and verify returned IDs/state after mutation.

## Pitfalls

- Task description updates may overwrite existing content; fetch and merge rather than blindly replacing.
- Comment creation has no general idempotency guarantee; dedupe before retrying after ambiguous failures.
- A list's `task_count` may omit subtasks or derived items; do not use it as the sole completeness check.
- An active toolkit connection proves authentication, not visibility into every private workspace object.
