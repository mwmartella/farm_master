"""
Thin HTTP wrapper around the Worker Management API.
All GUI code should use these functions instead of touching the DB directly.
"""

import requests

BASE_URL = "http://192.168.1.7:8000"


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


# ─────────────────────────────────────────────
# Fields
# ─────────────────────────────────────────────

def get_fields() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/fields/"))


def create_field(name: str, code: str | None, site_id: str | None,
                 gross_area_ha: str | None, notes: str | None) -> dict:
    return _handle(requests.post(f"{BASE_URL}/fields/", json={
        "name": name,
        "code": code or None,
        "site_id": site_id or None,
        "gross_area_ha": float(gross_area_ha) if gross_area_ha else None,
        "notes": notes or None,
    }))


def update_field(field_id: str, name: str, code: str | None,
                 gross_area_ha: str | None, notes: str | None) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/fields/{field_id}", json={
        "name": name,
        "code": code or None,
        "gross_area_ha": float(gross_area_ha) if gross_area_ha else None,
        "notes": notes or None,
    }))


def delete_field(field_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/fields/{field_id}")
    resp.raise_for_status()


# ─────────────────────────────────────────────
# Fruit Types
# ─────────────────────────────────────────────

def get_fruit_types() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/fruit-types/"))


def create_fruit_type(name: str, notes: str | None) -> dict:
    return _handle(requests.post(f"{BASE_URL}/fruit-types/", json={
        "name": name,
        "notes": notes or None,
    }))


def update_fruit_type(fruit_type_id: str, name: str, notes: str | None) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/fruit-types/{fruit_type_id}", json={
        "name": name,
        "notes": notes or None,
    }))


def delete_fruit_type(fruit_type_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/fruit-types/{fruit_type_id}")
    resp.raise_for_status()


# ─────────────────────────────────────────────
# Varieties
# ─────────────────────────────────────────────

def get_varieties() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/varieties/"))


def create_variety(name: str, fruit_type_id: str) -> dict:
    return _handle(requests.post(f"{BASE_URL}/varieties/", json={
        "name": name,
        "fruit_type_id": fruit_type_id,
    }))


def update_variety(variety_id: str, name: str) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/varieties/{variety_id}", json={
        "name": name,
    }))


def delete_variety(variety_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/varieties/{variety_id}")
    resp.raise_for_status()


# ─────────────────────────────────────────────
# Variety Clones
# ─────────────────────────────────────────────

def get_variety_clones() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/variety-clones/"))


def create_variety_clone(name: str, variety_id: str, notes: str | None) -> dict:
    return _handle(requests.post(f"{BASE_URL}/variety-clones/", json={
        "name": name,
        "variety_id": variety_id,
        "notes": notes or None,
    }))


def update_variety_clone(clone_id: str, name: str, notes: str | None) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/variety-clones/{clone_id}", json={
        "name": name,
        "notes": notes or None,
    }))


def delete_variety_clone(clone_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/variety-clones/{clone_id}")
    resp.raise_for_status()


# ─────────────────────────────────────────────
# Blocks
# ─────────────────────────────────────────────

def get_blocks() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/blocks/"))


def create_block(field_id: str, name: str, code: str | None,
                 block_type: str | None, notes: str | None) -> dict:
    return _handle(requests.post(f"{BASE_URL}/blocks/", json={
        "field_id": field_id,
        "name": name,
        "code": code or None,
        "block_type": block_type or None,
        "notes": notes or None,
    }))


def update_block(block_id: str, name: str, code: str | None,
                 block_type: str | None, notes: str | None) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/blocks/{block_id}", json={
        "name": name,
        "code": code or None,
        "block_type": block_type or None,
        "notes": notes or None,
    }))


def delete_block(block_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/blocks/{block_id}")
    resp.raise_for_status()


# ─────────────────────────────────────────────
# Rootstocks
# ─────────────────────────────────────────────

def get_rootstocks() -> list[dict]:
    return _handle(requests.get(f"{BASE_URL}/rootstocks/"))


def create_rootstock(name: str, fruit_type_id: str,
                     vigour_class: str | None, notes: str | None) -> dict:
    return _handle(requests.post(f"{BASE_URL}/rootstocks/", json={
        "name": name,
        "fruit_type_id": fruit_type_id,
        "vigour_class": vigour_class or None,
        "notes": notes or None,
    }))


def update_rootstock(rootstock_id: str, name: str,
                     vigour_class: str | None, notes: str | None) -> dict:
    return _handle(requests.patch(f"{BASE_URL}/rootstocks/{rootstock_id}", json={
        "name": name,
        "vigour_class": vigour_class or None,
        "notes": notes or None,
    }))


def delete_rootstock(rootstock_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/rootstocks/{rootstock_id}")
    resp.raise_for_status()


