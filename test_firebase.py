import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
firebase_admin.initialize_app(cred)

db = firestore.client()

# Test: ek document write karo
db.collection("test").document("ping").set({"status": "connected", "app": "KaamYaar AI"})
print("✅ Firebase connected successfully!")

# Read back
doc = db.collection("test").document("ping").get()
print(f"✅ Read back: {doc.to_dict()}")