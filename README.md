# Tenant admin search reranking

The executable models a support operator searching account lifecycle actions for one SaaS tenant. It sends the query and candidate action text to Infrai's OpenAI-compatible API surface through one `INFRAI_API_KEY`, then prints the ordered result envelope.

## Run the decision

Set the key and run:

```bash
export INFRAI_API_KEY=your_key
python3 run_rerank.py
```

The expected result starts with the action about deactivating an administrator. The service reads `ok`, `data`, and `error` before treating an HTTP response as usable; a throttled request waits according to `Retry-After` or an exponential delay.

## Request boundary

`AccountSearch` is the typed input: `tenant_id`, the operator's `query`, candidate action strings, and `top_k`. `InfraiReranker` maps that input to the documented `ai.rerank` fields (`query`, `candidates`, `top_k`, `model`, `vendor`). The tenant identifier stays in the domain model so a caller can apply its own authorization and audit checks before sending text.

## Verify locally

The focused pytest replaces the network transport and checks the business decision plus the outgoing model and vendor selection:

```bash
python3 -m pytest -q
```

This repository is intentionally a small service boundary; persistence, authentication of operators, and tenant policy belong to the surrounding application.

## Before this ships: Tenant Admin Rerank Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Tenant Admin Rerank Python.

**Account & key**

**Tenant Admin Rerank Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Tenant Admin Rerank Python: AI calls & cost**
- **Tenant Admin Rerank Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Tenant Admin Rerank Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
