# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Claude Code Instructions — Clinical Evidence Coordinator / AgentCore Edition

## Commands

```bash
pip install -r requirements.txt                 # make install
python -m compileall backend && pytest -q       # make test (same as CI)
pytest backend/tests/test_workflow.py::test_missing_evidence_fails_closed -q   # single test
uvicorn backend.app.main:app --reload           # make run — API on :8000
make demo                                       # POST samples/study-package-complete.json to /api/review
python scripts/run_demo.py                      # run both samples in-process, no server
python scripts/make_synthetic_pdfs.py          # regenerate samples/documents/*.pdf and samples/scenarios/
```

`pytest.ini` sets `pythonpath = .`, so imports are always `backend.app...` from the repo root. Env vars (see `.env.example`): `PROVIDER_MODE` (default `mock`), `ARTIFACT_DIR`, `AWS_REGION`, `BEDROCK_MODEL_ID`. `backend/app/config.py` reads them once at import time.

## How the code works today

- **Upload page:** `frontend/index.html` is a single static file with no build step, served at `/` by `uvicorn backend.app.main:app`. It posts PDFs and requirements to `POST /api/review/documents`, which extracts text with pypdf (`backend/app/documents/pdf_text.py`) and calls `Orchestrator.run_documents()`.
- **Document intake:** `run_documents()` first runs `DocumentIntakeAgent`. For each document it sends the requirements and the text to a provider using `prompts/document_intake.md` (the only prompt file loaded at runtime). It turns the answers into `evidence_items`, then runs the normal `run()` pipeline. Any malformed provider output, exception, or empty text gives no requirements and `status: incomplete` (fail closed). Invented requirement IDs are passed through so `QualityAgent` blocks them.
- **Providers:** `providers/factory.get_provider()` chooses based on `PROVIDER_MODE`. `mock` is keyword matching and not AI; it reads the `<requirements>`/`<document>` tags in the intake prompt, so keep those tags if you change the prompt. `bedrock` uses the Anthropic SDK's `AnthropicBedrockMantle` with `BEDROCK_MODEL_ID` (default `anthropic.claude-opus-5`) and AWS credentials from the standard chain.
- **Pipeline:** `Orchestrator.run()` in `backend/app/orchestration/orchestrator.py` runs the steps in a fixed order: requirements → evidence → quality → review → `validation/validator.validate()`. It creates a `WorkflowState`, passes each worker a hand-built context dict, and saves each output with `ArtifactStore`, which writes JSON files to `ARTIFACT_DIR`.
- **Config files are not loaded at runtime:** `config/workflow.yaml`, `config/agents.yaml`, `agent-manifest.yaml` and every prompt except `prompts/document_intake.md` describe the design, but no code reads them. The context each worker gets in the orchestrator must match the `permissions.read` list in `agents.yaml`. If you change one, update the other.
- **The four original workers are plain Python with no LLM calls:** they implement `BaseAgent.run(context) -> dict`. Only `DocumentIntakeAgent` uses a provider.
- **Final status:** `validator.validate()` alone sets `status`. It returns `NOT_READY_FOR_HUMAN_REVIEW` if any required requirement has no evidence with `status == "complete"`, or if `QualityAgent` reported any `blocking` findings. `human_review_required` is always `True`. `ReviewResponse` in `models.py` restricts `status` to the two allowed values.
- **Runtime adapters:** `runtime/local_adapter.py` and `runtime/agentcore_adapter.py` both implement `platform/contracts.RuntimeAdapter` and just wrap `Orchestrator`. The AgentCore adapter writes artifacts to `/tmp/artifacts` by default. `test_runtime_adapters.py` checks that both adapters return the same domain result; keep that test passing. `platform/contracts.py` also defines `StateRepository`, `ArtifactRepository` and `ModelProvider`, which have no implementations yet.
- **AgentCore wiring:** `agentcore_app.py` at the repo root is the only module that imports `bedrock_agentcore`. It validates the payload against `StudyPackage` and calls `AgentCoreRuntimeAdapter`. `agentcore/agentcore.json` (created with the CLI via `agentcore add agent --type byo`) registers it with `codeLocation: "./"`, so the whole repo is zipped; the CLI leaves out `agentcore/`, `.venv` and `.env*`. The root `pyproject.toml` lists only the dependencies for the CodeZip package; local dev uses `requirements.txt`. Run it locally with `.venv/bin/python agentcore_app.py` (`/ping` and `/invocations` on `127.0.0.1:8080`), build with `agentcore package`, and plan a deploy with `agentcore deploy --dry-run`. `.github/workflows/agentcore-deploy.yml` is manual-only (`workflow_dispatch`).
- **Tests:** they use `samples/*.json` as fixtures and pass `tmp_path` as the artifact dir. To cover a new failure mode, change a copy of the complete sample, following the pattern in `test_workflow.py`.

## Objective

Take this repository from a local deterministic multi-agent workflow to a real AWS-hosted reference implementation using Amazon Bedrock AgentCore Runtime.

Preserve the domain architecture while adding cloud runtime capability.

## Non-negotiable architecture

**State travels. Agents do not remember.**

- The orchestrator owns workflow state.
- Workers receive minimum sufficient context.
- Worker outputs are structured artifacts.
- Deterministic validation remains the final machine gate.
- Human review remains mandatory.
- Provider/runtime dependencies stay behind adapters.

## Read first

1. `intents/Feature.md`
2. `config/workflow.yaml`
3. `config/agents.yaml`
4. `docs/PLATFORM_ARCHITECTURE.md`
5. `docs/AGENTCORE_DEPLOYMENT.md`
6. existing tests

## First target

Keep the local workflow green.

Then expose the existing orchestrator through an AgentCore-compatible code-based agent entry point.

Do **not** rewrite the four clinical workers simply to fit a framework.

## AgentCore strategy

Use the current AWS AgentCore CLI workflow.

Preferred path:

```bash
npm install -g @aws/agentcore
agentcore --version
```

Use a **code-based Python agent**.

When creating the AgentCore wrapper, prefer:
- Python 3.12+
- Bedrock model provider
- CodeZip initially
- no memory initially
- no Gateway initially
- no Registry dependency initially
- no MCP dependency initially

The first cloud milestone is:

```text
AgentCore Runtime
    |
existing ClinicalEvidence Orchestrator
    |
Bedrock provider (when enabled)
    |
deterministic validator
    |
structured result
```

## Do not overbuild

Do not add these merely because they exist:

- Kubernetes
- EKS
- Step Functions
- Redis
- NAT Gateway
- multi-AZ RDS
- service mesh
- dozens of Lambda functions
- one microservice per agent

## Cloud-neutral boundary

Business/domain modules must not import AgentCore SDK/runtime code directly.

Target dependency direction:

```text
domain/orchestration
       ↑
platform interfaces
       ↑
AWS AgentCore adapter
```

## Verification gate

Before declaring any implementation step complete:

```bash
python -m compileall backend
pytest -q
```

For AgentCore work also verify, where applicable:

```bash
agentcore deploy --dry-run
agentcore status
```

Never claim successful AWS deployment unless it actually succeeds in the user's environment.

## Safety boundary

Synthetic data only.

Never add:
- PHI
- diagnosis logic
- treatment advice
- clinical safety approval
- autonomous regulatory decisions

Allowed machine statuses:

- `READY_FOR_HUMAN_REVIEW`
- `NOT_READY_FOR_HUMAN_REVIEW`
