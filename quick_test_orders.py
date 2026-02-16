#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Get verification code
resp = requests.post(f"{BASE_URL}/auth/send-code", json={"phone_number": "1234567890"})
code = resp.json()["debug_code"]
print(f"Code: {code}")

# 2. Login
resp = requests.post(f"{BASE_URL}/auth/login", json={"phone_number": "1234567890", "verification_code": code})
token = resp.json()["access_token"]
print(f"Token: {token[:20]}...")

# 3. Get orders
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(f"{BASE_URL}/order/orders?limit=10", headers=headers)
print(f"\nStatus: {resp.status_code}")
print(json.dumps(resp.json(), indent=2))
