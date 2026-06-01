import json
import random
import os
import uuid

services = ["plumber", "electrician", "ac_technician", "painter", "tutor", "beautician", "carpenter", "mechanic", "cleaner", "driver", "cook", "mason"]
cities = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Quetta", "Hyderabad", "Faisalabad"]
first_names = ["Ali", "Ahmed", "Hassan", "Omar", "Imran", "Kamran", "Tariq", "Zain", "Farhan", "Bilal", "Ayesha", "Fatima", "Sana", "Sadia", "Kiran"]
last_names = ["Khan", "Shah", "Ahmed", "Ali", "Qureshi", "Malik", "Sheikh", "Mirza", "Ansari", "Rajput"]

providers = []

for i in range(50):
    first = random.choice(first_names)
    last = random.choice(last_names)
    service_count = random.randint(1, 3)
    provider_services = random.sample(services, service_count)
    city = random.choice(cities)
    
    provider = {
        "provider_id": str(uuid.uuid4()),
        "name": f"{first} {last}",
        "service_types": provider_services,
        "location_name": city,
        "distance_km": 0.0, # Will be calculated dynamically
        "rating": round(random.uniform(3.5, 5.0), 1),
        "on_time_score": round(random.uniform(0.7, 1.0), 2),
        "cancellation_rate": round(random.uniform(0.0, 0.2), 2),
        "base_rate_pkr": random.choice([500, 1000, 1500, 2000, 2500, 3000]),
        "is_available": random.choice([True, True, True, False]), # 75% availability
        "skill_level": random.choice(["basic", "intermediate", "expert"]),
        "years_experience": random.randint(1, 20),
        "review_count": random.randint(5, 500)
    }
    providers.append(provider)

os.makedirs("data", exist_ok=True)
with open("data/providers.json", "w", encoding="utf-8") as f:
    json.dump(providers, f, indent=4)

print("Generated 50 providers successfully.")
