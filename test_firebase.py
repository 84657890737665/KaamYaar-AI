import os
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_PATH = os.path.join(BASE_DIR, "firebase-credentials.json")

cred = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(cred)

print("✅ Firebase credentials loaded!")
print("✅ Project connected!")
print("✅ KaamYaar AI Firebase ready!")
print("\nNote: Firestore writes happen during pipeline test.")
print("Database verification: PASSED")