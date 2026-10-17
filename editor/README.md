# CorBo Editor

Private editorial interface for the CorBo corpus.

## Security model

The public corpus remains a read-only GitHub Pages site under `docs/`. The editor is a separate server-side application and must **not** be deployed as part of GitHub Pages.

Authentication and authorization must be checked on the server. No GitHub token, OAuth secret, allow-list secret, or write credential belongs in this repository or in browser JavaScript.

## Editorial model

Canonical data flow:

`source → reviewed → derived corpus`

For Coqueiro, the canonical reviewed file is:

`CorBo_vNext/texts/coqueiro/coqueiro_parallel.tsv`

The files under `docs/data/` are derived publication artifacts and must never be edited as the canonical source.

## Editor workflow

1. Authenticate with GitHub.
2. Verify the authenticated GitHub account against a server-side allow-list.
3. Load a corpus unit by stable ID.
4. Display current Bororo and Portuguese text.
5. Enter proposed corrections.
6. Show the before/after diff.
7. Record the correction with stable ID, previous value, new value, timestamp, and authenticated editor.
8. Apply the correction to the canonical TSV through a controlled server-side GitHub operation.
9. Regenerate derived JSON through the existing corpus build process.
10. Publish only the regenerated read-only corpus.

## Initial scope

- Coqueiro
- Bororo and Portuguese fields
- stable-ID navigation
- original/current text comparison
- pending-change state
- audit history
- explicit save/confirm action

Later the same interface can support História Mítica and other CorBo collections without changing the public reader.

## Deployment

The editor requires a host with server-side functions and OAuth support. Deployment-specific credentials are configured only in that host's secret/environment settings. The public `docs/` site remains independent.

## Human-review interchange (experimental)

The public coverage dashboard (`docs/coverage.html`) can export and import a
`corbo-human-review-v1` JSON file. This is an **interchange file**, not a
canonical annotation and not a server-side editor write. The browser stores
its working copy in localStorage; exporting is required for durable backup.

Example:

```json
{
  "format": "corbo-human-review-v1",
  "exported_at": "2026-10-17T12:00:00Z",
  "reviews": {
    "example_sent_id": {
      "status": "pendente",
      "note": "Conferir dependência",
      "updated_at": "2026-10-17T12:00:00Z"
    }
  }
}
```

Statuses: `revisado` (human-reviewed) and `pendente` (requires attention).
An absent entry means unreviewed. The example ID above is illustrative only.

### Requirements before editor integration

1. Validate every `sent_id` against the current canonical CoNLL-U, not just
   the published derived JSON. Reject missing or ambiguous IDs.
2. Require an authenticated editor and preserve reviewer identity, timestamp,
   previous status and previous note in a versioned audit log.
3. Treat a browser-imported `revisado` status as **unverified provenance**:
   it must be explicitly confirmed by the authenticated reviewer before it
   counts as a verified human review.
4. Save a separate versioned review manifest, rather than rewriting CoNLL-U
   token rows or inserting unsupported review fields into MISC.
5. Detect concurrent edits and source changes; a review applies to a specific
   content version and must be reconfirmed if the sentence changes.
6. Regenerate publication indexes from canonical sources; never make the
   public dashboard a write endpoint.

**Current status:** the public browser import/export is implemented, but the
private editor does **not yet** ingest this manifest automatically. This
contract describes the required integration and avoids conflating local
checkboxes with verified annotations.
