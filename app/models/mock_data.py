from datetime import datetime, timezone
from typing import List
from .provider import Provider, Location
from .user import User
from .booking import Booking, BookingStatus, PriceBreakdown
from .dispute import Dispute, DisputeStatus

# --- MOCK PROVIDERS (30 Realistic Pakistani Providers) ---
MOCK_PROVIDERS: List[Provider] = [
    # Karachi Providers
    Provider(
        id="prov_khi_01",
        name="Muhammad Ali",
        service_type="Plumber",
        location=Location(lat=24.8607, lng=67.0011),
        address="Shop 12, Gulshan-e-Iqbal Block 5, Karachi",
        rating=4.5,
        on_time_score=95.0,
        cancellation_rate=2.0,
        base_rate=800.0,
        availability=True,
        skills=["Pipe Fitting", "Water Heater Repair", "Leak Detection"]
    ),
    Provider(
        id="prov_khi_02",
        name="Tariq Electrician",
        service_type="Electrician",
        location=Location(lat=24.8236, lng=67.0326),
        address="Phase 2, DHA, Karachi",
        rating=4.8,
        on_time_score=98.0,
        cancellation_rate=1.0,
        base_rate=1000.0,
        availability=True,
        skills=["Wiring", "AC Installation", "UPS Setup"]
    ),
    Provider(
        id="prov_khi_03",
        name="Shazia Maid Services",
        service_type="Maid",
        location=Location(lat=24.8722, lng=67.0333),
        address="PECHS Block 2, Karachi",
        rating=4.2,
        on_time_score=90.0,
        cancellation_rate=5.0,
        base_rate=500.0,
        availability=True,
        skills=["Cleaning", "Cooking", "Laundry"]
    ),
    Provider(
        id="prov_khi_04",
        name="Imran Carpenter",
        service_type="Carpenter",
        location=Location(lat=24.9180, lng=67.0971),
        address="Johar Mor, Gulistan-e-Johar, Karachi",
        rating=4.6,
        on_time_score=92.0,
        cancellation_rate=3.0,
        base_rate=1200.0,
        availability=False,
        skills=["Furniture Repair", "Door Fitting", "Polishing"]
    ),
    Provider(
        id="prov_khi_05",
        name="Bilal Auto Mechanic",
        service_type="Mechanic",
        location=Location(lat=24.8532, lng=67.0166),
        address="Saddar Auto Market, Karachi",
        rating=4.9,
        on_time_score=99.0,
        cancellation_rate=0.5,
        base_rate=1500.0,
        availability=True,
        skills=["Engine Diagnostics", "Oil Change", "Brake Repair"]
    ),
    Provider(
        id="prov_khi_06",
        name="Kamran AC Tech",
        service_type="AC Technician",
        location=Location(lat=24.8143, lng=67.0435),
        address="Clifton Block 4, Karachi",
        rating=4.7,
        on_time_score=96.0,
        cancellation_rate=2.0,
        base_rate=1500.0,
        availability=True,
        skills=["Split AC Gas Refill", "AC Servicing", "Installation"]
    ),
    Provider(
        id="prov_khi_07",
        name="Zainab Beauty Parlour Home Service",
        service_type="Beautician",
        location=Location(lat=24.9204, lng=67.1344),
        address="Malir Cantt, Karachi",
        rating=4.9,
        on_time_score=98.5,
        cancellation_rate=1.0,
        base_rate=2000.0,
        availability=True,
        skills=["Bridal Makeup", "Hair Styling", "Facial"]
    ),
    Provider(
        id="prov_khi_08",
        name="Usman Painter",
        service_type="Painter",
        location=Location(lat=24.8948, lng=67.0261),
        address="Nazimabad No 2, Karachi",
        rating=4.3,
        on_time_score=85.0,
        cancellation_rate=4.0,
        base_rate=900.0,
        availability=True,
        skills=["Wall Painting", "Texture Painting", "Polishing"]
    ),
    Provider(
        id="prov_khi_09",
        name="Naseem Tailors",
        service_type="Tailor",
        location=Location(lat=24.8788, lng=67.0142),
        address="Tariq Road, Karachi",
        rating=4.8,
        on_time_score=97.0,
        cancellation_rate=1.5,
        base_rate=1000.0,
        availability=True,
        skills=["Mens Shalwar Kameez", "Alteration", "Suiting"]
    ),
    Provider(
        id="prov_khi_10",
        name="Farhan Pest Control",
        service_type="Pest Control",
        location=Location(lat=24.8286, lng=67.0705),
        address="Korangi Industrial Area, Karachi",
        rating=4.5,
        on_time_score=94.0,
        cancellation_rate=2.5,
        base_rate=2500.0,
        availability=True,
        skills=["Fumigation", "Termite Proofing", "Bedbug Removal"]
    ),

    # Lahore Providers
    Provider(
        id="prov_lhr_01",
        name="Rizwan AC & Fridge Services",
        service_type="Appliance Repair",
        location=Location(lat=31.4697, lng=74.2728),
        address="Johar Town Phase 2, Lahore",
        rating=4.7,
        on_time_score=93.0,
        cancellation_rate=3.0,
        base_rate=1000.0,
        availability=True,
        skills=["Fridge Repair", "AC Servicing", "Washing Machine Repair"]
    ),
    Provider(
        id="prov_lhr_02",
        name="Asif Plumber Specialist",
        service_type="Plumber",
        location=Location(lat=31.4810, lng=74.3030),
        address="Model Town, Lahore",
        rating=4.4,
        on_time_score=89.0,
        cancellation_rate=5.0,
        base_rate=700.0,
        availability=True,
        skills=["Geyser Repair", "Motor Installation", "Pipe Clogging"]
    ),
    Provider(
        id="prov_lhr_03",
        name="Ayesha Cooking Services",
        service_type="Chef/Cook",
        location=Location(lat=31.5204, lng=74.3587),
        address="Gulberg III, Lahore",
        rating=4.9,
        on_time_score=99.0,
        cancellation_rate=1.0,
        base_rate=1500.0,
        availability=False,
        skills=["Desi Food", "Continental", "Baking"]
    ),
    Provider(
        id="prov_lhr_04",
        name="Waqas Electric Works",
        service_type="Electrician",
        location=Location(lat=31.4790, lng=74.4168),
        address="DHA Phase 5, Lahore",
        rating=4.8,
        on_time_score=96.5,
        cancellation_rate=1.5,
        base_rate=1200.0,
        availability=True,
        skills=["Solar Panel Installation", "UPS Repair", "House Wiring"]
    ),
    Provider(
        id="prov_lhr_05",
        name="Chaudhry Wood Works",
        service_type="Carpenter",
        location=Location(lat=31.5497, lng=74.3436),
        address="Ichhra Market, Lahore",
        rating=4.5,
        on_time_score=90.0,
        cancellation_rate=4.0,
        base_rate=1000.0,
        availability=True,
        skills=["Custom Furniture", "Kitchen Cabinets", "Wood Polishing"]
    ),
    Provider(
        id="prov_lhr_06",
        name="Sana Home Cleaning",
        service_type="Maid",
        location=Location(lat=31.5102, lng=74.3441),
        address="Cavalry Ground, Lahore",
        rating=4.6,
        on_time_score=95.0,
        cancellation_rate=2.0,
        base_rate=600.0,
        availability=True,
        skills=["Deep Cleaning", "Dusting", "Dishwashing"]
    ),
    Provider(
        id="prov_lhr_07",
        name="Bhatti Generator Services",
        service_type="Mechanic",
        location=Location(lat=31.5820, lng=74.3294),
        address="Shahdara, Lahore",
        rating=4.3,
        on_time_score=88.0,
        cancellation_rate=6.0,
        base_rate=1500.0,
        availability=True,
        skills=["Generator Repair", "Maintenance", "Oil Change"]
    ),
    Provider(
        id="prov_lhr_08",
        name="Muneeb Glass Works",
        service_type="Glass Worker",
        location=Location(lat=31.4504, lng=74.2982),
        address="Township, Lahore",
        rating=4.4,
        on_time_score=92.0,
        cancellation_rate=3.5,
        base_rate=800.0,
        availability=True,
        skills=["Window Glass", "Mirrors", "Aluminum Windows"]
    ),
    Provider(
        id="prov_lhr_09",
        name="Lahore CCTV Solutions",
        service_type="Security Technician",
        location=Location(lat=31.5283, lng=74.3313),
        address="Jail Road, Lahore",
        rating=4.8,
        on_time_score=97.0,
        cancellation_rate=1.0,
        base_rate=2000.0,
        availability=True,
        skills=["Camera Installation", "DVR Setup", "Networking"]
    ),
    Provider(
        id="prov_lhr_10",
        name="Faisal Roza-e-Deewar (Masons)",
        service_type="Mason",
        location=Location(lat=31.5701, lng=74.3120),
        address="Ravi Road, Lahore",
        rating=4.2,
        on_time_score=85.0,
        cancellation_rate=5.0,
        base_rate=1200.0,
        availability=True,
        skills=["Brick Laying", "Plastering", "Tile Fixing"]
    ),

    # Islamabad Providers
    Provider(
        id="prov_isb_01",
        name="Jamil Electric & Solar",
        service_type="Electrician",
        location=Location(lat=33.7058, lng=73.0437),
        address="Blue Area, Islamabad",
        rating=4.9,
        on_time_score=98.0,
        cancellation_rate=0.5,
        base_rate=1500.0,
        availability=True,
        skills=["Solar Setup", "UPS", "Commercial Wiring"]
    ),
    Provider(
        id="prov_isb_02",
        name="Shafiq Handyman Services",
        service_type="Handyman",
        location=Location(lat=33.7182, lng=73.0531),
        address="F-7 Markaz, Islamabad",
        rating=4.8,
        on_time_score=96.0,
        cancellation_rate=1.0,
        base_rate=1000.0,
        availability=True,
        skills=["General Repairs", "Picture Hanging", "TV Mounting"]
    ),
    Provider(
        id="prov_isb_03",
        name="Nida House Care",
        service_type="Maid",
        location=Location(lat=33.6844, lng=73.0479),
        address="G-8 Markaz, Islamabad",
        rating=4.5,
        on_time_score=94.0,
        cancellation_rate=2.0,
        base_rate=800.0,
        availability=True,
        skills=["Housekeeping", "Cooking", "Babysitting"]
    ),
    Provider(
        id="prov_isb_04",
        name="Raza Plumbers",
        service_type="Plumber",
        location=Location(lat=33.6518, lng=73.1566),
        address="PWD Housing Society, Islamabad",
        rating=4.4,
        on_time_score=91.0,
        cancellation_rate=3.5,
        base_rate=900.0,
        availability=True,
        skills=["Sanitary Fitting", "Geyser Repair", "Water Pump"]
    ),
    Provider(
        id="prov_isb_05",
        name="Capital Car Mechanics",
        service_type="Mechanic",
        location=Location(lat=33.6669, lng=73.0163),
        address="G-11 Markaz, Islamabad",
        rating=4.7,
        on_time_score=95.0,
        cancellation_rate=2.5,
        base_rate=2000.0,
        availability=True,
        skills=["Car Inspection", "AC Repair", "Tune Up"]
    ),
    Provider(
        id="prov_isb_06",
        name="Hassan Aluminum & Glass",
        service_type="Glass Worker",
        location=Location(lat=33.6938, lng=72.9851),
        address="F-11 Markaz, Islamabad",
        rating=4.6,
        on_time_score=93.0,
        cancellation_rate=2.0,
        base_rate=1200.0,
        availability=True,
        skills=["Aluminum Partitions", "Glass Doors", "Windows"]
    ),
    Provider(
        id="prov_isb_07",
        name="Saqib Painter Pros",
        service_type="Painter",
        location=Location(lat=33.7294, lng=73.0931),
        address="Bara Kahu, Islamabad",
        rating=4.3,
        on_time_score=88.0,
        cancellation_rate=4.5,
        base_rate=800.0,
        availability=False,
        skills=["Exterior Painting", "Interior Painting", "Distemper"]
    ),
    Provider(
        id="prov_isb_08",
        name="Isloo Packers & Movers",
        service_type="Movers",
        location=Location(lat=33.6425, lng=73.0640),
        address="I-8 Markaz, Islamabad",
        rating=4.8,
        on_time_score=97.0,
        cancellation_rate=1.0,
        base_rate=5000.0,
        availability=True,
        skills=["Home Relocation", "Office Shifting", "Packing"]
    ),
    Provider(
        id="prov_isb_09",
        name="Faizan Gardening Services",
        service_type="Gardener",
        location=Location(lat=33.7145, lng=73.0560),
        address="F-6, Islamabad",
        rating=4.9,
        on_time_score=99.0,
        cancellation_rate=0.0,
        base_rate=1000.0,
        availability=True,
        skills=["Lawn Mowing", "Plant Care", "Landscaping"]
    ),
    Provider(
        id="prov_isb_10",
        name="Amir IT Support",
        service_type="IT Technician",
        location=Location(lat=33.6593, lng=73.0238),
        address="G-10 Markaz, Islamabad",
        rating=4.7,
        on_time_score=96.0,
        cancellation_rate=2.0,
        base_rate=1500.0,
        availability=True,
        skills=["WiFi Setup", "PC Repair", "Software Installation"]
    ),
]

