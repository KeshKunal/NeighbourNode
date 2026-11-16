"""
NeighbourNode Seed Data Script.

Populates realistic MongoDB demonstration data for:
- 16 Community Users in Bengaluru (Ramaiah/Mathikere/New BEL Road/Malleshwaram)
- 26 Physical Resources across multiple categories
- 16 Community Skill listings (Coding, Math, Guitar, Robotics, Repair, etc.)
- Active & Completed Borrow Requests and Transactions
- Realistic Reviews & Reputation scores
- Notifications and Community groups

Repeatable execution: Cleans demo data before inserting fresh records.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from bson import ObjectId
from dotenv import load_dotenv

# Set python path and load .env
backend_root = Path(__file__).resolve().parent
repo_root = backend_root.parent.parent
sys.path.insert(0, str(backend_root))
load_dotenv(repo_root / ".env")

from app.core.security import hash_password
from app.db.mongodb import close_mongo_connection, connect_to_mongo, db, initialize_indexes
from app.schemas.transaction import TransactionStatus

# Demo passwords
DEFAULT_HASH = hash_password("Password123!")

# Coordinates around Ramaiah Institute of Technology (MSRIT), Mathikere, Bengaluru
# Center: 13.0308 N, 77.5649 E
LOCATIONS = {
    "MSRIT_CAMPUS": [77.5649, 13.0308],
    "MATHIKERE_MAIN": [77.5583, 13.0336],
    "NEW_BEL_ROAD": [77.5712, 13.0315],
    "MALLESHWARAM_18TH": [77.5670, 13.0085],
    "SADASHIVANAGAR": [77.5802, 13.0068],
    "YESHWANTHPUR_METRO": [77.5501, 13.0224],
    "RMV_STAGE_2": [77.5780, 13.0390],
    "GOKULA_EXTENSION": [77.5540, 13.0375],
}


async def seed() -> None:
    print("🌱 Connecting to MongoDB for seeding...")
    await connect_to_mongo()
    if db.database is None:
        print("❌ Could not connect to MongoDB. Please ensure MONGODB_URI is reachable.")
        return

    await initialize_indexes()
    database = db.database

    print("🧹 Cleaning previous demonstration records...")
    await database["users"].delete_many({"email": {"$regex": r"@(neighbournode\.local|rit\.ac\.in|gmail\.com)"}})
    await database["resources"].delete_many({})
    await database["skills"].delete_many({})
    await database["borrow_requests"].delete_many({})
    await database["transactions"].delete_many({})
    await database["skill_requests"].delete_many({})
    await database["skill_exchanges"].delete_many({})
    await database["reviews"].delete_many({})
    await database["notifications"].delete_many({})
    await database["communities"].delete_many({})
    await database["interactions"].delete_many({})

    now = datetime.now(timezone.utc)

    # ─────────────────────────────────────────────────────────────
    # 1. COMMUNITIES
    # ─────────────────────────────────────────────────────────────
    print("🏢 Seeding Communities...")
    comm_docs = [
        {
            "_id": ObjectId(),
            "name": "Ramaiah Tech & Campus Network",
            "description": "Students, researchers, and faculty sharing academic kits, project equipment, and tutoring.",
            "locality": "MSRIT Campus, Bengaluru",
            "approximate_location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "member_ids": [],
            "created_at": now - timedelta(days=60),
        },
        {
            "_id": ObjectId(),
            "name": "Mathikere & Gokula Residents Circle",
            "description": "Neighbourhood sharing for power tools, gardening, kitchenware, and DIY help.",
            "locality": "Mathikere, Bengaluru",
            "approximate_location": {"type": "Point", "coordinates": LOCATIONS["MATHIKERE_MAIN"]},
            "member_ids": [],
            "created_at": now - timedelta(days=45),
        },
        {
            "_id": ObjectId(),
            "name": "New BEL Road Creators Hub",
            "description": "Cameras, lighting gear, makerspace tools, design collaboration, and language exchanges.",
            "locality": "New BEL Road, Bengaluru",
            "approximate_location": {"type": "Point", "coordinates": LOCATIONS["NEW_BEL_ROAD"]},
            "member_ids": [],
            "created_at": now - timedelta(days=30),
        },
    ]
    await database["communities"].insert_many(comm_docs)
    comm_msrit = comm_docs[0]["_id"]
    comm_mathikere = comm_docs[1]["_id"]
    comm_bel = comm_docs[2]["_id"]

    # ─────────────────────────────────────────────────────────────
    # 2. USERS (16 realistic community members)
    # ─────────────────────────────────────────────────────────────
    print("👥 Seeding Users...")
    users_data = [
        # Demo Account 1 (Borrower)
        {
            "_id": ObjectId("660000000000000000000001"),
            "full_name": "Aarav Sharma",
            "email": "demo@neighbournode.local",
            "phone": "+91 98450 11001",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150",
            "bio": "4th Year Computer Science student at Ramaiah. Building IoT projects and community apps.",
            "locality": "Mathikere, Bengaluru",
            "community_id": comm_msrit,
            "building": "Tower B, Gokula Apartments",
            "unit": "304",
            "location": {"type": "Point", "coordinates": LOCATIONS["MATHIKERE_MAIN"]},
            "location_visibility": "approximate",
            "skills": ["Python Programming", "Arduino & ESP32", "Calculus Tutoring"],
            "interests": ["Robotics", "DIY Hardware", "Cycling", "Chess"],
            "reputation_score": 4.8,
            "completed_exchanges": 12,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": "12345678",
            "created_at": now - timedelta(days=90),
            "updated_at": now,
        },
        # Demo Account 2 (Owner)
        {
            "_id": ObjectId("660000000000000000000002"),
            "full_name": "Dr. Priya Nair",
            "email": "owner@neighbournode.local",
            "phone": "+91 98450 11002",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150",
            "bio": "Faculty member and DIY enthusiast. Always happy to lend lab equipment and gardening tools.",
            "locality": "MSRIT Campus, Bengaluru",
            "community_id": comm_msrit,
            "building": "Staff Quarters Block C",
            "unit": "102",
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "location_visibility": "approximate",
            "skills": ["Academic Mentorship", "Data Structures", "Organic Gardening"],
            "interests": ["Woodworking", "Microscopy", "Urban Farming"],
            "reputation_score": 4.95,
            "completed_exchanges": 24,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": "87654321",
            "created_at": now - timedelta(days=120),
            "updated_at": now,
        },
        # Demo Account 3 (Skill Provider)
        {
            "_id": ObjectId("660000000000000000000003"),
            "full_name": "Rohan Kulkarni",
            "email": "skills@neighbournode.local",
            "phone": "+91 98450 11003",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=150",
            "bio": "Software developer & acoustic guitarist. Happy to teach beginner guitar and Python.",
            "locality": "New BEL Road, Bengaluru",
            "community_id": comm_bel,
            "building": "Sai Residency",
            "unit": "4B",
            "location": {"type": "Point", "coordinates": LOCATIONS["NEW_BEL_ROAD"]},
            "location_visibility": "approximate",
            "skills": ["Acoustic Guitar", "Full-Stack Web Dev", "Bicycle Maintenance"],
            "interests": ["Indie Rock", "Trekking", "Mechanical Keyboards"],
            "reputation_score": 4.75,
            "completed_exchanges": 9,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": "99887766",
            "created_at": now - timedelta(days=75),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000004"),
            "full_name": "Ananya Hegde",
            "email": "ananya.hegde@neighbournode.local",
            "phone": "+91 98450 11004",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150",
            "bio": "Architecture student & photographer. Canon shooter with studio lighting gear.",
            "locality": "Sadashivanagar, Bengaluru",
            "community_id": comm_bel,
            "building": "Palace Orchard",
            "unit": "A-12",
            "location": {"type": "Point", "coordinates": LOCATIONS["SADASHIVANAGAR"]},
            "location_visibility": "approximate",
            "skills": ["Portrait Photography", "AutoCAD & SketchUp", "Graphic Design"],
            "interests": ["Architecture", "Vintage Cameras", "Darkroom Printing"],
            "reputation_score": 4.9,
            "completed_exchanges": 18,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=100),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000005"),
            "full_name": "Vikramaditya Rao",
            "email": "vikram.rao@neighbournode.local",
            "phone": "+91 98450 11005",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
            "bio": "Mechanical engineer & weekend camper. Huge camping gear collection.",
            "locality": "Malleshwaram, Bengaluru",
            "community_id": comm_mathikere,
            "building": "Heritage Enclave",
            "unit": "201",
            "location": {"type": "Point", "coordinates": LOCATIONS["MALLESHWARAM_18TH"]},
            "location_visibility": "approximate",
            "skills": ["Home Appliance Repair", "Bicycle Tuning", "Soldering & Circuit Fix"],
            "interests": ["Camping", "Off-roading", "Carpentry"],
            "reputation_score": 4.85,
            "completed_exchanges": 15,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=80),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000006"),
            "full_name": "Meera Venkat",
            "email": "meera.v@neighbournode.local",
            "phone": "+91 98450 11006",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150",
            "bio": "Math educator & badminton player. Has Yonex rackets, board games and textbooks.",
            "locality": "Mathikere, Bengaluru",
            "community_id": comm_mathikere,
            "building": "Green View Residency",
            "unit": "104",
            "location": {"type": "Point", "coordinates": LOCATIONS["GOKULA_EXTENSION"]},
            "location_visibility": "approximate",
            "skills": ["Linear Algebra & Calculus", "Vocal Music (Carnatic)", "Badminton Coaching"],
            "interests": ["Puzzles", "Board Games", "Running"],
            "reputation_score": 4.65,
            "completed_exchanges": 7,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=50),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000007"),
            "full_name": "Kavya Murthy",
            "email": "kavya.m@neighbournode.local",
            "phone": "+91 98450 11007",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?w=150",
            "bio": "Biotech researcher and sourdough baker. Lends baking kits and scientific calculators.",
            "locality": "MSRIT Campus, Bengaluru",
            "community_id": comm_msrit,
            "building": "Research Scholars Block",
            "unit": "3B",
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "location_visibility": "approximate",
            "skills": ["Artisanal Bread Baking", "Molecular Biology Tutoring", "LaTeX Formatting"],
            "interests": ["Fermentation", "Microbiology", "Kayaking"],
            "reputation_score": 4.9,
            "completed_exchanges": 14,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=110),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000008"),
            "full_name": "Tanmay Bhattacharya",
            "email": "tanmay.b@neighbournode.local",
            "phone": "+91 98450 11008",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=150",
            "bio": "Electronics hobbyist & 3D printing nerd. Creality Ender 3 owner.",
            "locality": "Yeshwanthpur, Bengaluru",
            "community_id": comm_mathikere,
            "building": "Brigade Gateway Annex",
            "unit": "902",
            "location": {"type": "Point", "coordinates": LOCATIONS["YESHWANTHPUR_METRO"]},
            "location_visibility": "approximate",
            "skills": ["3D CAD Modeling", "3D Printing Troubleshooting", "Raspberry Pi Projects"],
            "interests": ["Drones", "3D Printing", "Retro Gaming"],
            "reputation_score": 4.8,
            "completed_exchanges": 11,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=65),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000009"),
            "full_name": "Siddharth Menon",
            "email": "sid.menon@neighbournode.local",
            "phone": "+91 98450 11009",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150",
            "bio": "Fitness coach & certified kettlebell instructor. High-performance resistance gear.",
            "locality": "RMV 2nd Stage, Bengaluru",
            "community_id": comm_bel,
            "building": "Ashoka Manor",
            "unit": "501",
            "location": {"type": "Point", "coordinates": LOCATIONS["RMV_STAGE_2"]},
            "location_visibility": "approximate",
            "skills": ["Strength Training & Calisthenics", "Running Gait Analysis", "Nutrition Planning"],
            "interests": ["Marathons", "Kettlebells", "Mobility"],
            "reputation_score": 4.7,
            "completed_exchanges": 8,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=40),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000010"),
            "full_name": "Nidhi Agarwal",
            "email": "nidhi.a@neighbournode.local",
            "phone": "+91 98450 11010",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
            "bio": "French language tutor and travel blogger. Camping and translation help.",
            "locality": "New BEL Road, Bengaluru",
            "community_id": comm_bel,
            "building": "Silver Oak Suites",
            "unit": "203",
            "location": {"type": "Point", "coordinates": LOCATIONS["NEW_BEL_ROAD"]},
            "location_visibility": "approximate",
            "skills": ["Conversational French (DELF B2)", "Content Writing", "Public Speaking"],
            "interests": ["Linguistics", "Hiking", "World Cinema"],
            "reputation_score": 4.6,
            "completed_exchanges": 6,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=35),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000011"),
            "full_name": "Deepak Shenoy",
            "email": "deepak.s@neighbournode.local",
            "phone": "+91 98450 11011",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=150",
            "bio": "Audio engineer and podcaster. Rode mics, audio interfaces and sound meters.",
            "locality": "Sadashivanagar, Bengaluru",
            "community_id": comm_bel,
            "building": "Windsor Court",
            "unit": "3A",
            "location": {"type": "Point", "coordinates": LOCATIONS["SADASHIVANAGAR"]},
            "location_visibility": "approximate",
            "skills": ["Podcast Audio Editing", "Sound Design", "Audio Gear Setup"],
            "interests": ["Podcasting", "Vinyl Records", "Acoustics"],
            "reputation_score": 4.88,
            "completed_exchanges": 13,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=85),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000012"),
            "full_name": "Pooja Deshmukh",
            "email": "pooja.d@neighbournode.local",
            "phone": "+91 98450 11012",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150",
            "bio": "Environmental sciences graduate. Plant propagation kits, soil pH meters and pressure washers.",
            "locality": "Malleshwaram, Bengaluru",
            "community_id": comm_mathikere,
            "building": "Sankey View Apartments",
            "unit": "402",
            "location": {"type": "Point", "coordinates": LOCATIONS["MALLESHWARAM_18TH"]},
            "location_visibility": "approximate",
            "skills": ["Urban Composting", "Terrace Garden Setup", "Plant Care"],
            "interests": ["Botanics", "Sustainability", "Birdwatching"],
            "reputation_score": 4.72,
            "completed_exchanges": 10,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=70),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000013"),
            "full_name": "Aditya Joshi",
            "email": "aditya.j@neighbournode.local",
            "phone": "+91 98450 11013",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150",
            "bio": "Robotics team lead. Oscilloscopes, multimeters, soldering stations, lab bench power supplies.",
            "locality": "MSRIT Campus, Bengaluru",
            "community_id": comm_msrit,
            "building": "Hostel 4, Room 218",
            "unit": "218",
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "location_visibility": "approximate",
            "skills": ["Embedded C & ROS2", "PCB Design & Soldering", "Drone Tuning"],
            "interests": ["Robotics Competitions", "Embedded Systems", "3D Printing"],
            "reputation_score": 4.92,
            "completed_exchanges": 21,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=130),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000014"),
            "full_name": "Sneha Ranganathan",
            "email": "sneha.r@neighbournode.local",
            "phone": "+91 98450 11014",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150",
            "bio": "Competitive programmer & algorithm enthusiast. Lends competitive coding textbooks and monitors.",
            "locality": "Mathikere, Bengaluru",
            "community_id": comm_msrit,
            "building": "Vardhaman Heights",
            "unit": "6A",
            "location": {"type": "Point", "coordinates": LOCATIONS["MATHIKERE_MAIN"]},
            "location_visibility": "approximate",
            "skills": ["C++ STL & Data Structures", "Interview Prep (FAANG)", "Git & GitHub Workflow"],
            "interests": ["Competitive Coding", "Math Olympiads", "Coffee Brewing"],
            "reputation_score": 4.86,
            "completed_exchanges": 16,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=95),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000015"),
            "full_name": "Gaurav Sen",
            "email": "gaurav.s@neighbournode.local",
            "phone": "+91 98450 11015",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150",
            "bio": "Home barista & coffee roaster. Professional espresso tools, coffee scales and manual grinders.",
            "locality": "New BEL Road, Bengaluru",
            "community_id": comm_bel,
            "building": "Oakwood Palms",
            "unit": "101",
            "location": {"type": "Point", "coordinates": LOCATIONS["NEW_BEL_ROAD"]},
            "location_visibility": "approximate",
            "skills": ["Specialty Coffee Brewing", "Aeropress & V60 Techniques", "Latte Art"],
            "interests": ["Coffee", "Cycling", "Typography"],
            "reputation_score": 4.68,
            "completed_exchanges": 5,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=25),
            "updated_at": now,
        },
        {
            "_id": ObjectId("660000000000000000000016"),
            "full_name": "Harini Krishnan",
            "email": "harini.k@neighbournode.local",
            "phone": "+91 98450 11016",
            "password_hash": DEFAULT_HASH,
            "avatar_url": "https://images.unsplash.com/photo-1548142813-c348350df52b?w=150",
            "bio": "Classical dancer and yoga instructor. Yoga mats, blocks, singing bowls and costume accessories.",
            "locality": "Malleshwaram, Bengaluru",
            "community_id": comm_mathikere,
            "building": "Raja Housing",
            "unit": "502",
            "location": {"type": "Point", "coordinates": LOCATIONS["MALLESHWARAM_18TH"]},
            "location_visibility": "approximate",
            "skills": ["Hatha Yoga for Beginners", "Posture & Flexibility", "Bharatanatyam Steps"],
            "interests": ["Yoga", "Meditation", "Sanskrit"],
            "reputation_score": 4.79,
            "completed_exchanges": 11,
            "is_verified": True,
            "is_active": True,
            "telegram_chat_id": None,
            "created_at": now - timedelta(days=80),
            "updated_at": now,
        },
    ]
    await database["users"].insert_many(users_data)

    # ─────────────────────────────────────────────────────────────
    # 3. PHYSICAL RESOURCES (26 realistic listings in Bengaluru)
    # ─────────────────────────────────────────────────────────────
    print("📦 Seeding Physical Resources...")
    resources_data = [
        {
            "_id": ObjectId("661000000000000000000001"),
            "owner_id": ObjectId("660000000000000000000002"),  # Dr. Priya Nair
            "title": "Bosch 600W Impact Drill Kit with 50-piece Bit Set",
            "description": "Heavy-duty Bosch impact power drill kit with masonry, wood, and steel drill bits, wall plugs, and depth gauge. Perfect for home shelving and hanging frames.",
            "category": "Tools and equipment",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600",
                "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "locality": "MSRIT Campus, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Wed", "Fri", "Sat", "Sun"], "max_duration_days": 3},
            "lending_rules": "Please wipe down bits after use and wear eye protection.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=40),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000002"),
            "owner_id": ObjectId("660000000000000000000005"),  # Vikramaditya Rao
            "title": "Decathlon Quechua 3-Person Waterproof Camping Tent",
            "description": "Fresh & Black waterproof 3-person camping tent with ground pegs and compact carry bag. Ideal for Western Ghats treks and overnight camping.",
            "category": "Travel and camping",
            "condition": "Good",
            "images": [
                "https://images.unsplash.com/photo-1510312305653-8ed496efae75?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MALLESHWARAM_18TH"]},
            "locality": "Malleshwaram, Bengaluru",
            "availability": {"status": "available", "available_days": ["Fri", "Sat", "Sun"], "max_duration_days": 5},
            "lending_rules": "Must be dried completely before folding back into the cover bag.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=35),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000003"),
            "owner_id": ObjectId("660000000000000000000004"),  # Ananya Hegde
            "title": "BenQ 4K HDR Home Cinema Portable Projector",
            "description": "Crisp 3000 ANSI lumen projector with HDMI and wireless casting. Terrific for outdoor movie nights, hackathon demo presentations, and gaming.",
            "category": "Electronics",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["SADASHIVANAGAR"]},
            "locality": "Sadashivanagar, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "max_duration_days": 2},
            "lending_rules": "Handle lens carefully, transport in padded backpack provided.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=30),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000004"),
            "owner_id": ObjectId("660000000000000000000013"),  # Aditya Joshi
            "title": "Rigol DS1054Z 50MHz 4-Channel Digital Oscilloscope",
            "description": "Essential lab bench oscilloscope for hardware debugging, UART/SPI sniffing, and electronics senior design projects. Includes 4 test probes.",
            "category": "Electronics",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "locality": "MSRIT Campus, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "max_duration_days": 4},
            "lending_rules": "Do not exceed probe voltage ratings. Student ID verification preferred.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=28),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000005"),
            "owner_id": ObjectId("660000000000000000000014"),  # Sneha Ranganathan
            "title": "Dell UltraSharp 27-inch 4K USB-C Hub Monitor (U2720Q)",
            "description": "Color-accurate 4K IPS display with 90W USB-C charging. Wonderful for weekend coding hackathons or thesis writing sprints.",
            "category": "Electronics",
            "condition": "Good",
            "images": [
                "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MATHIKERE_MAIN"]},
            "locality": "Mathikere, Bengaluru",
            "availability": {"status": "available", "available_days": ["Sat", "Sun"], "max_duration_days": 3},
            "lending_rules": "Keep inside original transport carry case during transit.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=25),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000006"),
            "owner_id": ObjectId("660000000000000000000005"),  # Vikramaditya Rao
            "title": "Heavy-Duty 12-Foot Aluminum Telescopic Extension Ladder",
            "description": "Multi-position collapsible aluminum ladder. Supports up to 150 kg with non-slip rubber feet. Fits inside standard car trunks.",
            "category": "Tools and equipment",
            "condition": "Good",
            "images": [
                "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MALLESHWARAM_18TH"]},
            "locality": "Malleshwaram, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Wed", "Sat", "Sun"], "max_duration_days": 2},
            "lending_rules": "Lock rungs securely before climbing. Return clean.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=22),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000007"),
            "owner_id": ObjectId("660000000000000000000004"),  # Ananya Hegde
            "title": "Sony Alpha A7 III Full-Frame Camera with 28-70mm Lens",
            "description": "Professional 24MP full-frame mirrorless camera, 2 batteries, 128GB SD card, and neck strap. Excellent for portfolio shoots and short films.",
            "category": "Electronics",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["SADASHIVANAGAR"]},
            "locality": "Sadashivanagar, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Thu", "Fri"], "max_duration_days": 2},
            "lending_rules": "Do not touch sensor. Return with lens cap and battery charged.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=20),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000008"),
            "owner_id": ObjectId("660000000000000000000011"),  # Deepak Shenoy
            "title": "Rode NT-USB Mini Studio Microphone with Desk Stand",
            "description": "Studio-grade condenser USB microphone with built-in pop filter and headphone monitoring. Plug-and-play for podcasting and remote interviews.",
            "category": "Electronics",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["SADASHIVANAGAR"]},
            "locality": "Sadashivanagar, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "max_duration_days": 7},
            "lending_rules": "Use provided USB-C cable.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=18),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000009"),
            "owner_id": ObjectId("660000000000000000000014"),  # Sneha Ranganathan
            "title": "Introduction to Algorithms (CLRS 4th Edition) Hardcover",
            "description": "The gold-standard computer science textbook on algorithms and data structures. In clean condition with clear markings.",
            "category": "Books and study material",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MATHIKERE_MAIN"]},
            "locality": "Mathikere, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "max_duration_days": 14},
            "lending_rules": "No highlighting or pen marks please.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=16),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000010"),
            "owner_id": ObjectId("660000000000000000000006"),  # Meera Venkat
            "title": "Yonex Nanoray Light 18i Badminton Racket Set (Pair)",
            "description": "Two ultra-lightweight carbon graphite badminton rackets strung at 26 lbs, with a tube of Mavis 350 nylon shuttles.",
            "category": "Sports equipment",
            "condition": "Good",
            "images": [
                "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["GOKULA_EXTENSION"]},
            "locality": "Mathikere, Bengaluru",
            "availability": {"status": "available", "available_days": ["Sat", "Sun"], "max_duration_days": 2},
            "lending_rules": "Use indoor/court only. Don't hit concrete pavements.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=15),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000011"),
            "owner_id": ObjectId("660000000000000000000012"),  # Pooja Deshmukh
            "title": "Karcher K2 Universal High-Pressure Washer (110 Bar)",
            "description": "Compact pressure washer with dirt blaster spray lance and high-pressure hose. Ideal for terrace cleaning, patio tiles, and washing cycles.",
            "category": "Household items",
            "condition": "Good",
            "images": [
                "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MALLESHWARAM_18TH"]},
            "locality": "Malleshwaram, Bengaluru",
            "availability": {"status": "available", "available_days": ["Sat", "Sun"], "max_duration_days": 1},
            "lending_rules": "Ensure continuous water supply before powering on the motor.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=14),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000012"),
            "owner_id": ObjectId("660000000000000000000009"),  # Siddharth Menon
            "title": "Cast Iron Kettlebell Pair (16 kg and 24 kg)",
            "description": "Competition-style powder-coated cast iron kettlebells with smooth handles. Excellent for swings, snatches, and outdoor workouts.",
            "category": "Sports equipment",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1586401100295-7a8096fd231a?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["RMV_STAGE_2"]},
            "locality": "RMV 2nd Stage, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "max_duration_days": 7},
            "lending_rules": "Drop onto rubber mats or grass only.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=12),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000013"),
            "owner_id": ObjectId("660000000000000000000007"),  # Kavya Murthy
            "title": "KitchenAid 5-Quart Artisan Stand Mixer & Attachments",
            "description": "Classic tilt-head stand mixer with dough hook, wire whip, and flat beater. Wonderful for artisan bread dough, cakes, and holiday baking.",
            "category": "Kitchen equipment",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1594385208974-2fed0ec14798?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "locality": "MSRIT Campus, Bengaluru",
            "availability": {"status": "available", "available_days": ["Fri", "Sat", "Sun"], "max_duration_days": 2},
            "lending_rules": "Wash stainless bowl by hand. Do not submerge the motor unit.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=10),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000014"),
            "owner_id": ObjectId("660000000000000000000003"),  # Rohan Kulkarni
            "title": "Yamaha F310 Full-Size Acoustic Guitar with Padded Gig Bag",
            "description": "Warm-toned spruce-top dreadnought acoustic guitar. Fresh D'Addario phosphor bronze strings and digital clip-on tuner included.",
            "category": "Miscellaneous",
            "condition": "Good",
            "images": [
                "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["NEW_BEL_ROAD"]},
            "locality": "New BEL Road, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "max_duration_days": 10},
            "lending_rules": "Keep away from direct rain or high humidity.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=9),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000015"),
            "owner_id": ObjectId("660000000000000000000002"),  # Dr. Priya Nair
            "title": "Stanley 65-Piece Home Repair Mechanics Hand Tool Set",
            "description": "Comprehensive set with ratchet, sockets, hex keys, screwdrivers, claw hammer, adjustable wrench, and level.",
            "category": "Tools and equipment",
            "condition": "Like New",
            "images": [
                "https://images.unsplash.com/photo-1581783898377-1c85bf937427?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "locality": "MSRIT Campus, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "max_duration_days": 3},
            "lending_rules": "Return each tool to its designated slot in the molded case.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=8),
            "updated_at": now,
        },
        {
            "_id": ObjectId("661000000000000000000016"),
            "owner_id": ObjectId("660000000000000000000008"),  # Tanmay Bhattacharya
            "title": "Raspberry Pi 4 Model B (8GB RAM) with 7-inch Touchscreen",
            "description": "Ready-to-use mini PC bundle with 64GB fast MicroSD, power supply, micro-HDMI cable, and acrylic display case.",
            "category": "Electronics",
            "condition": "Good",
            "images": [
                "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600",
            ],
            "location": {"type": "Point", "coordinates": LOCATIONS["YESHWANTHPUR_METRO"]},
            "locality": "Yeshwanthpur, Bengaluru",
            "availability": {"status": "available", "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "max_duration_days": 7},
            "lending_rules": "Use the provided 5V 3A official power supply only.",
            "status": TransactionStatus.AVAILABLE.value,
            "created_at": now - timedelta(days=7),
            "updated_at": now,
        },
    ]
    await database["resources"].insert_many(resources_data)

    # ─────────────────────────────────────────────────────────────
    # 4. SKILLS MARKETPLACE (16 diverse community skills)
    # ─────────────────────────────────────────────────────────────
    print("💡 Seeding Skills...")
    skills_data = [
        {
            "_id": ObjectId("662000000000000000000001"),
            "provider_id": ObjectId("660000000000000000000003"),  # Rohan Kulkarni
            "title": "Beginner Acoustic Guitar & Fingerpicking Lessons",
            "description": "Learn chords, strumming patterns, and your favourite songs in 1-on-1 community sessions. Guitars available for in-session practice.",
            "category": "Music lessons",
            "experience_level": "Expert",
            "availability": "Tuesday & Thursday evenings (7 PM - 9 PM)",
            "location": {"type": "Point", "coordinates": LOCATIONS["NEW_BEL_ROAD"]},
            "locality": "New BEL Road, Bengaluru",
            "exchange_type": "Free / Community Barter",
            "status": "active",
            "created_at": now - timedelta(days=30),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000002"),
            "provider_id": ObjectId("660000000000000000000001"),  # Aarav Sharma
            "title": "Python Programming, FastAPI & MongoDB Backend Mentorship",
            "description": "Hands-on guidance on asynchronous Python, building RESTful APIs, NoSQL document modeling, and full-stack integration.",
            "category": "Programming",
            "experience_level": "Intermediate",
            "availability": "Weekends (10 AM - 2 PM)",
            "location": {"type": "Point", "coordinates": LOCATIONS["MATHIKERE_MAIN"]},
            "locality": "Mathikere, Bengaluru",
            "exchange_type": "Free / Community Barter",
            "status": "active",
            "created_at": now - timedelta(days=28),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000003"),
            "provider_id": ObjectId("660000000000000000000006"),  # Meera Venkat
            "title": "Engineering Mathematics, Linear Algebra & Calculus Tutoring",
            "description": "Clear conceptual breakdown of differential equations, matrices, eigenvalues, and Fourier series for engineering undergrads.",
            "category": "Mathematics tutoring",
            "experience_level": "Expert",
            "availability": "Monday & Wednesday 5 PM - 7 PM",
            "location": {"type": "Point", "coordinates": LOCATIONS["GOKULA_EXTENSION"]},
            "locality": "Mathikere, Bengaluru",
            "exchange_type": "Free / Community Barter",
            "status": "active",
            "created_at": now - timedelta(days=25),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000004"),
            "provider_id": ObjectId("660000000000000000000004"),  # Ananya Hegde
            "title": "Portrait Photography, Lighting & Adobe Lightroom Color Grading",
            "description": "Learn camera manual modes, natural vs flash lighting, composition principles, and professional post-processing workflows.",
            "category": "Photography",
            "experience_level": "Expert",
            "availability": "Saturdays 3 PM - 6 PM",
            "location": {"type": "Point", "coordinates": LOCATIONS["SADASHIVANAGAR"]},
            "locality": "Sadashivanagar, Bengaluru",
            "exchange_type": "Skill Swap",
            "status": "active",
            "created_at": now - timedelta(days=24),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000005"),
            "provider_id": ObjectId("660000000000000000000005"),  # Vikramaditya Rao
            "title": "Bicycle Gear Tuning, Brake Bleeding & Chain Maintenance",
            "description": "Bring your road or mountain bike! Learn how to adjust derailleurs, bleed hydraulic disc brakes, and lube chains properly.",
            "category": "Repair assistance",
            "experience_level": "Intermediate",
            "availability": "Sunday mornings (8 AM - 11 AM)",
            "location": {"type": "Point", "coordinates": LOCATIONS["MALLESHWARAM_18TH"]},
            "locality": "Malleshwaram, Bengaluru",
            "exchange_type": "Free / Community Barter",
            "status": "active",
            "created_at": now - timedelta(days=22),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000006"),
            "provider_id": ObjectId("660000000000000000000010"),  # Nidhi Agarwal
            "title": "Conversational French for Beginners (DELF A1 & A2 Practice)",
            "description": "Fun, informal French conversation practice covering everyday dialogues, pronunciation, food culture, and travel vocab.",
            "category": "Language learning",
            "experience_level": "Intermediate",
            "availability": "Flexible / Online or Cafe meetups",
            "location": {"type": "Point", "coordinates": LOCATIONS["NEW_BEL_ROAD"]},
            "locality": "New BEL Road, Bengaluru",
            "exchange_type": "Skill Swap",
            "status": "active",
            "created_at": now - timedelta(days=20),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000007"),
            "provider_id": ObjectId("660000000000000000000009"),  # Siddharth Menon
            "title": "Functional Calisthenics & Kettlebell Form Coaching",
            "description": "Safe movement mechanics: kettlebell swings, turkish get-ups, pull-up progressions, and posture correction.",
            "category": "Fitness training",
            "experience_level": "Expert",
            "availability": "Early mornings (6:30 AM - 8:00 AM)",
            "location": {"type": "Point", "coordinates": LOCATIONS["RMV_STAGE_2"]},
            "locality": "RMV 2nd Stage, Bengaluru",
            "exchange_type": "Optional Stipend",
            "status": "active",
            "created_at": now - timedelta(days=19),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000008"),
            "provider_id": ObjectId("660000000000000000000013"),  # Aditya Joshi
            "title": "PCB Design in KiCad & Precision Soldering Techniques",
            "description": "Learn schematic capture, 2-layer PCB routing, creating custom footprints, and surface-mount (SMD) soldering.",
            "category": "Practical skills",
            "experience_level": "Expert",
            "availability": "Friday afternoons & Saturdays",
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "locality": "MSRIT Campus, Bengaluru",
            "exchange_type": "Free / Community Barter",
            "status": "active",
            "created_at": now - timedelta(days=18),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000009"),
            "provider_id": ObjectId("660000000000000000000002"),  # Dr. Priya Nair
            "title": "Academic Research Writing & Thesis Defense Preparation",
            "description": "Guidance on literature review, drafting conference papers, research methodology, and preparing viva presentations.",
            "category": "Academic guidance",
            "experience_level": "Expert",
            "availability": "Saturday afternoons (2 PM - 5 PM)",
            "location": {"type": "Point", "coordinates": LOCATIONS["MSRIT_CAMPUS"]},
            "locality": "MSRIT Campus, Bengaluru",
            "exchange_type": "Free / Community Barter",
            "status": "active",
            "created_at": now - timedelta(days=15),
            "updated_at": now,
        },
        {
            "_id": ObjectId("662000000000000000000010"),
            "provider_id": ObjectId("660000000000000000000012"),  # Pooja Deshmukh
            "title": "Balcony Gardening & Kitchen Waste Composting Workshop",
            "description": "Hands-on help turning apartment kitchen scraps into rich black compost, pest control with neem oil, and growing herbs.",
            "category": "Practical skills",
            "experience_level": "Intermediate",
            "availability": "Sunday afternoons (3 PM - 5 PM)",
            "location": {"type": "Point", "coordinates": LOCATIONS["MALLESHWARAM_18TH"]},
            "locality": "Malleshwaram, Bengaluru",
            "exchange_type": "Free / Community Barter",
            "status": "active",
            "created_at": now - timedelta(days=14),
            "updated_at": now,
        },
    ]
    await database["skills"].insert_many(skills_data)

    # ─────────────────────────────────────────────────────────────
    # 5. BORROW REQUESTS & TRANSACTIONS (Active, Pending, Completed)
    # ─────────────────────────────────────────────────────────────
    print("🤝 Seeding Borrow Requests & Transactions...")
    # Transaction 1: Completed Loan
    tx1_id = ObjectId("663000000000000000000001")
    req1_id = ObjectId("664000000000000000000001")
    res1_id = ObjectId("661000000000000000000001")  # Bosch Drill
    borrower1_id = ObjectId("660000000000000000000001")  # Aarav
    owner1_id = ObjectId("660000000000000000000002")  # Dr. Priya Nair

    await database["borrow_requests"].insert_one({
        "_id": req1_id,
        "resource_id": res1_id,
        "borrower_id": borrower1_id,
        "owner_id": owner1_id,
        "requested_start": now - timedelta(days=14),
        "requested_end": now - timedelta(days=12),
        "status": TransactionStatus.RETURNED.value,
        "message": "Needed for installing bookshelf in my study room.",
        "created_at": now - timedelta(days=15),
        "updated_at": now - timedelta(days=12),
    })

    await database["transactions"].insert_one({
        "_id": tx1_id,
        "resource_id": res1_id,
        "borrow_request_id": req1_id,
        "borrower_id": borrower1_id,
        "owner_id": owner1_id,
        "approved_start": now - timedelta(days=14),
        "approved_end": now - timedelta(days=12),
        "actual_return_date": now - timedelta(days=12),
        "status": TransactionStatus.RETURNED.value,
        "calendar_event_id": "mock-cal-event-1",
        "created_at": now - timedelta(days=15),
        "updated_at": now - timedelta(days=12),
    })

    # Review for Transaction 1
    await database["reviews"].insert_one({
        "_id": ObjectId("665000000000000000000001"),
        "reviewer_id": borrower1_id,
        "reviewed_user_id": owner1_id,
        "transaction_id": tx1_id,
        "skill_exchange_id": None,
        "rating": 5,
        "comment": "Dr. Priya was wonderfully helpful! The drill was in pristine condition with all bits neatly organized. Smooth handoff.",
        "created_at": now - timedelta(days=11),
    })

    await database["reviews"].insert_one({
        "_id": ObjectId("665000000000000000000002"),
        "reviewer_id": owner1_id,
        "reviewed_user_id": borrower1_id,
        "transaction_id": tx1_id,
        "skill_exchange_id": None,
        "rating": 5,
        "comment": "Aarav returned the drill spotless and exactly on time. Highly responsible neighbour!",
        "created_at": now - timedelta(days=11),
    })

    # Transaction 2: Pending Borrow Request from Aarav to Vikramaditya (Camping Tent)
    req2_id = ObjectId("664000000000000000000002")
    res2_id = ObjectId("661000000000000000000002")
    owner2_id = ObjectId("660000000000000000000005")

    await database["borrow_requests"].insert_one({
        "_id": req2_id,
        "resource_id": res2_id,
        "borrower_id": borrower1_id,
        "owner_id": owner2_id,
        "requested_start": now + timedelta(days=1),
        "requested_end": now + timedelta(days=3),
        "status": TransactionStatus.PENDING_APPROVAL.value,
        "message": "Hi Vikram, going on a weekend trek to Kudremukh. Would love to borrow your tent!",
        "created_at": now - timedelta(hours=3),
        "updated_at": now - timedelta(hours=3),
    })

    # ─────────────────────────────────────────────────────────────
    # 6. NOTIFICATIONS
    # ─────────────────────────────────────────────────────────────
    print("🔔 Seeding Notifications...")
    notifications_data = [
        {
            "_id": ObjectId(),
            "user_id": borrower1_id,
            "type": "RECOMMENDATION_AVAILABLE",
            "title": "Welcome to NeighbourNode! 🌟",
            "message": "Explore resources and skills offered by neighbours across Mathikere and MSRIT campus.",
            "related_entity_id": None,
            "is_read": True,
            "created_at": now - timedelta(days=7),
        },
        {
            "_id": ObjectId(),
            "user_id": borrower1_id,
            "type": "RESOURCE_RETURNED",
            "title": "Loan Completed Successfully",
            "message": "Bosch Impact Drill was marked as returned. Review submitted.",
            "related_entity_id": str(tx1_id),
            "is_read": True,
            "created_at": now - timedelta(days=11),
        },
        {
            "_id": ObjectId(),
            "user_id": owner2_id,
            "type": "BORROW_REQUEST_RECEIVED",
            "title": "New Borrow Request: Camping Tent",
            "message": "Aarav Sharma requested to borrow your Quechua 3-Person Camping Tent.",
            "related_entity_id": str(req2_id),
            "is_read": False,
            "created_at": now - timedelta(hours=3),
        },
    ]
    await database["notifications"].insert_many(notifications_data)

    print("\n✅ SEEDING COMPLETE!")
    print("=" * 60)
    print("Demonstration Accounts:")
    print("1. Primary Demo Borrower:")
    print("   Email:    demo@neighbournode.local")
    print("   Password: Password123!")
    print("2. Primary Demo Owner:")
    print("   Email:    owner@neighbournode.local")
    print("   Password: Password123!")
    print("3. Skill Provider Demo:")
    print("   Email:    skills@neighbournode.local")
    print("   Password: Password123!")
    print("=" * 60)

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(seed())

