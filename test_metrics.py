#!/usr/bin/env python3
import sys
import time

import requests

BASE_URL = "http://localhost:8000"


def test_prime_generation_metrics():
    print("=" * 60)
    print("Testing Prime Generation Metrics")
    print("=" * 60)

    print("\n1. Checking current metrics in VictoriaMetrics...")
    try:
        response = requests.get("http://localhost:8428/api/v1/label/__name__/values")
        metrics = response.json().get("data", [])
        prime_metrics_before = [m for m in metrics if "primes" in m]
        print(
            f"   Prime metrics before: {prime_metrics_before if prime_metrics_before else 'None'}"
        )
    except Exception as e:
        print(f"   Warning: Could not fetch metrics: {e}")

    print("\n2. Attempting to get JWT token...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass123"},
            timeout=5,
        )
        if login_response.status_code == 200:
            token = login_response.json().get("jwt_token")
            print(f"   ✓ Login successful! Token obtained.")
        else:
            print(f"   ✗ Login failed (status {login_response.status_code})")
            print("   Note: This is expected if no test user exists in DB")
            print("\n   To properly test metrics, you need to:")
            print("   1. Create a user in the database, OR")
            print("   2. Use the FastAPI docs at http://localhost:8000/docs")
            return False
    except Exception as e:
        print(f"   ✗ Login error: {e}")
        return False

    print("\n3. Making prime generation requests...")
    headers = {"Authorization": f"Bearer {token}"}

    test_counts = [5, 10, 100, 1000]
    for count in test_counts:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/primes/generate",
                json={"count": count},
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200:
                print(f"   ✓ Generated {count} primes successfully")
            else:
                print(
                    f"   ✗ Failed to generate {count} primes (status {response.status_code})"
                )
        except Exception as e:
            print(f"   ✗ Error generating {count} primes: {e}")

    print("\n4. Waiting for metrics to be exported (15 seconds)...")
    time.sleep(16)

    print("\n5. Checking for new prime metrics...")
    try:
        response = requests.get("http://localhost:8428/api/v1/label/__name__/values")
        metrics = response.json().get("data", [])
        prime_metrics = [m for m in metrics if "primes" in m]

        if prime_metrics:
            print(f"   ✓ SUCCESS! Found {len(prime_metrics)} prime metrics:")
            for metric in sorted(prime_metrics):
                print(f"     - {metric}")
        else:
            print("   ✗ No prime metrics found yet")

    except Exception as e:
        print(f"   ✗ Error fetching metrics: {e}")

    print("\n6. Querying metric values...")
    prime_metric_names = [
        "primes_generation_requests_total",
        "primes_requested_count_bucket",
        "primes_generation_duration_bucket",
        "primes_numbers_generated_total",
        "primes_computation_iterations_bucket",
    ]

    for metric_name in prime_metric_names:
        try:
            response = requests.get(
                f"http://localhost:8428/api/v1/query", params={"query": metric_name}
            )
            result = response.json()
            if result.get("data", {}).get("result"):
                print(f"   ✓ {metric_name}: {len(result['data']['result'])} series")
            else:
                print(f"   - {metric_name}: No data")
        except Exception as e:
            print(f"   ✗ Error querying {metric_name}: {e}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_prime_generation_metrics()
    sys.exit(0 if success else 1)
