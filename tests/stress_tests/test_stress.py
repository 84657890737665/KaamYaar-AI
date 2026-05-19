import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
import uuid
import random
import time
import concurrent.futures
from fastapi.testclient import TestClient

from app.main import app

# Create a TestClient instance. This bypasses the network and hits the ASGI app directly.
client = TestClient(app)

@pytest.fixture
def mock_auth_headers():
    return {"Authorization": f"Bearer test-token-{uuid.uuid4().hex[:8]}"}

def generate_1000_providers():
    providers = []
    for i in range(1000):
        providers.append({
            "id": f"provider-{i}",
            "name": f"Provider {i}",
            "service_type": "plumber",
            "rating": random.uniform(3.0, 5.0),
            "total_jobs": random.randint(10, 500),
            "cancellation_rate": random.uniform(0.0, 15.0),
            "base_rate": random.uniform(500, 2500),
            "availability": True,
            "skills": ["plumbing", "pipe repair"],
            "total_jobs": random.randint(10, 500),
            "location": {"lat": 24.86, "lng": 67.00},
            "address": "Mock Address",
            "on_time_score": random.uniform(80.0, 100.0),
            "distance_text": "5 km",
            "distance_value": random.randint(1000, 20000),
            "duration_text": "15 mins"
        })
    return providers

def test_st4_ranking_complexity(mock_auth_headers):
    """
    ST4 - Ranking Complexity: 1000 providers ranking with full 6-factor scoring.
    We hit the HTTP endpoint to measure the exact latency with 1000 providers.
    """
    providers = generate_1000_providers()
    
    payload = {
        "providers": providers,
        "user_request": {
            "service": "plumber",
            "urgency": "high",
            "complexity": "medium",
            "customer_location": {
                "lat": 24.86,
                "lng": 67.00
            }
        }
    }
    
    start_time = time.time()
    response = client.post(
        "/api/v1/rank-providers",
        json=payload,
        headers=mock_auth_headers,
        timeout=60.0 # Increased timeout to 60 seconds
    )
    end_time = time.time()
    
    latency = (end_time - start_time) * 1000
    
    if response.status_code != 200:
        print(f"Validation error: {response.text}")
        
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    
    data = response.json()
    assert "ranked_providers" in data, "Response should contain ranked_providers key"
    ranked_providers = data["ranked_providers"]
    assert len(ranked_providers) == 1000, f"Expected 1000 providers, got {len(ranked_providers)}"
    assert "ranking_score" in ranked_providers[0], "ranking_score missing from ranked provider"
    
    print(f"\n[ST4] Ranking 1000 providers via TestClient took {latency:.2f} ms")


def test_st3_booking_spike(mock_auth_headers):
    """
    ST3 - Booking Spike: Send a quick burst of 50 bookings concurrently
    to simulate an instantaneous spike. Uses ThreadPoolExecutor with TestClient.
    """
    def create_booking():
        payload = {
            "provider_id": f"provider-{random.randint(1, 100)}",
            "service_type": "plumber",
            "location": {
                "lat": 24.86,
                "lng": 67.00
            },
            "urgency": "high"
        }
        return client.post(
            "/api/v1/mobile/book-service",
            json=payload,
            headers={"Authorization": f"Bearer test-token-{uuid.uuid4().hex[:8]}"},
            timeout=60.0 # Increased timeout to 60 seconds
        )
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        start_time = time.time()
        futures = [executor.submit(create_booking) for _ in range(50)]
        
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000
        success_count = sum(1 for r in responses if r.status_code == 200)
        
        print(f"\n[ST3] Booking Spike: 50 bookings took {latency:.2f} ms. Success rate: {success_count}/50")
        assert success_count > 0, "No bookings succeeded."
