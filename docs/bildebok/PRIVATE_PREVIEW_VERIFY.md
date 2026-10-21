# Private preview verification – 2026-10-21

Status: implemented and locally tested; not deployed, not tested through Michael's
production session, not open to learners. Railway's platform incident currently
prevents provisioning and deployments. This report does not claim completion of
the full book objective.

Code-only branch: `feat/private-book-code-20261021`, based on production commit
`5caceb1b98b5c365c2cfe45014967d95bbbea654`. Tests below cover the uncommitted code
snapshot; record the resulting commit and deployment before claiming live delivery.

## Code-only regression run

```powershell
D:/thai2drive-main/work/thai2drive/.venv/Scripts/python.exe -m pytest backend/tests/test_private_book_access.py backend/tests/test_private_book_storage.py backend/tests/test_private_book_upload.py backend/tests/test_private_book_completion.py backend/tests/test_studybook_web.py backend/tests/test_webapp_lang_routes.py backend/tests/test_sign_catalog.py -q -p no:cacheprovider
```

Result: 155 passed, 4 subtests passed, two existing dependency/deprecation warnings.
Tests use synthetic data. They cover denied access before private storage reads,
answer and teacher-field omission, missing-storage failure, immutable storage
hashes, corrupt/oversized responses, upload conflict refusal and bounded model
calls. They do not prove a real S3 service or a real authenticated production flow.

A separate read-only security review found no concrete code-deploy blocker. Its
upload/delivery validation mismatch was fixed by sharing image-name and size
limits, with rejection tests for unsupported extensions and oversized inputs.

## Private release dry-run

```powershell
D:/thai2drive-main/work/thai2drive/.venv/Scripts/python.exe backend/scripts/upload_private_book.py --content-root ../private-book-preview-20261021/backend --dry-run
```

Validated: 152 rows, 151 image files, 154 total objects including the catalog,
teacher overrides and provenance. All image bytes matched full catalog SHA256.
No object was uploaded and no release was activated by this command.

Catalog SHA256: `1d24a890b5bad9302ed55e7c8ca9be4cfc6abcf8237e5489fc0722c2ee083a2c`.
Teacher overrides SHA256: `28809c94524585250aa08a683474526317f730e1afe0d359f8a1caf30c6405a5`.

The separate private working copy previously passed access/attempt tests using a
real local MongoDB, six local responsive/language browser flows, and three bounded
real model calls for one lesson. Those results predate the remote storage adapter
and do not substitute for testing that adapter against the provisioned bucket.

## Before live delivery

Provision and verify private storage; verify anonymous bucket access is denied;
upload and verify immutable objects; pin the release and account allowlist;
review and commit only public-safe code; push and deploy from the current
production base. Verify runtime version, Michael access, guest/other-account
denial, protected resources and actual book flow. Provide the private URL and
copyable Argus control message only with accurately labelled evidence.
