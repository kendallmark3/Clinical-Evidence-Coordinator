# Intent — Clinical Evidence Coordinator v0.1

## Intent

Create a small multi-agent application that reviews a **synthetic clinical-study evidence package** and determines whether the package is complete, internally consistent, traceable, and ready to be handed to a human reviewer.

The system is a reference implementation for multi-agent orchestration, not a medical decision system.

## Business Goal

Demonstrate an enterprise-relevant AI workflow that:

- coordinates specialized agents,
- preserves evidence provenance,
- produces structured artifacts,
- uses deterministic validation,
- fails closed on missing evidence,
- creates a human-readable review package,
- and can move from local development through GitHub Actions into a low-cost AWS deployment.

## Inputs

Primary input is one JSON study package containing:

- `study_id`
- `title`
- `protocol_requirements[]`
- `evidence_items[]`

Each requirement contains:
- requirement ID
- description
- whether evidence is required

Each evidence item contains:
- evidence ID
- evidence type
- source
- requirement IDs it claims to support
- status
- summary

Version one uses synthetic data only.

## Outputs

The workflow must emit:

- `requirements.json`
- `evidence-map.json`
- `quality-findings.json`
- `review-summary.json`
- `validation-result.json`
- `workflow-state.json`

Final machine status:

- `READY_FOR_HUMAN_REVIEW`
- `NOT_READY_FOR_HUMAN_REVIEW`

The workflow must never emit `APPROVED`, `SAFE`, `CLINICALLY_VALID`, or equivalent medical/regulatory conclusions.

## Agent Roles

### Requirements Agent

Goal:
Normalize the protocol requirements into a structured checklist.

Must not:
- invent requirements,
- change requirement meaning,
- approve evidence.

### Evidence Agent

Goal:
Map submitted evidence to protocol requirements.

Must return:
- matching evidence IDs,
- missing evidence,
- source references.

Must not:
- assume absent evidence exists,
- treat a summary as proof when no source exists.

### Quality Agent

Goal:
Identify package-quality problems.

Checks:
- missing required evidence,
- evidence marked incomplete,
- duplicate evidence IDs,
- unknown requirement references,
- inconsistent study IDs or metadata when present.

### Review Agent

Goal:
Prepare a concise handoff for a human reviewer.

Must:
- cite unresolved issues,
- summarize completeness,
- explicitly state human review is required.

Must not:
- make a medical or regulatory decision.

## Orchestration

Workflow order:

1. Requirements Agent
2. Evidence Agent
3. Quality Agent
4. Review Agent
5. Deterministic Validator

The orchestrator:
- creates workflow state,
- sends minimum sufficient context to each worker,
- validates each worker output,
- records artifacts,
- updates state,
- invokes the final deterministic validator.

## Deterministic Release Rules

`READY_FOR_HUMAN_REVIEW` only when all are true:

1. Every required requirement has at least one mapped evidence item.
2. No evidence item used for a required requirement has status `missing` or `incomplete`.
3. No evidence item references an unknown requirement.
4. Evidence IDs are unique.
5. No blocking quality finding exists.
6. Human review is still required.

Otherwise:

`NOT_READY_FOR_HUMAN_REVIEW`

## Success Criteria

### Functional

- Complete synthetic package returns `READY_FOR_HUMAN_REVIEW`.
- Missing required evidence returns `NOT_READY_FOR_HUMAN_REVIEW`.
- Unknown requirement references fail validation.
- Duplicate evidence IDs fail validation.
- Artifacts contain evidence IDs and requirement IDs.
- Output is deterministic in mock mode.

### Engineering

- `pytest` passes.
- App starts with FastAPI.
- Docker image builds.
- No credentials are required for mock mode.
- GitHub Actions runs compile and tests.
- Provider abstraction supports future Bedrock use.
- Terraform starter supports ECR + App Runner + S3 + DynamoDB.
- Secrets are not stored in source.

## Non-Goals

Version one does not:
- ingest PHI,
- connect to hospital systems,
- access production clinical data,
- perform diagnosis,
- evaluate treatment,
- determine medical-device safety,
- determine regulatory compliance or approval,
- autonomously submit anything to a regulator.

## First Demo

Run `samples/study-package-complete.json`.

Then run `samples/study-package-missing-evidence.json`.

The second run must fail closed and identify the missing requirement evidence.
