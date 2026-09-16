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
