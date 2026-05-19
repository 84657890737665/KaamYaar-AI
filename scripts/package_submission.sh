#!/bin/bash
set -e

PROJECT_NAME="kaamyaar-ai-submission"
DATE=$(date +%Y%m%d)
ZIP_NAME="${PROJECT_NAME}-${DATE}.zip"

echo "📦 Packaging KaamYaar AI Submission..."

# Create temp directory
mkdir -p /tmp/${PROJECT_NAME}

# Copy backend
cp -r backend/ /tmp/${PROJECT_NAME}/

# Copy mobile app
cp -r mobile-app/ /tmp/${PROJECT_NAME}/

# Copy dashboard
cp -r dashboard/ /tmp/${PROJECT_NAME}/

# Copy docs
cp README.md CHECKLIST.md /tmp/${PROJECT_NAME}/

# Copy mock data
cp -r mock-data/ /tmp/${PROJECT_NAME}/

# Copy agent traces
cp -r agent-traces/ /tmp/${PROJECT_NAME}/

# Create manifest
cat > /tmp/${PROJECT_NAME}/manifest.json <<EOF
{
  "project": "KaamYaar AI",
  "version": "1.0.0",
  "date": "${DATE}",
  "team": {
    "tanzeela": "Team Lead / GenAI Agents",
    "rukhsar": "Flutter / UI-UX",
    "moattar": "Backend / DevOps / Architecture"
  },
  "files_count": $(find /tmp/${PROJECT_NAME} -type f | wc -l),
  "backend_url": "https://kaamyaar-xxx.run.app",
  "total_providers": 50,
  "languages_supported": 8
}
EOF

# Zip it
cd /tmp
zip -r ${ZIP_NAME} ${PROJECT_NAME} \
  -x "*.git*" -x "*__pycache__*" -x "*.pyc" -x ".env" \
  -x "node_modules/*" -x "*.mp4"

# Move to output
mv ${ZIP_NAME} ~/Desktop/

echo "✅ Package ready: ~/Desktop/${ZIP_NAME}"
echo "📊 Size: $(du -h ~/Desktop/${ZIP_NAME} | cut -f1)"
