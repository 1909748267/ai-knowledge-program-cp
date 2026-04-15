def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["deepseek_config"] in {"ok", "missing"}
    assert "timestamp" in body
