# Architecture Notes

## Logical pattern

```text
Intent
  |
Orchestrator
  |
  +--> Requirements Agent
  +--> Evidence Agent
  +--> Quality Agent
  +--> Review Agent
  |
Explicit Shared State
  |
Deterministic Validator
  |
Human Review
```

## Why one container first?

The orchestration pattern does not require microservices.

Version one keeps:
- API
- orchestrator
- agents
- state manager
- validator

inside one deployable container.

This proves the workflow before introducing infrastructure complexity.

## Upgrade path

Only split components when evidence supports the need.

Possible triggers:

- long-running tasks -> SQS worker
- high concurrency -> horizontally scaled workers
- durable run state -> DynamoDB / PostgreSQL
- large documents -> S3
- enterprise ingress -> API Gateway / ALB / WAF
- cross-team reuse -> shared agent/platform services
- regulated production -> stronger identity, network isolation, audit, observability

The logical agent pattern remains the same.
