.PHONY: test deploy seed logs

# Default variables
REGION ?= us-central1
PROJECT_ID ?= $(shell gcloud config get-value project 2>/dev/null)
SERVICE_NAME ?= kaamyaar-backend

test:
	@echo "Running tests with pytest..."
	pytest tests/ -v

seed:
	@echo "Seeding the database..."
	python app/scripts/seed_db.py

deploy:
	@echo "Deploying to Google Cloud Run..."
	gcloud run deploy $(SERVICE_NAME) \
		--source . \
		--region $(REGION) \
		--project $(PROJECT_ID) \
		--allow-unauthenticated

logs:
	@echo "Fetching logs for $(SERVICE_NAME)..."
	gcloud run services logs tail $(SERVICE_NAME) \
		--region $(REGION) \
		--project $(PROJECT_ID)
