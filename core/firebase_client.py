"""
core/firebase_client.py

Centralised, cached Firebase Admin and Firestore client initialisation.
Ensures the Firebase app is only initialised once to prevent "app already exists" errors.
"""

import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

_db = None


def get_firestore_client() -> firestore.firestore.Client | None:
    """
    Returns a shared, lazily-initialised Firestore client.
    Ensures that firebase_admin.initialize_app is only called once.
    If the credentials file is missing or connection fails, logs warning and returns None
    instead of crashing the pipeline, allowing robust local execution.
    """
    global _db
    if _db is not None:
        return _db

    try:
        # Check if already initialised by another module/agent
        if not firebase_admin._apps:
            # Look for firebase-credentials.json in the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cred_path = os.path.join(base_dir, "firebase-credentials.json")

            if not os.path.exists(cred_path):
                logger.warning(
                    "[FirebaseClient] Credentials file not found at %s. Firestore will run in offline simulation mode.",
                    cred_path,
                )
                return None

            logger.info("[FirebaseClient] Initialising Firebase Admin SDK with credentials from %s...", cred_path)
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            logger.debug("[FirebaseClient] Firebase Admin SDK already initialised.")

        _db = firestore.client()
        logger.info("[FirebaseClient] Firestore client successfully connected.")
        return _db

    except Exception as exc:
        logger.error("[FirebaseClient] Failed to initialise Firestore client: %s. Swerving to simulated offline mode.", exc)
        return None
