# Recruitment Integration Requirements

This document tells colleagues exactly what must be registered for each recruitment provider before the Flexus `Researcher` bot can use the integration.

Rules:
- Credentials belong in the runtime secret store or environment, not in bot setup fields.
- Reusable IDs may be passed per call unless stated otherwise.
- If a provider requires commercial approval, do that first. Do not ask engineering to debug a provider that has not granted API access yet.

## 1. Prolific

- Access model: self-serve API token for researcher accounts.
- Required credentials:
  - `PROLIFIC_API_TOKEN`
- Where to get it:
  - Prolific researcher workspace API settings.
- Where to register it:
  - runtime environment or secret manager used by the Flexus deployment.
- Required approvals:
  - none beyond having a Prolific researcher account with API access enabled.
- Runtime IDs often needed:
  - `study_id`
  - `participant_group_id`
  - `submission_id`
  - `webhook_id`
- Notes:
  - Use participant groups for allowlists and blocklists.
  - Prefer webhooks over polling when inbound webhook delivery is available.

## 2. Cint

- Access model: enterprise bearer API key for Exchange Demand API.
- Required credentials:
  - `CINT_API_KEY`
- Optional runtime configuration:
  - `CINT_API_VERSION`
- Optional but recommended request discipline:
  - `Idempotency-Key` on POST calls to protect against duplicate project / target-group / fielding operations during retries
- Where to get it:
  - from Cint account team / developer onboarding and the API Starter Kit issued during integration onboarding.
- Where to register it:
  - runtime environment or secret manager.
- Required approvals:
  - enterprise API access approved by Cint
  - dedicated `Integration Consultant` assigned by Cint
  - test / onboarding environment access
  - production go-live approval
- Required organizational context:
  - `account_id`
  - available `business_unit_id` values
  - available `project_manager_id` or account users used for target-group ownership
  - service clients if the account routes through them
- Runtime IDs often needed:
  - `account_id`
  - `project_id`
  - `target_group_id`
  - `business_unit_id`
  - `profile_id`
  - user identifiers for business-unit discovery
- Notes:
  - Cint account discovery is part of the integration surface: account listing, account users, service clients, and user business units.
  - Fielding launch is async.
  - Quota distribution and feasibility should be checked before scaling.
  - Supplier-level quota distribution should be used before launch for harder quota structures.
  - Price retrieval and price prediction can require `Private Exchange`; if not enabled, those methods may return `403`.
  - To get real end-to-end value from the full surface, colleagues must ensure the account has all needed demand capabilities enabled, not just a JWT token.

## 3. MTurk

- Access model: AWS SigV4 request signing.
- Required credentials:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
- Optional credentials:
  - `AWS_SESSION_TOKEN`
- Optional runtime configuration:
  - `MTURK_SANDBOX=true`
- Where to get them:
  - AWS account used for MTurk Requester access.
- Where to register them:
  - runtime environment or secret manager.
- Required approvals:
  - MTurk requester account in good standing.
- Runtime IDs often needed:
  - `hit_id`
  - `assignment_id`
  - `qualification_type_id`
  - `worker_id`
  - `hit_type_id`
- Notes:
  - Sandbox should be used for dry runs before real spend.
  - Qualification and notification setup is not optional if quality matters.

## 4. UserTesting

- Access model: reviewed bearer token after enterprise API approval.
- Required credentials after approval:
  - `USERTESTING_ACCESS_TOKEN`
- Optional app-registration values:
  - `USERTESTING_CLIENT_ID`
  - `USERTESTING_CLIENT_SECRET`
- Where to get them:
  - UserTesting developer portal after the API team approves the app.
- Where to register them:
  - runtime environment or secret manager.
- Required approvals:
  - enterprise plan
  - developer app review / approval
- Runtime IDs often needed:
  - `test_id`
  - `session_id`
- Notes:
  - Current Flexus integration is results-focused.
  - If the business wants programmatic test creation later, provide the exact approved API docs first.

## 5. User Interviews

