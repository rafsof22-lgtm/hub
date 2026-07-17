# Hybrid LLM Router Architecture

Last updated: 2026-07-17

Status: architecture guidance and implementation backlog only. This file does not replace the ChatGPT Agent core model, does not configure provider secrets, and does not prove a live router deployment.

## Recommended Architecture

Use ChatGPT Agent as the orchestrator and cheaper LLMs as workers.

```text
ChatGPT Agent -> Universal Router -> GPT-5 / DeepSeek / Kimi / Qwen / Local Llama / OCR-vision workers
```

Recommended model routing:

| Task class | Preferred model or worker |
|---|---|
| Master planning, reasoning, safety checks, final decisions | GPT-5 |
| Coding implementation and code-review drafts | DeepSeek |
| Research and long-document synthesis | Kimi |
| Long-context document handling | Kimi |
| Classification and bulk analysis | Qwen |
| Repetitive background jobs | Local Llama |
| OCR, screenshots, media, document extraction | Local or low-cost OCR/vision worker |
| Embeddings | Cheap embedding model |

## Rationale

- Keeps ChatGPT as the master orchestrator and final decision layer.
- Offloads bulk, repetitive, and cost-sensitive work to cheaper worker models.
- Preserves stronger centralized safety and reasoning for final actions.
- Fits the Jarvis/XRP-HBAR runtime model where many agents may need low-cost background execution.
- Supports an under-AUD-100/month planning target for 100+ agents where workload, model choice, caching, batching, and local workers make that feasible.

## Option 1: ChatGPT Orchestrator With Cheaper Workers

This is the recommended target.

```text
ChatGPT Agent -> Task Router -> Kimi / DeepSeek / Qwen / Local Llama / OCR or vision workers
```

Use this when the system needs ChatGPT Agent features, connected tools, approval gates, and centralized final decisions, while still reducing bulk model spend.

## Option 2: Replace GPT Entirely

Use Kimi, DeepSeek, Qwen, or another OpenAI-compatible model as the whole agent runtime.

Pros:

- Very cheap compared with premium reasoning for every task.
- Scalable for high-volume background work.
- API compatible where the provider supports OpenAI-compatible APIs.

Cons:

- Loses native ChatGPT Agent features.
- Loses automatic use of ChatGPT built-in tools and connected app behavior.
- Requires a separately deployed runtime, tool layer, auth, memory, scheduling, safety gates, and orchestration.

Use this only for a separate deployed worker/runtime, not for replacing the ChatGPT Agent Builder core model.

## Option 3: Make ChatGPT Agent Internally Use Kimi/DeepSeek

Current repo assumption: not supported inside ChatGPT Agent Builder.

The ChatGPT Agent Editor does not expose a setting that lets the agent owner replace the core internal reasoning model with Kimi, DeepSeek, Qwen, or another third-party LLM. The agent can connect external apps and tools, but the core reasoning model remains OpenAI-managed.

Re-check official OpenAI documentation before building any implementation that depends on third-party replacement of the Agent Builder core model.

## Cheapest Architecture Target

| Task | Model |
|---|---|
| Master planner | GPT-5 |
| Coding | DeepSeek |
| Research | Kimi |
| Long context | Kimi |
| Classification | Qwen |
| OCR | Local or low-cost OCR/vision model |
| Embeddings | Cheap embedding model |

## Jarvis/XRP-HBAR Runtime Target

Target:

- Preserve ChatGPT's strongest reasoning for planning, safety checks, and final decisions.
- Offload expensive bulk work to cheaper models.
- Keep safety and final decisions centralized.
- Support OpenRouter, LiteLLM, or a similar routing layer.
- Keep provider secrets in GitHub Actions Secrets or the host runtime secret store only.
- Preserve the existing VTI/email deployment path; do not make router rollout a prerequisite for current health, readiness, VTI smoke, or Gmail proof gates.

## Future Router Backlog

1. Add a router interface that accepts a task type, safety tier, context size, estimated token cost, and preferred worker.
2. Add provider adapters for OpenRouter, LiteLLM, DeepSeek, Kimi, Qwen, local Llama, OCR/vision, and embeddings.
3. Add a policy file for routing defaults, cost caps, failover order, and tasks that must stay on GPT-5.
4. Add dry-run mode that returns the selected worker without calling any provider.
5. Add request/response audit metadata without storing secret values or sensitive payloads.
6. Add budget counters and monthly cap alerts for the under-AUD-100 planning target.
7. Add health checks for each configured provider using narrow read-only or metadata calls.
8. Add route-level smoke tests that prove fallback behavior without leaking prompts, secrets, or user data.

## Future Secret And Env Names

Future-only placeholders belong in the host runtime secret store, GitHub Actions Secrets, or `.env.production` depending on the implementation path. Do not commit real values.

Secret names:

- `OPENROUTER_API_KEY`
- `DEEPSEEK_API_KEY`
- `KIMI_API_KEY`
- `QWEN_API_KEY`
- `LITELLM_MASTER_KEY`

Non-secret or low-sensitivity runtime names:

- `LLM_ROUTER_MODE`
- `LLM_ROUTER_DEFAULT_MODEL`
- `LLM_ROUTER_CODING_MODEL`
- `LLM_ROUTER_RESEARCH_MODEL`
- `LLM_ROUTER_CLASSIFICATION_MODEL`
- `LOCAL_LLM_BASE_URL`
- `OCR_VISION_ENDPOINT`
- `EMBEDDING_MODEL`

## Proof Gates Before Claiming Live Router Support

Do not claim the hybrid router is live until all applicable gates pass:

| gate | required proof |
|---|---|
| config proof | env names present in the correct secret store with no values in repo or logs |
| dry-run proof | router selects expected workers without provider calls |
| provider health proof | each enabled provider passes a narrow health/auth check |
| cost guard proof | monthly and per-task budget caps are enforced |
| fallback proof | failed worker calls fall back or fail closed as designed |
| safety proof | final approval and high-risk decisions stay centralized |
| route proof | live runtime exposes a router status/smoke endpoint and passes workflow checks |

## Non-Goals For Current Deployment

- Do not replace ChatGPT Agent Builder's core model.
- Do not add real provider keys to the repository.
- Do not make DeepSeek/Kimi/Qwen/OpenRouter/LiteLLM required for current VTI/email health.
- Do not claim under-AUD-100/month operation until real usage, provider pricing, caching, local model capacity, and scheduler load are measured.