# --- MOCK USERS ---
MOCK_USERS: List[User] = [
    User(id="user_01", phone="+923001234567", preferred_language="ur"),
    User(id="user_02", phone="+923339876543", preferred_language="en"),
    User(id="user_03", phone="+923451122334", preferred_language="ur"),
]

# --- MOCK BOOKINGS ---
MOCK_BOOKINGS: List[Booking] = [
    Booking(
        id="book_01",
        user_id="user_01",
        provider_id="prov_khi_01",
        service_type="Plumber",
        status=BookingStatus.COMPLETED,
        price_breakdown=PriceBreakdown(base_fare=800.0, taxes=40.0, total=840.0)
    ),
    Booking(
        id="book_02",
        user_id="user_02",
        provider_id="prov_lhr_03",
        service_type="Chef/Cook",
        status=BookingStatus.IN_PROGRESS,
        price_breakdown=PriceBreakdown(base_fare=1500.0, taxes=75.0, total=1575.0)
    ),
    Booking(
        id="book_03",
        user_id="user_03",
        provider_id="prov_isb_01",
        service_type="Electrician",
        status=BookingStatus.PENDING,
        price_breakdown=PriceBreakdown(base_fare=1500.0, taxes=75.0, total=1575.0)
    )
]

# --- MOCK DISPUTES ---
MOCK_DISPUTES: List[Dispute] = [
    Dispute(
        id="disp_01",
        booking_id="book_01",
        reason="Provider was 1 hour late and did not complete the job properly.",
        status=DisputeStatus.IN_REVIEW,
        resolution=None
    )
]
