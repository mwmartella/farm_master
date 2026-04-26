"""
Thin HTTP wrapper around the Worker Management API.
All GUI code should use these functions instead of touching the DB directly.
"""

import requests

BASE_URL = "http://192.168.1.15:8000"


def _handle(response: requests.Response) -> dict:
    """Raise a clean exception with the API error detail if the call failed."""
    try:
        response.raise_for_status()
    except requests.HTTPError:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(detail)
    return response.json()


# ─────────────────────────────────────────────
# Worker Codes
# ─────────────────────────────────────────────

def get_worker_codes() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/worker-codes/"))


def get_active_worker_codes() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/worker-codes/active"))


def create_worker_code(code_name: str, code_description: str, pay_rate: str) -> dict:
    return _handle(requests.post(f"{BASE_URL}/worker-codes/", json={
        "code_name": code_name,
        "code_description": code_description,
        "pay_rate": pay_rate,
    }))


def update_worker_code(code_id: str, code_name: str,
                       code_description: str, pay_rate: str) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/worker-codes/{code_id}", json={
        "code_name": code_name,
        "code_description": code_description,
        "pay_rate": pay_rate,
    }))


def end_worker_code(code_id: str) -> dict:
    return _handle(requests.post(f"{BASE_URL}/worker-codes/{code_id}/end"))


# ─────────────────────────────────────────────
# Workers
# ─────────────────────────────────────────────

def get_workers() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/workers/"))


def create_worker(worker_code: str, first_name: str, last_name: str) -> dict:
    return _handle(requests.post(f"{BASE_URL}/workers/", json={
        "worker_code": worker_code,
        "first_name": first_name,
        "last_name": last_name,
    }))


def update_worker(worker_id: str, first_name: str, last_name: str) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/workers/{worker_id}", json={
        "first_name": first_name,
        "last_name": last_name,
    }))


def end_worker(worker_id: str) -> dict:
    return _handle(requests.post(f"{BASE_URL}/workers/{worker_id}/end"))


# ─────────────────────────────────────────────
# Worker Times
# ─────────────────────────────────────────────

def get_worker_times() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/worker-times/"))


def create_worker_time(time_name: str, start_time: str,
                       end_time: str | None) -> dict:
    payload = {"time_name": time_name, "start_time": start_time}
    if end_time:
        payload["end_time"] = end_time
    return _handle(requests.post(f"{BASE_URL}/worker-times/", json=payload))


def update_worker_time(time_id: str, time_name: str,
                       start_time: str, end_time: str | None) -> dict:
    payload: dict = {"time_name": time_name, "start_time": start_time}
    if end_time:
        payload["end_time"] = end_time
    return _handle(requests.patch(f"{BASE_URL}/worker-times/{time_id}",
                                  json=payload))


def end_worker_time(time_id: str) -> dict:
    return _handle(requests.post(f"{BASE_URL}/worker-times/{time_id}/end"))


# ─────────────────────────────────────────────
# Businesses
# ─────────────────────────────────────────────

def get_businesses() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/businesses/"))


def create_business(name: str, code: str | None) -> dict:
    return _handle(requests.post(f"{BASE_URL}/businesses/", json={
        "name": name,
        "code": code or None,
    }))


def update_business(business_id: str, name: str, code: str | None) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/businesses/{business_id}", json={
        "name": name,
        "code": code or None,
    }))


def delete_business(business_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/businesses/{business_id}")
    resp.raise_for_status()


# ─────────────────────────────────────────────
# Sites
# ─────────────────────────────────────────────

def get_sites() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/sites/"))


def create_site(name: str, code: str | None, business_id: str | None,
                type_: str, address: str, notes: str | None) -> dict:
    return _handle(requests.post(f"{BASE_URL}/sites/", json={
        "name": name,
        "code": code or None,
        "business_id": business_id or None,
        "type": type_,
        "address": address,
        "notes": notes or None,
    }))


def update_site(site_id: str, name: str, code: str | None,
                type_: str, address: str, notes: str | None) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/sites/{site_id}", json={
        "name": name,
        "code": code or None,
        "type": type_,
        "address": address,
        "notes": notes or None,
    }))


def delete_site(site_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/sites/{site_id}")
    resp.raise_for_status()


