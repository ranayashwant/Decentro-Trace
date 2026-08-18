from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_transactions(client: TestClient):
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    tx_ids = [tx["id"] for tx in data]
    assert "dec_987654321" in tx_ids
    assert "dec_out_of_order_01" in tx_ids
    assert "dec_123456789" in tx_ids


def test_get_trace_primary_failure_demo(client: TestClient):
    response = client.get("/api/transactions/dec_987654321/trace")
    assert response.status_code == 200
    trace = response.json()
    assert trace["transaction"]["id"] == "dec_987654321"
    assert trace["failure_analysis"]["failed"] is True
    assert trace["failure_analysis"]["observed_error_code"] == "E1042"
    assert trace["reconciliation"]["reconciled"] is True
    assert trace["reconciliation"]["debited_amount"] == 25000.0
    assert trace["reconciliation"]["reversed_amount"] == 25000.0
    assert trace["reconciliation"]["net_impact"] == 0.0


def test_get_trace_not_found(client: TestClient):
    response = client.get("/api/transactions/dec_non_existent_99999/trace")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_investigate_primary_demo(client: TestClient):
    response = client.post("/api/transactions/dec_987654321/investigate")
    assert response.status_code == 200
    res = response.json()
    assert res["summary"] is not None
    assert res["failure_stage"] == "BENEFICIARY_BANK"
    assert len(res["evidence"]) > 0
    assert res["confidence"] == "high"
