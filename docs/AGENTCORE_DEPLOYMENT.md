# AgentCore Deployment Path

## 1. What stays ours

These remain application/domain responsibilities:

- Intent
- clinical evidence workflow
- agent responsibilities
- state schema
- structured artifacts
- deterministic validation
- tests
- success criteria
- human decision boundary

## 2. What AgentCore can own

The managed AWS layer can increasingly own:

- runtime hosting
- deployment packaging
- scaling
- runtime endpoint
- IAM integration
- logs/traces
- later: identity, gateway/tool access, memory, registry

Start with **Runtime only**.

## 3. Prerequisites

Current AgentCore documentation uses the AgentCore CLI:

```bash
npm install -g @aws/agentcore
agentcore --version
```

Configure normal AWS credentials for the target account/region.

## 4. Create an AgentCore wrapper project

Do not delete or rewrite this repo.

Create a temporary AgentCore code-based Python project so the installed CLI generates the current supported structure.

Example:

```bash
agentcore create   --project-name ClinicalEvidenceCoordinator   --name ClinicalEvidenceAgent   --language Python   --framework Strands   --model-provider Bedrock   --memory none   --build CodeZip
```

Then compare that generated project with this repo.

The goal is to wrap:

```text
backend.app.orchestration.orchestrator.Orchestrator
```

not throw it away.

## 5. Local AgentCore test

After wiring the entry point:

```bash
agentcore dev
```

Exercise both sample packages.

## 6. Dry run

Before provisioning:

```bash
agentcore deploy --dry-run
```

Review what AgentCore/CDK plans to create.

Be able to explain:
- runtime
- IAM role
- Bedrock permissions
- logs/observability
- packaging

## 7. Deploy

When the dry run is understood:

```bash
agentcore deploy
agentcore status
```

## 8. Bedrock

The current v0.1 path works without an LLM.

Enable a real Bedrock provider after Runtime works.

Recommended split:

```text
LLM:
- interpret unstructured evidence
- summarize
- classify
- propose mappings
- surface uncertainty

Code/rules:
- required fields
- ID uniqueness
- allowed transitions
- completeness gates
- final readiness status
```

## 9. Add later only when justified

### Registry
For multiple agents/skills requiring discovery/catalog/governance.

### Gateway / MCP
For governed access to shared enterprise tools/APIs.

### Memory
Only when cross-turn/session memory creates actual value.

### Evaluations
As model behavior becomes a meaningful part of the workflow.

## 10. Enterprise scale

If asked “How does this become 100 agents?”:

```text
1 shared platform
N reusable skills
N shared MCP/API tools
a small number of orchestration patterns
many domain agent definitions
```

Not 100 copied platforms.
