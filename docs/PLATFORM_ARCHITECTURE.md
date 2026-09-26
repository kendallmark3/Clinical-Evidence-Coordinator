# Platform Architecture — Avoiding 100 Snowflake Agents

## Principle

Build **domain agents on a shared agent platform**.

## Layering

```text
DOMAIN REPO
------------------------------------------------
Intent
Workflow
Domain agents
Prompts
Schemas
Domain validation
Domain tests
Synthetic fixtures

SHARED AGENT PLATFORM
------------------------------------------------
Runtime interface
Model provider interface
State interface
Tool/MCP interface
Telemetry interface
Identity interface
Evaluation hooks
Common error/retry policy
CI/CD templates

CLOUD ADAPTERS
------------------------------------------------
AWS AgentCore / Bedrock
Azure equivalent
Google equivalent
```

## Dependency rule

Domain code depends on platform interfaces.

Cloud adapters implement platform interfaces.

## Reusable after agent #1

Likely candidates:

- runtime invocation contract
- provider interface
- structured artifact envelope
- workflow state envelope
- logging/tracing correlation IDs
- tool permission model
- validation result envelope
- evaluation hooks
- deployment templates
- GitHub Actions reusable workflow

## Remains domain-specific

- clinical evidence intent
- requirements semantics
- evidence mapping rules
- domain prompts
- domain schemas
- domain success criteria
- domain fixtures/tests

## DRY test

Before creating agent #2, ask:

> Which files would I copy?

Anything copied unchanged probably belongs in the shared platform.
