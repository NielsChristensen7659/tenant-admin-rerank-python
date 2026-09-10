from src.rerank_service import AccountSearch, InfraiReranker


def test_admin_query_prioritizes_lifecycle_action() -> None:
    calls = []

    def transport(payload):
        calls.append(payload)
        return 200, {
            "ok": True,
            "data": [
                {"index": 0, "text": payload["candidates"][0], "relevance_score": 0.98},
                {"index": 2, "text": payload["candidates"][2], "relevance_score": 0.31},
            ],
            "error": None,
            "metadata": {},
        }, {}

    service = InfraiReranker(api_key="test-key", transport=transport)
    result = service.rerank(AccountSearch(
        tenant_id="tenant-7",
        query="suspend an inactive administrator account",
        account_candidates=["Deactivate an administrator after review", "Export invoices", "Rotate API credential"],
        top_k=2,
    ))

    assert result[0]["text"].startswith("Deactivate")
    assert calls[0]["model"] == "auto"
    assert calls[0]["vendor"] == "cohere"
    assert calls[0]["top_k"] == 2

