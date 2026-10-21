# Private visual book deployment

The application code may live in the public repository. The catalog, answer keys,
teacher basis, provenance records and private image bytes must not be committed
there, including in earlier commits on a branch. The private data directories are
ignored. Use a branch based on the production source without private-content
commits in its ancestry.

## Private storage

Use a private S3-compatible bucket in the existing Railway project. No public ACL,
public bucket policy or browser-accessible signed URL is needed. Only the backend
fetches objects. Existing public learner resources retain their current delivery.

The server uses these environment variables:

| Variable | Purpose |
| --- | --- |
| `PRIVATE_BOOK_ENABLED` | Feature switch; disabled unless explicitly enabled |
| `PRIVATE_BOOK_REVIEWER_IDS` | Persisted account IDs permitted to review; initially only Michael |
| `PRIVATE_BOOK_S3_ENDPOINT` | HTTPS storage endpoint |
| `PRIVATE_BOOK_S3_REGION` | S3 signing region |
| `PRIVATE_BOOK_S3_BUCKET` | Private S3 bucket name |
| `PRIVATE_BOOK_S3_ACCESS_KEY_ID` | Server-only storage credential reference |
| `PRIVATE_BOOK_S3_SECRET_ACCESS_KEY` | Server-only storage credential reference |
| `PRIVATE_BOOK_CATALOG_SHA256` | Full digest pinning the deployed catalog |
| `PRIVATE_BOOK_BASIS_SHA256` | Full digest pinning the teacher overrides |

Prefer Railway bucket variable references for credentials. Never include their
rendered values in logs, commits, reports or browser payloads.

Before upload, run `backend/scripts/upload_private_book.py --content-root <private-backend-directory> --dry-run`.
The uploader validates every image before any write. Run the same command without
`--dry-run` only with the intended private bucket configured. It creates immutable
content-addressed images and release documents, verifies downloaded bytes after
writing, and refuses different existing bytes. Identical objects are reused.
Uploading does not activate a catalog, approve candidates or open learner access.

After successful upload, configure the digest pins and account permission, deploy
the code, and verify the running deployment. The application starts safely without
private content. Authorized preview requests return 503 if content is unavailable;
guests and other accounts remain denied before any private storage read.

## Required production checks

Open `/api/book-preview/enter` using Michael's existing web login. Verify the book,
navigation, image proportions, selected language, answer and teacher explanation.
Check guest and other-account denial for view, catalog, images and attempts.
Direct storage URLs must also reject anonymous reads. Record deployment ID,
code commit, catalog digest, counts, missing images and the actual checks performed.
Do not call a local mock test an authenticated production test.

To disable: set `PRIVATE_BOOK_ENABLED=0` and apply that configuration through the
existing Railway deployment process. Verify protected routes return 404. Existing
public learner content is independent of this switch. Rollback uses the previously
healthy Railway deployment; never roll back by deleting source content.

## Current limitation

This preview does not implement student publication. A later release-control step
must bind explicit approval to exact lesson versions and preserve existing access
and premium rules before any learner opening. Do not interpret upload, a valid
hash, a candidate image or a private review as publication approval.