- Access model: bearer API key for Research Hub API surface.
- Required credentials:
  - `USERINTERVIEWS_API_KEY`
- Where to get it:
  - User Interviews account / API onboarding for Hub integrations.
- Where to register it:
  - runtime environment or secret manager.
- Required approvals:
  - API-enabled User Interviews account.
- Runtime IDs often needed:
  - `participant_id`
- Notes:
  - Current public Flexus surface is participant profile management.
  - If project or invite APIs are desired, the exact public docs must be supplied first.

## 6. Respondent

- Access model: partner API key + secret.
- Required credentials:
  - `RESPONDENT_API_KEY`
  - `RESPONDENT_API_SECRET`
- Where to get them:
  - Respondent partner onboarding after staging review.
- Where to register them:
  - runtime environment or secret manager.
- Required approvals:
  - staging implementation review
  - production credentials approval
  - signed MSA with Respondent
- Runtime IDs often needed:
  - `organization_id`
  - `team_id`
  - `researcher_id`
  - `project_id`
  - `screener_response_id`
- Notes:
  - Production approval requires proving project creation, response handling, invite, attended, reject, and report flows.
  - Moderated studies also need scheduling and messaging mechanisms in place.

## 7. PureSpectrum

- Access model: enterprise access-token header for Buy API.
- Required credentials:
  - `PURESPECTRUM_ACCESS_TOKEN`
- Optional runtime configuration:
  - `PURESPECTRUM_ENV=staging`
- Where to get it:
  - PureSpectrum product or support team.
- Where to register it:
  - runtime environment or secret manager.
- Required approvals:
  - enterprise API access / buyer account setup.
- Runtime IDs often needed:
  - `survey_id`
  - supplier and traffic-channel identifiers if the account uses them
- Notes:
  - Survey creation normally needs category, localization, IR, LOI, live URL, and field time.
  - Use staging during onboarding.

## 8. Dynata

- Access model: split by API family.
- Demand API required values:
  - `DYNATA_DEMAND_API_KEY`
  - `DYNATA_DEMAND_BASE_URL`
- REX required values:
  - `DYNATA_REX_ACCESS_KEY`
  - `DYNATA_REX_SECRET_KEY`
  - `DYNATA_REX_BASE_URL`
- Where to get them:
  - Dynata account manager / developer onboarding.
- Where to register them:
  - runtime environment or secret manager.
- Required approvals:
  - Demand API and REX onboarding as needed by the business workflow.
- Runtime IDs often needed:
  - `project_id`
  - `quota_cell_id`
  - `respondent_id`
- Notes:
  - Demand and REX are separate products. Do not assume one credential set unlocks both.
  - Base URLs are explicitly stored as config because Dynata supplies them during onboarding.

## 9. Lucid Marketplace

- Access model: consultant-led API key provisioning.
- Required credentials:
  - `LUCID_API_KEY`
- Optional runtime configuration:
  - `LUCID_ENV=sandbox`
- Where to get it:
  - Lucid / Cint Marketplace consultant onboarding.
- Where to register it:
  - runtime environment or secret manager.
- Required approvals:
  - marketplace account setup
  - environment access from integrations team
  - consultant-provided Demand API guide or Postman collection
- Runtime IDs often needed:
  - project and quota identifiers from the consultant-provided API contract
- Notes:
  - Publicly fetchable docs confirm auth and environment model but not the full demand endpoint map.
  - Before asking engineering for deeper Lucid support, provide the sanctioned Postman collection.

## 10. Toloka

- Access model: ApiKey header.
- Required credentials:
  - `TOLOKA_API_KEY`
- Optional runtime configuration:
  - `TOLOKA_ENV=sandbox`
- Where to get it:
  - Toloka requester account API settings.
- Where to register it:
  - runtime environment or secret manager.
- Required approvals:
  - requester account with API access.
- Runtime IDs often needed:
  - `project_id`
  - `pool_id`
  - `assignment_id`
- Notes:
  - Use sandbox for early dry runs.
  - Pool, task, and webhook settings should be validated before live worker spend.
