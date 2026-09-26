# AI Analysis: Is This the Template for Agents at Scale?

*Assessed 2026-09-26 against version 1 (initial commit). Update this file when the gaps below are closed.*

## Verdict

**The architecture is the right template. The model-call discipline is not finished yet.**

The shape to reuse for every future agent is already here: the orchestrator owns state, workers get minimal context, the model proposes and deterministic rules decide, and cloud code sits behind adapters. What still has to be built is the hygiene around calling a model: stop-reason handling, context-window limits, structured output, usage logging, evaluation, and isolating each run's files. Only one of the five agents calls a model today, so this gap is small now and would be large at 100 agents.

## What has been verified

| Claim | Evidence |
|---|---|
| Local workflow gives correct verdicts | 21 tests pass on a clean Python 3.12 install from `requirements.txt` |
| Upload page works end to end | Three PDF scenarios in `samples/scenarios/` run through the page in a browser and return the expected verdicts |
| Fails closed on bad model behavior | Tests cover malformed output, an invalid status, invented requirement IDs, and a provider exception; all return `NOT_READY_FOR_HUMAN_REVIEW` |
| AgentCore package is sound | `agentcore package` builds, and the zip serves `/ping` and `/invocations` correctly on Linux ARM64 / Python 3.12 |
| Real Bedrock error path | A live Bedrock call rejected by AWS was caught per document and the package was marked not ready |

**Not yet verified:** Claude's classification quality (model access is not enabled on the AWS account yet, so every test uses the keyword mock), and any real AWS deployment.

## What is right and should be kept

1. **State travels; agents do not remember.** `Orchestrator` (in `backend/app/orchestration/orchestrator.py`) owns `WorkflowState`. Each worker receives a hand-built context dict that matches its `permissions.read` list in `config/agents.yaml`. No worker sees conversation history or other workers' working notes.
2. **The model proposes; rules decide.** `DocumentIntakeAgent` only proposes evidence mappings. `validation/validator.py` alone sets the final status. It can only return `READY_FOR_HUMAN_REVIEW` or `NOT_READY_FOR_HUMAN_REVIEW`, and `human_review_required` is always true.
3. **Fail closed at every model boundary.** Unparseable output, an invalid field, an exception, or a document with no text all become "no requirements matched, status incomplete". Invented requirement IDs are deliberately passed through so `QualityAgent` blocks them visibly.
4. **Cloud dependencies are contained.** Only `agentcore_app.py` imports the AgentCore SDK, and only `providers/bedrock_provider.py` imports the Anthropic Bedrock client. The same workflow runs locally, in Docker, and in the AgentCore package.
5. **Every step leaves a structured record.** Each stage writes a JSON artifact, so a reviewer can trace the verdict.
6. **Stateless per request.** This fits AgentCore Runtime; no memory service is needed.

## Gaps

Four of the five agents (requirements, evidence, quality, review) are deterministic functions with no model. The model-related gaps apply to `DocumentIntakeAgent` and `BedrockProvider`.

### Model-call discipline

| Area | Current state | What good looks like |
|---|---|---|
| Stop reasons | `refusal` raises and fails closed. `max_tokens` truncation is not detected: it fails closed only because the cut-off JSON will not parse, and the error says "not JSON" instead of the real cause. Stop reasons are not logged. | Handle every stop reason explicitly (`end_turn`, `max_tokens`, `refusal`, and any others), record it on the artifact, and give each one a specific fail-closed reason. |
| Context window | The full extracted text of each PDF is sent with no size check. A long protocol could exceed the context window or cost far more than expected. | Count tokens before sending. Over a set budget, fail closed with "document too large for a single pass" (or chunk deliberately). Never truncate silently. |
| Output format | JSON is requested in the prompt and extracted with a regex. | Use the API's structured output (a JSON schema) where the platform supports it, and keep the shape validation as a second check. |
| Evidence provenance | The model gives a rationale but no quotes. A reviewer must open the PDF to check a match. | Require the model to quote the exact text that proves the match and the status (for example "Document status: FINAL - signed"), then check deterministically that the quote appears in the document. |
| Timeouts and retries | SDK defaults (10-minute timeout, 2 retries). | Set a per-call timeout that suits the workload, and record retries. |
| Usage and cost | Token usage is not recorded. | Log input/output tokens, model ID and latency per call on the run's artifacts. Required for cost control at scale. |
| Prompt-injection surface | The prompt says to treat document text as data. Text is wrapped in `<document>` tags, but a document containing `</document>` could break the framing, and the mock parser depends on those tags. | Escape or neutralize the delimiters, or pass documents as separate content blocks. |

