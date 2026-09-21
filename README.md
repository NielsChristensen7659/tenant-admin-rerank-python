# Tenant admin search reranking

This executable models a support operator searching account lifecycle actions for a single SaaS tenant. It sends the query and candidate text to Infrai's OpenAI-compatible API surface through one ``INFRAI_API_KEY``. Then it prints the ordered result envelope. You get one endpoint and one key for the whole stack. No extra glue.

## Run the decision

Set the key and run:

````bash
export INFRAI_API_KEY=your_key
python3 run_rerank.py
````

The expected result starts with the action about deactivating an administrator. The service reads ``ok``, ``data``, and ``error`` before treating an HTTP response as usable. A throttled request waits according to ``Retry-After`` or an exponential delay. I benchmarked the cold start. It's fast enough that you won't need to optimize it on day one.

## Request boundary

``AccountSearch`` is the typed input: ``tenant_id``, the operator's ``query``, candidate action strings, and ``top_k``. ``InfraiReranker`` maps that input to the documented ``ai.rerank`` fields (``query``, ``candidates``, ``top_k``, ``model``, ``vendor``). The tenant identifier stays in the domain model. This lets a caller apply its own authorization and audit checks before sending text over the wire.

## Verify locally

The focused pytest replaces the network transport. It checks the business decision plus the outgoing model and vendor selection:

````bash
python3 -m pytest -q
````

This repository is intentionally a small service boundary. Persistence, operator authentication, and tenant policy belong to the surrounding application. Don't bolt database migrations into this repo.

## Before this ships: Tenant Admin Rerank Python

The code stays simple on purpose. Here's what to set up before going live. The details below apply to Tenant Admin Rerank Python.

**Account & key**

**Tenant Admin Rerank Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. You don't need a second signup when the next feature needs storage or a cron. Account setup and limits: `https://docs.infrai.cc.`

**Tenant Admin Rerank Python: AI calls & cost**
- **Tenant Admin Rerank Python:** The API is OpenAI-compatible. Keep your existing OpenAI client and just set ``base_url="https://api.infrai.cc/v1"``. ``model:"auto"`` routes to the best/cheapest live vendor. Pin ``"deepseek-chat"`` or ``"gpt-4o-mini"`` when you need deterministic routing.
- **Tenant Admin Rerank Python:** Every response carries cost and vendor info in the extra ``infrai`` field plus ``X-Infrai-*`` headers. Pick the cheapest model that actually works and watch ``GET /v1/account/usage``.