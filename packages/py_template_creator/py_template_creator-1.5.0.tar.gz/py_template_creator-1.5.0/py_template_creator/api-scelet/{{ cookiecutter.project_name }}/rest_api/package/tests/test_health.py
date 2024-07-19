def test_health(client):
    response = client.get("/api/health")
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_root(client):
    response = client.get("/api/")
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
