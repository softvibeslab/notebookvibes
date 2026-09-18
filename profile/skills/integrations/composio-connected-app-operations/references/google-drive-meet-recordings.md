# Google Drive and Google Meet Recording Discovery

Use this playbook when the user asks whether Drive is connected, requests files, or wants recordings associated with a client, project, or calendar meeting.

## Confirm live read access

1. Discover current tools:
   ```bash
   composio search 'verify Google Drive access and list recent files' --toolkits googledrive --limit 10
   ```
2. Call `GOOGLEDRIVE_GET_ABOUT` to verify the connected identity and actual Drive read access.
3. Call `GOOGLEDRIVE_FIND_FILE` with a small recent-file sample. A connected-toolkit label alone is not proof that file reads work.
4. Report only capabilities actually exercised. Do not claim write, share, or delete access from a successful read.

## Find Meet recordings reliably

Do not rely on a single broad video search. Recordings may live in shared-drive-backed or nested folders and may be named only with a Meet code and timestamp.

1. Search for likely containers:
   - folders named `Meet Recordings`
   - folders named `Google Meet`
   - project/client folders named by the user
2. Enumerate a folder with:
   ```text
   '<folder_id>' in parents and trashed = false
   ```
3. Recurse into child folders. Google Meet may create a date/code-named folder containing the actual MP4.
4. Follow every `nextPageToken`; do not stop after the first 100 items.
5. Request minimal useful fields: `id,name,mimeType,createdTime,modifiedTime,webViewLink,parents,size`.

## Composio large-response handling

When output is large, the CLI may return a wrapper instead of inline data:

```json
{
  "successful": true,
  "storedInFile": true,
  "outputFilePath": "/tmp/composio/.../OUTPUT.json"
}
```

Read and parse `outputFilePath`. Do not interpret the absence of inline `data.files` as an empty result.

## Correlate recordings with Calendar

When filenames do not include the client/project name:

1. Query Google Calendar for the project/client name across the relevant date range.
2. Use full event detail to extract:
   - event title and start/end in the calendar timezone;
   - `conferenceData.conferenceId`;
   - organizer and attendees when relevant.
3. Search Drive for each conference ID and for the event title.
4. Compare recording creation time with the meeting window, allowing time for recording finalization.
5. Classify results explicitly:
   - **Confirmed:** title or conference ID matches.
   - **Probable:** timestamp and surrounding evidence match, but no stable identifier does.
   - **Unconfirmed candidate:** merely close in time or generically named.
6. Do not relabel a nearby unrelated MP4 as the requested meeting. If only chat transcripts match, say that no recording MP4 was confirmed.

## Important limitations

- Meet recordings are commonly saved in the organizer's Drive. A meeting visible on the user's calendar does not prove its recording is in the user's Drive.
- A zero-result broad search is not proof of absence until known recording folders, nested children, pagination, shared-drive scope, and calendar correlation have been checked.
- Never download large MP4 files merely to identify them unless metadata and calendar correlation are insufficient and the user approves the heavier inspection.
