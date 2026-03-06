import os
import requests
import time

BASE_URL = os.environ.get('INVESTOR_PORTAL_BASE', 'https://staging-api.venture.example')
AUTH_TOKEN = os.environ.get('INVESTOR_PORTAL_TOKEN', 'TEST_SERVICE_TOKEN_v1')
HEADERS = {'Authorization': f'Bearer {AUTH_TOKEN}'}


def test_create_and_revoke_link():
    # Create
    payload = {'email': 'qa+tester@example.com', 'expires_in_minutes': 10}
    r = requests.post(f"{BASE_URL}/api/investor_links", json=payload, headers=HEADERS, timeout=5)
    assert r.status_code == 201, f"Create failed: {r.status_code} {r.text}"
    data = r.json()
    link_id = data['id']
    token = data['token']

    # Dashboard access
    r2 = requests.get(f"{BASE_URL}/dashboard", params={'token': token}, timeout=5)
    assert r2.status_code == 200, f"Dashboard access failed: {r2.status_code} {r2.text}"

    # Audit logs include creation
    r3 = requests.get(f"{BASE_URL}/api/audit_logs", params={'link_id': link_id}, headers=HEADERS, timeout=5)
    assert r3.status_code == 200
    logs = r3.json()
    assert any(l['action'] == 'create' for l in logs), f"Create audit not found: {logs}"

    # Revoke
    r4 = requests.delete(f"{BASE_URL}/api/investor_links/{link_id}", headers=HEADERS, timeout=5)
    assert r4.status_code == 204

    # Audit logs include revoke
    r5 = requests.get(f"{BASE_URL}/api/audit_logs", params={'link_id': link_id}, headers=HEADERS, timeout=5)
    assert r5.status_code == 200
    logs2 = r5.json()
    assert any(l['action'] == 'revoke' for l in logs2), f"Revoke audit not found: {logs2}"


def test_link_expiry_and_malformed_token():
    # Create short-lived link
    payload = {'email': 'qa+expire@example.com', 'expires_in_minutes': 0}
    r = requests.post(f"{BASE_URL}/api/investor_links", json=payload, headers=HEADERS, timeout=5)
    assert r.status_code == 201
    token = r.json()['token']

    # Immediately access should be 401 because expires_in_minutes=0
    r2 = requests.get(f"{BASE_URL}/dashboard", params={'token': token}, timeout=5)
    assert r2.status_code in (401, 404), f"Expected expired token to be rejected, got {r2.status_code}"

    # Malformed token
    r3 = requests.get(f"{BASE_URL}/dashboard", params={'token': 'bad.token.value'}, timeout=5)
    assert r3.status_code == 401


def test_kpi_latency():
    t0 = time.time()
    r = requests.get(f"{BASE_URL}/api/kpis", headers=HEADERS, timeout=5)
    t1 = time.time()
    assert r.status_code == 200
    latency_ms = (t1 - t0) * 1000
    assert latency_ms < 500, f"KPI latency too high: {latency_ms}ms"


def teardown_module(module):
    # Clean up test data using teardown endpoint
    r = requests.post(f"{BASE_URL}/api/testing/teardown", headers=HEADERS, timeout=10)
    if r.status_code not in (202, 200):
        print('Teardown failed or not authorized:', r.status_code, r.text)
