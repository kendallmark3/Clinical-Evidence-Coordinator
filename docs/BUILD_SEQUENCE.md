# Build Sequence

## Session 1 — Understand and preserve the workflow

- [ ] Read `Intent.md`, workflow config, agent config.
- [ ] Run all tests.
- [ ] Run complete sample.
- [ ] Run missing-evidence sample.
- [ ] Trace state through all four agents.
- [ ] Explain why the deterministic validator owns final machine status.
- [ ] Draw the domain/platform boundary.

## Session 2 — AgentCore runtime

- [ ] Install current AgentCore CLI.
- [ ] Create a disposable code-based Python AgentCore sample.
- [ ] Compare its generated entry point/config with this repo.
- [ ] Add an AgentCore adapter/entry point without rewriting domain agents.
- [ ] Run `agentcore dev`.
- [ ] Preserve existing local tests.
- [ ] Run `agentcore deploy --dry-run`.
- [ ] Review IAM/runtime/logging resources.
- [ ] Deploy only after the dry run is understood.
- [ ] Invoke the deployed runtime.
- [ ] Inspect logs/traces.

## Session 3 — Real model path

- [ ] Enable Bedrock provider.
- [ ] Give the model one bounded task first.
- [ ] Capture structured response.
- [ ] Add evaluation fixture.
- [ ] Keep deterministic validator unchanged.
- [ ] Measure model usage/cost.

## Session 4 — Enterprise platform extraction

- [ ] Identify duplicated platform code.
- [ ] Move reusable interfaces into `platform/`.
- [ ] Define a reusable agent manifest.
- [ ] Sketch agent #2 without copying orchestration plumbing.
- [ ] Decide what belongs in Registry.
- [ ] Decide what should become an MCP/Gateway tool.

## Be able to explain

- Why an agent is not the same as a microservice.
- Why 100 use cases do not imply 100 unique platforms.
- How shared skills reduce duplication.
- How AgentCore differs from the business workflow.
- How the same domain workflow could map to Azure/Google later.
- Where model judgment ends and deterministic validation begins.
