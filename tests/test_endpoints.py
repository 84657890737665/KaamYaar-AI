from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    # It could be 200 or 503 depending on if Firestore is properly connected or missing creds locally
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["service"] == "kaamyaar-backend"

def test_parse_request_english():
    payload = {"raw_text": "I need a plumber immediately in F-7", "language_hint": "en"}
    response = client.post("/api/v1/parse-request", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "service" in data

def test_parse_request_roman_urdu():
    payload = {"raw_text": "Mujhe urgent AC repair wala chahiye G-13 mein", "language_hint": "roman_ur"}
    response = client.post("/api/v1/parse-request", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "service" in data

def test_parse_request_urdu():
    payload = {"raw_text": "مجھے جی 13 میں اے سی ٹیکنیشن کی ضرورت ہے", "language_hint": "ur"}
    response = client.post("/api/v1/parse-request", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "service" in data

def test_find_providers():
    payload = {
        "service": "AC Technician",
        "location": {"lat": 33.6844, "lng": 73.0479},
        "radius_km": 15.0,
        "require_available": True
    }
    response = client.post("/api/v1/find-providers", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # The list may be empty or contain providers depending on seed/mock state
    if len(data) > 0:
        assert "distance_value" in data[0]
        assert "distance_text" in data[0]

def test_rank_providers():
    mock_provider = {
        "id": "mock_rank_1",
        "name": "Test AC Service",
        "service_type": "AC Technician",
        "location": {"lat": 33.6900, "lng": 73.0400},
        "address": "G-11, Islamabad",
        "rating": 4.5,
        "on_time_score": 90.0,
        "cancellation_rate": 5.0,
        "base_rate": 1500.0,
        "availability": True,
        "skills": ["AC repair"],
        "distance_text": "5 km",
        "distance_value": 5000,
        "duration_text": "10 mins"
    }
    
    payload = {
        "providers": [mock_provider],
        "user_request": {"service": "AC Technician", "urgency": "urgent"},
        "weights": {
            "distance": 0.3,
            "rating": 0.2,
            "on_time": 0.2,
            "price": 0.15,
            "cancellation": 0.1,
            "skills_match": 0.05
        }
    }
    
    response = client.post("/api/v1/rank-providers", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ranked_providers" in data
    assert len(data["ranked_providers"]) == 1
    assert "ranking_score" in data["ranked_providers"][0]
    assert "reasoning_text" in data["ranked_providers"][0]
    assert "rating_score" in data["ranked_providers"][0]["factors"]