### Context passed between steps

This is mostly sound. Each document is classified in its own call, and later steps receive structured summaries, not document text. Two things to trim before volume grows:

- `POST /api/review/documents` returns every intermediate artifact to the browser. Return the verdict, the coverage view and the per-document classifications, and keep the rest server-side.
- The full `evidence_items` list goes to three downstream steps. That's fine at 5 documents; at hundreds, pass only the fields each step's rule actually reads.

### Review and evaluation

- **Nothing checks the model's claims against the source.** `QualityAgent` checks the mapping's structure, and the validator checks completeness. Neither checks that the document really says what the model claims. Evidence quotes (above) close this.
- **No evaluation set.** Classification quality has never been measured with a real model. Build a small labeled set (the three scenarios plus tricky cases: an ambiguous title, a scanned PDF, a document that mentions a topic without being the required record, an embedded instruction) and track accuracy per model and prompt version.

### Structural issues that matter at scale

1. **Runs overwrite each other.** `ArtifactStore` writes fixed filenames (`requirements.json`, `document-intake.json`, and so on) into one directory, so concurrent runs on AgentCore would overwrite each other's audit trail. Key artifacts by `workflow_id`, then move them to the `ArtifactRepository` interface (for example S3) when deployed.
2. **Every agent is hand-wired.** `config/workflow.yaml` and `config/agents.yaml` describe the workflow, but no code reads them; the orchestrator is a fixed sequence in Python. At 100 agents this becomes 100 copies of the orchestration wiring.
3. **Human decision not captured.** The workflow stops at `READY_FOR_HUMAN_REVIEW`. There is no record of the reviewer's decision, which a regulated workflow will need.

## The model for 100 agents

Split what is built once from what each use case supplies.

**Shared platform, built once:**
- A model-call wrapper: stop-reason handling, token counting against a budget, structured output, timeouts, retries, and usage/cost logging, all failing closed.
- Evidence-quote verification.
- Per-run artifact storage behind `ArtifactRepository`.
- The runtime entry point (AgentCore adapter), the upload API and page, and the provider factory.
- A manifest loader that builds the orchestration from config.

**Per use case, kept small:**
- The requirements list.
- The intake prompt.
- The deterministic rules and validator checks.
- An evaluation set of labeled synthetic documents.
- A manifest that wires these together.

**The test for agent #2:** it should need no new orchestration or platform code, only config, a prompt, rules and evaluation data. If it needs more, the platform boundary is in the wrong place.

## Recommended order

| Step | Work | Needs AWS? |
|---|---|---|
| 1 | Harden the model call: explicit stop reasons, token budget check, structured output, evidence quotes with deterministic verification, timeouts, usage logging | No |
| 2 | Store artifacts per run (`workflow_id`) | No |
| 3 | Build the evaluation set; run Claude on it and record results | Yes: Bedrock model access |
| 4 | Deploy to AgentCore Runtime; accept documents through the runtime entry point; put a signed front door in front of the upload page | Yes |
| 5 | When agent #2 is built, extract the shared platform and drive orchestration from the manifest | No |

Step 5 is intentionally last: generalize from two real agents, not one.
