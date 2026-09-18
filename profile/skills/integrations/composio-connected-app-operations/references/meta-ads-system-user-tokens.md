# Meta Ads system-user tokens for connected-app platforms

Use this reference when a hosted integration asks for a Meta Ads access token with `ads_read` and/or `ads_management`.

## Authority and freshness

Treat Meta's current system-user documentation as authoritative and re-check it before giving lifetime guarantees:

- System users overview: <https://developers.facebook.com/docs/business-management-apis/system-users>
- Install apps and generate tokens: <https://developers.facebook.com/docs/business-management-apis/system-users/install-apps-and-generate-tokens>

Integration copy may lag behind Meta. In particular, a form may request a “non-expiring” token while Meta recommends 60-day expiring tokens and may require expiration for some businesses. Describe this as a provider/integration mismatch, not as user error.

## Prerequisite graph

A usable server token requires more than selecting scopes:

1. A Meta Business Portfolio where the user is an administrator.
2. The target ad account owned by or shared with that portfolio.
3. A Meta developer app configured for the Marketing API.
4. The app added to or claimed by the same Business Portfolio.
5. A Business Manager system user.
6. The target ad account assigned to that system user with the task level needed.
7. A token generated for that app and system user with the required scopes.

Missing asset assignment can produce a syntactically valid token that still cannot access the ad account.

## UI workflow

1. Open Meta Business Settings → Users → System users.
2. Create a clearly named system user for the integration. Prefer a standard system user when sufficient; use admin only when the intended operations require it.
3. Assign the target ad account. Grant read/reporting tasks for analytics and campaign-management tasks only when writes are intended.
4. Under Accounts → Apps, add or claim the Meta developer app if it is not already attached to the portfolio.
5. On the system user, choose **Generate new token**, select the app, select an allowed lifetime, and request the minimum scopes.
6. For a Meta Ads integration that explicitly requires them, select `ads_read` and `ads_management`; add `business_management` only if account/business enumeration actually needs it.
7. Copy the token directly into the provider's HTTPS credential form.

Never ask the user to paste the token into chat, email, screenshots, logs, or a public URL. If exposed, revoke and regenerate it.

## Least privilege and action scope

- `ads_read` supports reporting and inspection.
- `ads_management` enables campaign mutations and is materially more sensitive.
- A toolkit demanding both scopes has write capability even if the current agent intends read-only use.
- Keep operational tools read-only until the user explicitly authorizes a campaign, budget, audience, or creative mutation.

## Lifetime handling

- If Meta offers a non-expiring system-user token and the integration requires it, the user may choose it after understanding the security trade-off.
- If Meta only offers or requires a 60-day token, use that token if the integration accepts it and record the need for rotation.
- Do not promise that a token “never expires” solely because the integration UI says so. Tokens can also become invalid when permissions, app status, business ownership, security policy, or the system user changes.

## Common blockers

- **System users menu absent:** wrong portfolio, insufficient admin role, or no eligible Business Portfolio.
- **App not listed:** app is not added/claimed by the portfolio or is owned elsewhere.
- **Scopes missing:** Marketing API setup/access, app role, business verification, or review requirements are incomplete.
- **Token works but ad account is invisible:** assign the ad-account asset and required tasks to the system user.
- **Integration rejects a 60-day token:** confirm its current requirements with the integration provider; do not invent a permanent-token workaround.

## Finding a tutorial video responsibly

When the user asks for a video:

1. Search YouTube for the exact workflow: `Meta Business system user Marketing API ads_read ads_management`.
2. Prefer a recent walkthrough that shows Business Settings, the system user, app selection, asset assignment, and token scopes.
3. Verify that the video is still publicly available using YouTube oEmbed or equivalent metadata.
4. Do not recommend a generic Graph API Explorer token video as if it generated a server/system-user token.
5. If transcript retrieval is unavailable, say that content-level verification was limited and describe why the title/workflow is relevant rather than claiming unseen steps.

## Verification after connection

Use a harmless read-only Meta Ads call to confirm:

- token authentication succeeds;
- the expected ad account is visible;
- `ads_read` works;
- no write is attempted without explicit user authorization.

A successful token submission screen alone is not end-to-end proof.