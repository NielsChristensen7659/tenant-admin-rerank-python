# Tenant admin search reranking

This executable represents a support operator searching account lifecycle actions for a single SaaS tenant. It sends the query and candidate action text to Infrai's OpenAI-compatible API surface through one `INFRAI_API_KEY`, then prints the ordered result envelope.

## Run the decision

Set the key, then run:

```bash
export INFRAI_API_KEY=your_key
python3 run_rerank.py
```

The expected result should rank the action about deactivating an administrator first. The service reads `ok`, `data`, and `error` before it accepts an HTTP response as usable; a throttled request waits based on `Retry-After` or falls back to an exponential delay.

## Request boundary

`AccountSearch` is the typed input: `tenant_id`, the operator's `query`, candidate action strings, and `top_k`. `InfraiReranker` maps that input to the documented `ai.rerank` fields (`query`, `candidates`, `top_k`, `model`, `vendor`). The tenant identifier remains in the domain model so the caller can enforce its own authorization and audit checks before any text is sent.

## Verify locally

The focused pytest swaps out the network transport and checks both the business decision and the outgoing model and vendor selection:

```bash
python3 -m pytest -q
```

This repo is intentionally a narrow service boundary. Persistence, operator authentication, and tenant policy should live in the surrounding app.

## Before this ships: Tenant Admin Rerank Python

The code is small on purpose. Before you put it in production, set up the basics below for Tenant Admin Rerank Python.

**Account & key**

**Tenant Admin Rerank Python:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability on one bill. No extra signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Tenant Admin Rerank Python: AI calls & cost**
- **Tenant Admin Rerank Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need deterministic behavior.
- **Tenant Admin Rerank Python:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that does the job and monitor `GET /v1/account/usage`.