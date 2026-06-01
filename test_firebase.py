import firebase_admin
from firebase_admin import credentials, firestore

# Seedha path daalo — test ke liye
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
db.collection("test").document("ping").set({
    "status": "connected", 
    "app": "KaamYaar AI"
})
print("✅ Firebase connected!")

doc = db.collection("test").document("ping").get()
print(f"✅ Read: {doc.to_dict()}")
