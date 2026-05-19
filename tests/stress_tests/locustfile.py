from locust import HttpUser, task, between, TaskSet
import random
import uuid

# Mock data
LANGUAGES = ["Urdu", "English", "Roman Urdu", "Punjabi", "Sindhi"]
SERVICES = ["AC technician", "plumber", "electrician", "carpenter", "cleaner"]
LOCATIONS = ["Karachi", "Lahore", "Islamabad"]

def generate_mock_auth_header():
    return {"Authorization": f"Bearer test-token-{uuid.uuid4().hex[:8]}"}

class ParseFloodTasks(TaskSet):
    @task
    def parse_request(self):
        text = f"I need a {random.choice(SERVICES)} in {random.choice(LOCATIONS)} urgently. Speak {random.choice(LANGUAGES)}"
        self.client.post(
            "/api/v1/parse-request",
            json={"text": text},
            headers=generate_mock_auth_header(),
            name="/api/v1/parse-request"
        )

class ProviderSearchTasks(TaskSet):
    @task
    def find_providers(self):
        self.client.post(
            "/api/v1/find-providers",
            json={
                "service_type": random.choice(SERVICES),
                "latitude": 24.8607 + random.uniform(-0.05, 0.05),
                "longitude": 67.0011 + random.uniform(-0.05, 0.05),
                "radius_km": 10.0
            },
            headers=generate_mock_auth_header(),
            name="/api/v1/find-providers"
        )

class BookingSpikeTasks(TaskSet):
    @task
    def create_booking(self):
        self.client.post(
            "/api/v1/mobile/book-service",
            json={
                "provider_id": f"provider-{random.randint(1, 100)}",
                "service_type": random.choice(SERVICES),
                "location": {
                    "lat": 24.86,
                    "lng": 67.00
                },
                "urgency": "high"
            },
            headers=generate_mock_auth_header(),
            name="/api/v1/mobile/book-service"
        )

class EndToEndFloodTasks(TaskSet):
    @task
    def complete_workflow(self):
        # 1. Parse Request
        text = f"I need a {random.choice(SERVICES)} in Karachi"
        parse_res = self.client.post(
            "/api/v1/parse-request",
            json={"text": text},
            headers=generate_mock_auth_header(),
            name="E2E: /api/v1/parse-request"
        )
        
        service_type = "plumber"
        if parse_res.status_code == 200:
            service_type = parse_res.json().get("service", "plumber")
            
        # 2. Find Providers
        search_res = self.client.post(
            "/api/v1/find-providers",
            json={
                "service_type": service_type,
                "latitude": 24.86,
                "longitude": 67.00,
                "radius_km": 5.0
            },
            headers=generate_mock_auth_header(),
            name="E2E: /api/v1/find-providers"
        )
        provider_id = f"provider-{random.randint(1, 100)}"
        if search_res.status_code == 200:
            providers = search_res.json().get("providers", [])
            if providers:
                provider_id = providers[0].get("id", provider_id)
                
        # 3. Book
        self.client.post(
            "/api/v1/mobile/book-service",
            json={
                "provider_id": provider_id,
                "service_type": service_type,
                "location": {
                    "lat": 24.86,
                    "lng": 67.00
                },
                "urgency": "standard"
            },
            headers=generate_mock_auth_header(),
            name="E2E: /api/v1/mobile/book-service"
        )

class DisputeStormTasks(TaskSet):
    @task
    def file_dispute(self):
        booking_id = f"booking-{uuid.uuid4()}"
        
        # 1. File dispute
        response = self.client.post(
            "/api/v1/disputes/file-dispute",
            json={
                "booking_id": booking_id,
                "user_id": f"user-{random.randint(1, 100)}",
                "reason": "Provider arrived late and did a poor job.",
                "evidence_urls": []
            },
            headers=generate_mock_auth_header(),
            name="/api/v1/disputes/file-dispute"
        )
        
        # 2. Resolve dispute
        if response.status_code == 200:
            dispute_id = response.json().get("dispute", {}).get("id")
            if dispute_id:
                self.client.post(
                    "/api/v1/disputes/resolve-dispute",
                    json={
                        "dispute_id": dispute_id,
                        "resolution": "Refund issued.",
                        "refund_amount": 500.0
                    },
                    headers=generate_mock_auth_header(),
                    name="/api/v1/disputes/resolve-dispute"
                )

class KaamYaarStressUser(HttpUser):
    wait_time = between(1, 3)
    
    # Weighting the tasks to distribute the load
    tasks = {
        ParseFloodTasks: 3,
        ProviderSearchTasks: 3,
        BookingSpikeTasks: 2,
        EndToEndFloodTasks: 1,
        DisputeStormTasks: 1
    }
