# A1: legacy campaign containment

The anonymous `POST /api/campaign/register` is permanently retired. It returns
HTTP 410 with `error=campaign_closed` and performs no database operation.
`GET /api/campaign/status` retains historical counts but always returns
`is_active=false`. `remaining` is historical arithmetic, not an available offer.
The web campaign banner and form are removed; compatibility handlers are inert.
Cached older clients are blocked at the server even before they reload the UI.

## Preserved second mechanism

Normal `/api/auth/signup` is unchanged. It initializes the old `signup_50`
counter from all existing users if absent, then increments it for each signup.
Non-admin positions at or below 50 receive a 30-day trial immediately on signup,
without email confirmation or a campaign start date. Admin positions also advance
the counter; a failed insert can consume a position. This is the OLD mechanism,
not activation of the newly approved campaign. Do not reset or reuse its counter.
Existing access, trials, paid entitlements and learning history are untouched.

## Read-only historical audit (A2)

`backend/scripts/audit_campaign_legacy.py` reads the configured production DB
without importing the server or invoking startup/index creation. It emits only
aggregate counts, index metadata and numeric counter state. It performs no writes.
Supply MONGO_URL and DB_NAME securely via the existing Railway environment; never
print variables or put connection strings in the command line. Results belong in
a local audit report, not the public repository. Reads are not a transactionally
consistent snapshot. Payment provenance and household identity are not inferred.

## Safe recovery / future changes

Do NOT revert this patch or redeploy a version predating it: that would restore
unauthenticated account writes. Recover by rolling forward while preserving the
410 tombstone and inactive status. After a known-good deployment, that deployment
is the minimum rollback baseline. A future campaign must use a separate verified
account activation path. Disabling future enrollment must preserve already granted
access and all audit history. Never delete documents or reset counters as rollback.
A3–A5 and launch remain unapproved pending historical review and an updated plan.
The owner's existing account is excluded from the future new-student cohort;
no existing account or child is inferred or altered by this patch.

## Verification

Run the campaign containment, unchanged signup boundary and aggregate-output
Python tests, and `node tests/test_campaign_containment_runtime.cjs`.
Independent Argus verification should confirm the live commit, 410 on a POST
with an empty body (never real contact details), historical inactive status,
absence of banner/form on NO/TH/EN web routes, normal signup code preservation,
and no changes to mobile or billing. Do not test unsafe old behavior in production.
