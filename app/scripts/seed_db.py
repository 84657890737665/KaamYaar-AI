import os
import sys

# Add the project root directory to the python path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
from app.services.firestore_service import firestore_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_seed():
    logger.info("Initializing database seeding process...")
    try:
        firestore_service.seed_mock_data()
        logger.info("Database seeding finished successfully.")
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_seed()
