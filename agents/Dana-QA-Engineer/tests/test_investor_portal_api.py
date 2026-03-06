import time
import requests
import pytest

BASE_URL = "http://localhost:8000"

# Helpers

def create_link(payload):
    return requests.post(f"{BASE_URL}/api/investor_links", json=payload)


def get_dashboard(token):
    return requests.get(f"{BASE_URL}/dashboard", params={"token": token})


def revoke_link(link_id):
    return requests.delete(f"{BASE_URL}/api/investor_links/{link_id}")


def get_audit_logs(link_id):
    return requests.get(f"{BASE_URL}/api/audit_logs", params={"link_id": link_id})


# Tests

@pytest.mark.integration
def test_create_link_and_access_dashboard():
    payload = {
        "founder_id": "test-founder",
        "permissions": ["read:kpis", "download:materials"],
        "expires_in": 60  # seconds for test
    }
    r = create_link(payload)
    assert r.status_code == 201, f"Create link failed: {r.status_code} {r.text}"
    body = r.json()
    assert "token" in body and "id" in body and "expires_at" in body

    token = body["token"]
    dash = get_dashboard(token)
    assert dash.status_code == 200
    j = dash.json()
    assert "kpis" in j and "materials" in j


@pytest.mark.integration
def test_revocation_and_audit_log():
    payload = {
        "founder_id": "test-founder",
        "permissions": ["read:kpis"],
        "expires_in": 120
    }
    r = create_link(payload)
    assert r.status_code == 201
    body = r.json()
    link_id = body["id"]
    token = body["token"]

    # Access once
    dash = get_dashboard(token)
    assert dash.status_code == 200

    # Revoke
    rev = revoke_link(link_id)
    assert rev.status_code == 204

    # Access should now fail
    dash2 = get_dashboard(token)
    assert dash2.status_code in (401, 403, 404)

    # Audit log contains access entry
    logs = get_audit_logs(link_id)
    assert logs.status_code == 200
    entries = logs.json()
    assert any(e.get("action") == "accessed_dashboard" for e in entries)


@pytest.mark.integration
def test_expired_token_behaviour():
    payload = {
        "founder_id": "test-founder",
        "permissions": ["read:kpis"],
        "expires_in": 1
    }
    r = create_link(payload)
    assert r.status_code == 201
    token = r.json()["token"]
    time.sleep(2)
    dash = get_dashboard(token)
    assert dash.status_code in (401, 403, 404)


@pytest.mark.integration
def test_kpi_endpoint_performance():
    start = time.time()
    r = requests.get(f"{BASE_URL}/api/kpis")
    duration_ms = (time.time() - start) * 1000
    assert r.status_code == 200
    assert duration_ms < 200, f"KPI endpoint too slow: {duration_ms}ms"


@pytest.mark.integration
def test_malformed_token_rejected():
    r = get_dashboard("not-a-real-token")
    assert r.status_code in (401, 400)


# To run: pytest output/tests/test_investor_portal_api.py -q
