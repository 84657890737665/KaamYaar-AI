# KaamYaar AI — Submission Checklist
**Date:** 2026-05-19  
**Team:** Tanzeela (Lead/Agents), Rukhsar (Flutter/UI), Moattar (Backend/DevOps)

## Core Deliverables
- [ ] `mobile-app/kaamyaar_app.apk` — Flutter APK (Rukhsar)
  - *Verification:* `Test-Path "mobile-app/kaamyaar_app.apk"`
- [ ] `demo-video.mp4` — 3-5 min demo (Tanzeela)
  - *Verification:* `Test-Path "demo-video.mp4"`
- [ ] `antigravity-video.mp4` — 2-3 min agent traces (Tanzeela)
  - *Verification:* `Test-Path "antigravity-video.mp4"`
- [ ] `agent-traces/` — JSON logs folder (Moattar)
  - *Verification:* `Test-Path "agent-traces"`
- [ ] `presentation.pptx` — Updated slides (Tanzeela)
  - *Verification:* `Test-Path "presentation.pptx"`
- [ ] `README.md` — Complete documentation (Moattar) ✅
  - *Verification:* `Test-Path "README.md"`
- [ ] `mock-data/providers.json` — 50+ providers (Moattar) ✅
  - *Verification:* `Test-Path "mock-data/providers.json"`

## Backend Verification
- [ ] Cloud Run URL live: `https://kaamyaar-xxx.run.app`
  - *Verification:* `curl.exe -I https://kaamyaar-xxx.run.app`
- [ ] `/health` endpoint returns 200
  - *Verification:* `curl.exe -s -o NUL -w "%{http_code}" https://kaamyaar-xxx.run.app/health`
- [ ] `/api/v1/parse-request` working with Urdu/Roman Urdu
  - *Verification:* `curl.exe -X POST https://kaamyaar-xxx.run.app/api/v1/parse-request -H "Content-Type: application/json" -d "{\"text\":\"mujhe plumber chahiye\"}"`
- [ ] `/dashboard` accessible
  - *Verification:* `curl.exe -I https://kaamyaar-xxx.run.app/dashboard`
- [ ] Firestore has 50+ seeded providers
  - *Verification:* Run backend test or seed script: `python -m app.scripts.seed_providers`

## Test Results
- [ ] ST1 Parse Flood: 100 concurrent ✅
  - *Verification:* `pytest tests/performance/test_parse_flood.py` (or relevant Locust command)
- [ ] ST2 Provider Search: 50 concurrent ✅
  - *Verification:* `pytest tests/performance/test_provider_search.py`
- [ ] ST3 Booking Spike: 200 in 60s ✅
  - *Verification:* `pytest tests/performance/test_booking_spike.py`
- [ ] ST4 Ranking: 1000 providers ✅
  - *Verification:* `pytest tests/performance/test_ranking_scale.py`
- [ ] ST5 End-to-End: 50 workflows ✅
  - *Verification:* `pytest tests/performance/test_e2e_workflows.py`
- [ ] ST6 Dispute Storm: 20 concurrent ✅
  - *Verification:* `pytest tests/performance/test_dispute_storm.py`

## Security
- [ ] No API keys in code ✅
  - *Verification:* `git log --all --source --remotes --oneline | findstr /i "key secret password"`
- [ ] `.env` in `.gitignore` ✅
  - *Verification:* `findstr ".env" .gitignore`
- [ ] Firebase rules secure ✅
  - *Verification:* `firebase deploy --only firestore:rules --dry-run` or manual console review
