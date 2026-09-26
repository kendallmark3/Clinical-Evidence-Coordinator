# Upload scenarios

Synthetic PDFs grouped for the upload page. Select every file in one folder, keep the default requirements, and click **Review package**.

| Folder | Expected result |
|---|---|
| `1-ready/` | Ready for human review. The parking memo matches nothing. |
| `2-missing-adverse-event/` | Not ready. REQ-003 has no evidence. |
| `3-draft-adverse-event/` | Not ready. The adverse event record is a draft, so it counts as incomplete. |

Regenerate the source PDFs with `python scripts/make_synthetic_pdfs.py`.
