import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_db = None

def get_firestore_client():
    global _db
    if _db is None:
        if not firebase_admin._apps:
            PROJECT_ROOT = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )

            cred_path = os.getenv("FIREBASE_CREDENTIALS")
            if cred_path and not os.path.isabs(cred_path):
                cred_path = os.path.join(PROJECT_ROOT, cred_path)
            elif not cred_path:
                cred_path = os.path.join(PROJECT_ROOT, "firebase-credentials.json")

            logger.info(f"Loading Firebase credentials from: {cred_path}")
            logger.info(f"File exists: {os.path.exists(cred_path)}")

            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db
