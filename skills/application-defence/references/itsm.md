# Operator feedback and ITSM

Begin with a local operator summary and neutral findings: what changed, impact, application/environment, owner, action/due date, evidence and coverage health. Avoid creating tickets for unchanged observations.

## Destination setup

Record provider/tenant, authorized connection, service/configuration-item mapping, routing group, record types, priority/SLA policy, mandatory/custom fields, visibility, allowed transitions and sharing rules. A connection does not authorize every action. Credentials belong in an executor secret store or authenticated tool, not generated files.

Neutral records include stable application/environment/component/control and finding identity; severity and exposure/business context; timestamps/evidence; owner; remedy/retest; exception/expiry; run ID; delivery state and external record ID. Version the field mapping. This JSON is not a universal vendor import.

Route vulnerabilities through local remediation/vulnerability processes. Verified compromise or service-impact evidence may require incident handling; recurring causes can link problem records; production fixes can require change records. Follow the operator's process and approval authority. The agent cannot grant its own change approval.

## Delivery and reconciliation

Derive stable correlation from tenant, application, environment, component/control and normalized finding identity. Exclude mutable severity and run timestamps; retain advisory aliases. Persist correlation and external IDs. A trusted adapter needs atomic upsert/claim or serialized locking plus reconciliation; search-then-create alone can race.

Delivery states are `unsent`, `pending`, `delivered`, `failed`, `unknown_effect`. Delivered requires an observed response/record. After timeout following a write, reconcile by correlation/external ID before retrying. If success cannot be established, preserve unknown_effect for operator reconciliation. Never blindly repeat create. Bound retries and respect rate limits.

Use tenant-specific priority/field mappings. Redact before sending; prefer access-controlled evidence links over raw attachments and verify destination/visibility. Keep sensitive details internal where required. No raw source archives/logs/secrets by default. Ticket closure can trigger a retest but cannot resolve a finding without fresh target-specific evidence. Preserve operator edits and risk exceptions separately.

## Candidate providers

- [ServiceNow Table API](https://www.servicenow.com/docs/r/xanadu/api-reference/rest-apis/c_TableAPI.html) supports record operations under instance access controls. Verify actual release, tables/plugins and tenant process. This is a reference, not a shipped connector.
- [Jira Service Management request API](https://developer.atlassian.com/cloud/jira/service-desk/rest/api-group-request/) supports customer-request operations using service-desk/request-type fields and permissions. Incident/change/problem/Assets workflows need their own supported APIs and mapping; request creation alone does not establish these capabilities.

Official references consulted 30 October 2026. No API client is bundled. Before live delivery, inspect the available connector/API and test authentication/scope, required fields, visibility, duplicate events, timeout-after-write reconciliation, routing, status changes and read-back in an authorized test destination. Otherwise return the export/setup plan marked unsent and live integration unverified.
