def sample_holding():
    return {
        "tradeDate": "2026-09-21",
        "company": "Example Capital",
        "department": "Equities",
        "portfolioCode": "PORT-01",
        "stockSymbol": "sh.600000",
        "stockName": "Example Bank",
        "amount": 100,
        "cost": 9.5,
        "marketValue": 1000,
        "closePrice": 10,
        "industry": "Banking",
    }


def test_health_and_empty_holdings(client):
    assert client.get("/health").get_json() == {"status": "ok"}
    assert client.get("/holdings/show").get_json() == []


def test_holding_crud_flow(client):
    payload = sample_holding()
    created = client.post("/data/edit/add", json=payload)
    assert created.status_code == 201

    listed = client.get("/holdings/show").get_json()
    assert len(listed) == 1
    assert listed[0]["market_value"] == 1000

    payload["marketValue"] = 1200
    updated = client.put("/data/edit/update", json=payload)
    assert updated.status_code == 200
    assert updated.get_json()["data"]["market_value"] == 1200

    duplicate = client.post("/data/edit/add", json=payload)
    assert duplicate.status_code == 409

    deleted = client.post("/data/edit/delete", json=listed[0])
    assert deleted.status_code == 200
    assert client.get("/holdings/show").get_json() == []


def test_mutations_require_full_record_identity(client):
    response = client.post("/data/edit/delete", json={"trade_date": "2026-09-21"})
    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["error"]
