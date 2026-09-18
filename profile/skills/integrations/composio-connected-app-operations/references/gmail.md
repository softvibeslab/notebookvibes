# Gmail through Composio

## Read identity first

Before sending, run the profile tool (currently `GMAIL_GET_PROFILE`) and retain only the sender address needed for the operation. This prevents accidental use of the wrong connected Gmail account.

## Sending workflow

1. Discover the send tool with `composio search` and confirm its current schema.
2. Confirm the current user request identifies the final recipient and intended content. Infer a neutral subject only when the user delegated wording.
3. Send plain text unless HTML was requested.
4. Include `cc`, `bcc`, and `extra_recipients` only as empty arrays when required by schema.
5. Omit optional `attachment` and `from_email` fields unless they contain valid values. An empty attachment string can be treated as a filename and fail with `ENOENT`.
6. Execute the send exactly once and preserve `id`, `threadId`, and `display_url`.

## Verification

Use the fetch/search tool with a bounded query such as:

```text
in:sent to:<recipient> subject:(<subject>) newer_than:1d
```

Verify recipient, subject, `SENT` label, and the message ID returned by the send. A matching Sent result is stronger evidence than a CLI exit code alone.

## Retry discipline

Gmail send is non-idempotent. If the execution times out or returns an ambiguous transport error, search Sent before retrying. Retry only when provider evidence shows no message was created.

## Reporting

Return sender, recipient, subject, status, and message/thread ID. Do not expose OAuth or Composio connection credentials.
