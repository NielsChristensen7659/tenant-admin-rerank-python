import json

from src.rerank_service import AccountSearch, rerank_account_search


if __name__ == "__main__":
    search = AccountSearch(
        tenant_id="acme-finance",
        query="suspend an inactive administrator account",
        account_candidates=[
            "Deactivate an administrator after an inactivity review",
            "Invite a new billing contact",
            "Rotate an API credential for a tenant",
        ],
        top_k=2,
    )
    print(json.dumps(rerank_account_search(search), indent=2))

