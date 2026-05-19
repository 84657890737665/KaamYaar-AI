import json

new_providers = [
    # 4 Plumbers (Karachi, Lahore, Islamabad, Faisalabad)
    {
        "id": "prov_031",
        "name": "Nadia Pipes",
        "service_type": "Plumber",
        "location": {"lat": 24.8607, "lng": 67.0011},
        "address": "Saddar, Karachi",
        "rating": 4.8,
        "on_time_score": 95.0,
        "cancellation_rate": 2.1,
        "base_rate": 800.0,
        "availability": True,
        "skills": ["Pipe Fitting", "Leak Repair", "Sanitary"]
    },
    {
        "id": "prov_032",
        "name": "Kamran Plumber",
        "service_type": "Plumber",
        "location": {"lat": 31.5204, "lng": 74.3587},
        "address": "Gulberg, Lahore",
        "rating": 4.1,
        "on_time_score": 88.5,
        "cancellation_rate": 5.4,
        "base_rate": 1200.0,
        "availability": False,
        "skills": ["Motor Installation", "Geyser Repair"]
    },
    {
        "id": "prov_033",
        "name": "Sadia Repairs",
        "service_type": "Plumber",
        "location": {"lat": 33.6844, "lng": 73.0479},
        "address": "F-8, Islamabad",
        "rating": 4.5,
        "on_time_score": 92.0,
        "cancellation_rate": 1.5,
        "base_rate": 1500.0,
        "availability": True,
        "skills": ["Leak Repair", "Drain Unblocking"]
    },
    {
        "id": "prov_034",
        "name": "Tariq Ustad",
        "service_type": "Plumber",
        "location": {"lat": 31.4187, "lng": 73.0791},
        "address": "People's Colony, Faisalabad",
        "rating": 3.9,
        "on_time_score": 85.0,
        "cancellation_rate": 7.0,
        "base_rate": 600.0,
        "availability": True,
        "skills": ["Pipe Fitting", "Geyser Repair"]
    },

    # 4 Electricians (Karachi, Lahore, Rawalpindi, Faisalabad)
    {
        "id": "prov_035",
        "name": "Faizan Electrician",
        "service_type": "Electrician",
        "location": {"lat": 24.8918, "lng": 67.0732},
        "address": "Gulshan-e-Iqbal, Karachi",
        "rating": 4.6,
        "on_time_score": 94.2,
        "cancellation_rate": 3.0,
        "base_rate": 1000.0,
        "availability": True,
        "skills": ["Wiring", "UPS Setup"]
    },
    {
        "id": "prov_036",
        "name": "Ayesha Tech",
        "service_type": "Electrician",
        "location": {"lat": 31.4697, "lng": 74.2728},
        "address": "Johar Town, Lahore",
        "rating": 4.9,
        "on_time_score": 98.0,
        "cancellation_rate": 0.5,
        "base_rate": 1800.0,
        "availability": False,
        "skills": ["Solar Installation", "Switchboard Repair"]
    },
    {
        "id": "prov_037",
        "name": "Zeeshan Spark",
        "service_type": "Electrician",
        "location": {"lat": 33.6261, "lng": 73.0714},
        "address": "Satellite Town, Rawalpindi",
        "rating": 4.0,
        "on_time_score": 87.5,
        "cancellation_rate": 8.1,
        "base_rate": 900.0,
        "availability": True,
        "skills": ["Wiring", "Appliance Repair"]
    },
    {
        "id": "prov_038",
        "name": "Imran Bhai",
        "service_type": "Electrician",
        "location": {"lat": 31.4326, "lng": 73.0683},
        "address": "Samanabad, Faisalabad",
        "rating": 3.8,
        "on_time_score": 89.0,
        "cancellation_rate": 6.5,
        "base_rate": 750.0,
        "availability": True,
        "skills": ["UPS Setup", "Switchboard Repair"]
    },

    # 4 AC Technicians (Karachi, Islamabad, Rawalpindi, Lahore)
    {
        "id": "prov_039",
        "name": "Sajid AC Experts",
        "service_type": "AC Technician",
        "location": {"lat": 24.8138, "lng": 67.0423},
        "address": "Clifton, Karachi",
        "rating": 4.7,
        "on_time_score": 93.5,
        "cancellation_rate": 4.2,
        "base_rate": 1600.0,
        "availability": True,
        "skills": ["Gas Refill", "AC Servicing"]
    },
    {
        "id": "prov_040",
        "name": "Fatima Cooling",
        "service_type": "AC Technician",
        "location": {"lat": 33.7294, "lng": 73.0931},
        "address": "G-11, Islamabad",
        "rating": 5.0,
        "on_time_score": 99.5,
        "cancellation_rate": 1.0,
        "base_rate": 2000.0,
        "availability": True,
        "skills": ["Installation", "Compressor Repair"]
    },
    {
        "id": "prov_041",
        "name": "Rizwan Tech",
        "service_type": "AC Technician",
        "location": {"lat": 33.5973, "lng": 73.0481},
        "address": "Saddar, Rawalpindi",
        "rating": 3.7,
        "on_time_score": 82.0,
        "cancellation_rate": 9.5,
        "base_rate": 850.0,
        "availability": True,
        "skills": ["Gas Refill", "AC Servicing"]
    },
    {
        "id": "prov_042",
        "name": "Ali Cool Care",
        "service_type": "AC Technician",
        "location": {"lat": 31.4805, "lng": 74.3239},
        "address": "Model Town, Lahore",
        "rating": 4.4,
        "on_time_score": 90.1,
        "cancellation_rate": 3.8,
        "base_rate": 1300.0,
        "availability": False,
        "skills": ["Compressor Repair", "Gas Refill"]
    },

    # 4 Carpenters (Lahore, Karachi, Faisalabad, Rawalpindi)
    {
        "id": "prov_043",
        "name": "Nawaz Woodworks",
        "service_type": "Carpenter",
        "location": {"lat": 31.5580, "lng": 74.3255},
        "address": "Anarkali, Lahore",
        "rating": 4.8,
        "on_time_score": 97.0,
        "cancellation_rate": 2.0,
        "base_rate": 1500.0,
        "availability": True,
        "skills": ["Cabinets", "Wood Polish"]
    },
    {
        "id": "prov_044",
        "name": "Hina Carpenters",
        "service_type": "Carpenter",
        "location": {"lat": 24.8667, "lng": 67.0311},
        "address": "PECHS, Karachi",
        "rating": 4.5,
        "on_time_score": 92.5,
        "cancellation_rate": 4.0,
        "base_rate": 1200.0,
        "availability": True,
        "skills": ["Furniture Repair", "Door Fitting"]
    },
    {
        "id": "prov_045",
        "name": "Aslam Maker",
        "service_type": "Carpenter",
        "location": {"lat": 31.4116, "lng": 73.0844},
        "address": "D Ground, Faisalabad",
        "rating": 3.6,
        "on_time_score": 80.0,
        "cancellation_rate": 8.0,
        "base_rate": 700.0,
        "availability": True,
        "skills": ["Cabinets", "Furniture Repair"]
    },
    {
        "id": "prov_046",
        "name": "Shahid Bhai",
        "service_type": "Carpenter",
        "location": {"lat": 33.6425, "lng": 73.0728},
        "address": "Commercial Market, Rawalpindi",
        "rating": 4.2,
        "on_time_score": 88.0,
        "cancellation_rate": 5.5,
        "base_rate": 950.0,
        "availability": False,
        "skills": ["Wood Polish", "Door Fitting"]
    },

    # 4 Painters (Islamabad, Karachi, Lahore, Faisalabad)
    {
        "id": "prov_047",
        "name": "Ayesha Colors",
        "service_type": "Painter",
        "location": {"lat": 33.7104, "lng": 73.0551},
        "address": "Blue Area, Islamabad",
        "rating": 4.9,
        "on_time_score": 98.5,
        "cancellation_rate": 1.2,
        "base_rate": 1900.0,
        "availability": True,
        "skills": ["Texture Paint", "Wall Painting"]
    },
    {
        "id": "prov_048",
        "name": "Farooq Paints",
        "service_type": "Painter",
        "location": {"lat": 24.9152, "lng": 67.0933},
        "address": "Gulistan-e-Johar, Karachi",
        "rating": 4.3,
        "on_time_score": 91.0,
        "cancellation_rate": 6.2,
        "base_rate": 1100.0,
        "availability": True,
        "skills": ["Distemper", "Exterior Paint"]
    },
    {
        "id": "prov_049",
        "name": "Bilal Master",
        "service_type": "Painter",
        "location": {"lat": 31.4621, "lng": 74.2942},
        "address": "Wapda Town, Lahore",
        "rating": 3.8,
        "on_time_score": 85.5,
        "cancellation_rate": 7.8,
        "base_rate": 800.0,
        "availability": False,
        "skills": ["Wall Painting", "Distemper"]
    },
    {
        "id": "prov_050",
        "name": "Javed Arts",
        "service_type": "Painter",
        "location": {"lat": 31.4255, "lng": 73.0911},
        "address": "Madina Town, Faisalabad",
        "rating": 4.1,
        "on_time_score": 88.8,
        "cancellation_rate": 4.5,
        "base_rate": 950.0,
        "availability": True,
        "skills": ["Texture Paint", "Exterior Paint"]
    }
]

def main():
    filepath = 'data/providers.json'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    # Filter out existing ones to avoid duplicates if re-run
    existing_ids = {p['id'] for p in data}
    to_add = [p for p in new_providers if p['id'] not in existing_ids]

    data.extend(to_add)

    # Make sure we don't exceed 50 if there are already 50
    if len(data) > 50:
        data = data[:50]

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Added {len(to_add)} providers. Total is now {len(data)}.")

if __name__ == '__main__':
    main()
