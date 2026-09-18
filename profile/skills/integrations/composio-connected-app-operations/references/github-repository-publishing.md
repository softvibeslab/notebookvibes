# Publishing a GitHub Repository Through Composio

Use this when the user explicitly authorizes publication to a GitHub repository, local `git push` cannot authenticate, and the connected GitHub toolkit is verified. This is a fallback transport, not a reason to bypass repository permissions or user approval.

## Workflow

1. **Sanitize before transport.** Build a publishable tree that excludes `.env`, auth stores, OAuth tokens, sessions, memories, logs, databases, cron outputs, caches, private IDs, and generated reports containing personal data. Prefer placeholders and `.env.example`.
2. **Verify the connected identity.** Execute a harmless identity tool such as `GITHUB_GET_THE_AUTHENTICATED_USER`; confirm it has access to the requested owner/repository.
3. **Discover live GitHub tools.** Run `composio search` for the intended operation and inspect schemas with `composio tools info`; tool slugs and inputs may change.
4. **Handle an empty repository specially.** Git Data APIs may fail before a first commit exists. Initialize one text file with `GITHUB_CREATE_OR_UPDATE_FILE_CONTENTS`; omit `branch` so GitHub uses the configured default branch.
5. **Commit the remaining tree atomically.** Use `GITHUB_COMMIT_MULTIPLE_FILES` with `branch=main`, `force=false`, and explicit author/committer information. Split large trees into roughly 30–60 files per batch to avoid payload and secondary-rate-limit problems.
6. **Treat tool JSON as the result.** Require `successful=true`, `error=null`, a full commit SHA, commit URL, and the expected `changed_paths`. A process exit code alone is insufficient.
7. **Verify independently.** Clone the public repository or query the repository/commit/tree APIs. Check default branch, head SHA, recursive tree file count, `truncated=false`, and compare the remote checkout against the sanitized local tree. Re-run focused tests from the fresh clone.
8. **Reconcile the local checkout if needed.** API commits create different history from a local root commit. Fetch the remote, compare tree SHAs, and only repoint the local branch when the trees are identical; never force-update blindly.

## CI Diagnosis When No Steps Ran

A workflow can fail before a runner starts, leaving an empty `steps` array and no downloadable job log. Query the check-run annotations endpoint. Account billing locks, policy blocks, and runner allocation failures appear there. Report these as infrastructure/account blockers, not code failures. Preserve local/fresh-clone test evidence but do not claim the canonical CI suite is green.

## Verification Checklist

- [ ] Exact destination and publication scope were explicitly authorized
- [ ] Connected GitHub identity was read and matched
- [ ] Secret/PII scan passed on the publishable tree
- [ ] Empty repository initialized through the Contents API when necessary
- [ ] Batch commits used `force=false`
- [ ] Every mutation returned a real commit SHA and URL
- [ ] Fresh clone or API tree matched expected files and bytes
- [ ] Focused tests ran from the remote checkout
- [ ] CI status and check-run annotations were inspected separately

## Pitfalls

- Do not interpret `git push` authentication failure as lack of GitHub access; a connected provider may be an authorized alternative.
- Do not use Git Data blob/tree creation to initialize an empty repository unless the live tool explicitly supports it.
- Do not retry an ambiguous commit blindly. Read branch HEAD/tree first and verify whether the intended paths already landed.
- Do not publish the live Hermes profile directory wholesale. Export a documented, sanitized representation instead.
- Do not hide CI failures by removing the workflow. Distinguish code failures from account/runner failures with annotations.
