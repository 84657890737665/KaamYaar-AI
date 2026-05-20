import logging
import time
from typing import Optional, List, TypeVar, Type, Any, Dict
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings
from app.models.base import BaseFirestoreModel
from app.models.provider import Provider
from app.models.user import User
from app.models.booking import Booking
from app.models.dispute import Dispute

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseFirestoreModel)

class FirestoreService:
    def __init__(self):
        self.db = None
        self._initialize_with_retries()

    def _initialize_with_retries(self, max_retries=3, delay=2):
        for attempt in range(max_retries):
            try:
                try:
                    firebase_admin.get_app()
                except ValueError:
                    # If Firebase requires specific credentials in production, load them here
                    # Otherwise, it uses GOOGLE_APPLICATION_CREDENTIALS environment variable
                    if settings.firebase_private_key and settings.firebase_client_email and settings.firebase_project_id:
                        cred_dict = {
                            "type": "service_account",
                            "project_id": settings.firebase_project_id,
                            "private_key": settings.firebase_private_key.replace('\\n', '\n'),
                            "client_email": settings.firebase_client_email,
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                        cred = credentials.Certificate(cred_dict)
                        firebase_admin.initialize_app(cred)
                    else:
                        firebase_admin.initialize_app()
                
                self.db = firestore.client()
                logger.info("Successfully connected to Firestore.")
                return
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} to connect to Firestore failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached. Firestore initialization failed.")
                    self.db = None

    def _check_db(self):
        if not self.db:
            raise ConnectionError("Firestore client is not initialized.")

    # Generic CRUD operations
    def create(self, collection_name: str, doc_id: str, data: Dict[str, Any]) -> str:
        self._check_db()
        self.db.collection(collection_name).document(doc_id).set(data)
        return doc_id

    def get(self, collection_name: str, doc_id: str, model_class: Type[T]) -> Optional[T]:
        self._check_db()
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return model_class.from_dict(doc.id, doc.to_dict())
        return None

    def get_all(self, collection_name: str, model_class: Type[T]) -> List[T]:
        self._check_db()
        docs = self.db.collection(collection_name).stream()
        return [model_class.from_dict(doc.id, doc.to_dict()) for doc in docs]

    def update(self, collection_name: str, doc_id: str, data: Dict[str, Any]) -> bool:
        self._check_db()
        doc_ref = self.db.collection(collection_name).document(doc_id)
        if doc_ref.get().exists:
            doc_ref.update(data)
            return True
        return False

    def delete(self, collection_name: str, doc_id: str) -> bool:
        self._check_db()
        self.db.collection(collection_name).document(doc_id).delete()
        return True

    def create_document(self, collection: str, document_id: str, data: dict) -> bool:
        '''Create new document in Firestore'''
        try:
            self.db.collection(collection).document(document_id).set(data)
            return True
        except Exception as e:
            print(f'Error creating document in {collection}: {e}')
            return False

    def update_document(self, collection: str, document_id: str, data: dict) -> bool:
        '''Update existing document in Firestore'''
        try:
            self.db.collection(collection).document(document_id).update(data)
            return True
        except Exception as e:
            print(f'Error updating document in {collection}: {e}')
            return False

    def get_document(self, collection: str, document_id: str) -> dict:
        '''Get document by ID from Firestore'''
        try:
            doc = self.db.collection(collection).document(document_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f'Error getting document from {collection}: {e}')
            return None

    def delete_document(self, collection: str, document_id: str) -> bool:
        '''Delete document from Firestore'''
        try:
            self.db.collection(collection).document(document_id).delete()
            return True
        except Exception as e:
            print(f'Error deleting document from {collection}: {e}')
            return False

    def query_documents(self, collection: str, filters: list) -> list:
        '''Query documents in Firestore with simple filters'''
        try:
            query = self.db.collection(collection)
            for f in filters:
                query = query.where(f["field"], f["operator"], f["value"])
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f'Error querying documents from {collection}: {e}')
            return []

    # Seed mock data
    def seed_mock_data(self):
        """Uploads all mock data to Firestore using batched writes."""
        self._check_db()
        from app.models.mock_data import MOCK_PROVIDERS, MOCK_USERS, MOCK_BOOKINGS, MOCK_DISPUTES
        
        logger.info("Starting database seeding...")
        
        # Firestore batch supports up to 500 operations
        batch = self.db.batch()
        operation_count = 0
        total_seeded = 0

        def _commit_batch_if_full():
            nonlocal batch, operation_count, total_seeded
            if operation_count >= 400:
                batch.commit()
                logger.info(f"Committed batch of {operation_count} writes.")
                total_seeded += operation_count
                batch = self.db.batch()
                operation_count = 0

        # Seed Providers
        for provider in MOCK_PROVIDERS:
            doc_ref = self.db.collection(Provider.COLLECTION_NAME).document(provider.id)
            batch.set(doc_ref, provider.to_dict())
            operation_count += 1
            _commit_batch_if_full()

        # Seed Users
        for user in MOCK_USERS:
            doc_ref = self.db.collection(User.COLLECTION_NAME).document(user.id)
            batch.set(doc_ref, user.to_dict())
            operation_count += 1
            _commit_batch_if_full()

        # Seed Bookings
        for booking in MOCK_BOOKINGS:
            doc_ref = self.db.collection(Booking.COLLECTION_NAME).document(booking.id)
            batch.set(doc_ref, booking.to_dict())
            operation_count += 1
            _commit_batch_if_full()

        # Seed Disputes
        for dispute in MOCK_DISPUTES:
            doc_ref = self.db.collection(Dispute.COLLECTION_NAME).document(dispute.id)
            batch.set(doc_ref, dispute.to_dict())
            operation_count += 1
            _commit_batch_if_full()

        if operation_count > 0:
            batch.commit()
            total_seeded += operation_count
            logger.info(f"Committed final batch of {operation_count} writes.")

        logger.info(f"Seeding completed! Total documents seeded: {total_seeded}")


# Global instance
firestore_service = FirestoreService()
