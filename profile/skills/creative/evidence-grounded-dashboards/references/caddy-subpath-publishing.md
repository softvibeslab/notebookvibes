# Caddy Subpath Publishing

Use this when a dashboard must live under an existing HTTPS hostname while the root domain already reverse-proxies another application.

## Route pattern

Place the specific static route before the fallback handler:

```caddyfile
example.com {
    encode gzip zstd

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        -Server
    }

    handle_path /dashboards/strategy/* {
        root * /var/www/strategy-dashboard
        file_server
    }

    handle {
        reverse_proxy 127.0.0.1:8502
    }
}
```

`handle_path` strips the matched prefix. The fallback `handle` preserves the existing application for every other route.

## Deployment sequence

1. Validate the proposed standalone Caddy fragment.
2. Install the dashboard into a dedicated, root-owned read-only directory under `/var/www`.
3. Back up the existing site fragment with a timestamp.
4. Install or patch the site fragment.
5. Format the site fragment.
6. Validate the complete imported Caddy configuration.
7. Reload Caddy; do not restart unless reload is unsupported.
8. Fetch the dashboard URL and the pre-existing root/upstream URL.
9. Compare local and remote SHA-256 hashes.
10. Capture and inspect a screenshot from the public URL.

## Rollback

If the complete configuration fails validation, do not reload. Restore the backup fragment and validate again. If the static path returns an error after reload, restore the backup and reload Caddy.

## Security

- Never publish a dashboard containing tokens, private source IDs, internal hostnames, or confidential excerpts.
- Use restrictive headers compatible with the existing application.
- Avoid changing global headers or the fallback proxy when adding a static route.
- Keep the dashboard directory non-writable by the web-server process unless runtime writes are explicitly required.
