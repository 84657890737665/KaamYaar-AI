import os
import json
import re

report = {}

def check_file(path):
    return os.path.exists(path)

def check_content(path, pattern):
    if not os.path.exists(path): return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        return bool(re.search(pattern, content))

def check_json(path, min_len):
    if not os.path.exists(path): return False
    try:
        data = json.load(open(path, 'r', encoding='utf-8'))
        return len(data) >= min_len
    except:
        return False

# 1. FastAPI Project Setup
report['1'] = {
    'main': check_file('app/main.py'),
    'routers': check_file('app/routers/__init__.py'),
    'models': check_file('app/models/__init__.py'),
    'services': check_file('app/services/__init__.py'),
    'utils': check_file('app/utils/__init__.py'),
    'tests': check_file('tests/__init__.py'),
    'reqs': check_content('requirements.txt', r'fastapi|uvicorn|python-dotenv|google-cloud-firestore|googlemaps|firebase-admin|pydantic|pydantic-settings'),
    'dockerfile': check_file('Dockerfile')
}

# 2. Cloud Run Deploy Test
report['2'] = {
    'cloudbuild': check_file('cloudbuild.yaml'),
    'gcloudignore': check_file('.gcloudignore'),
    'health': check_content('app/main.py', r'/health|/'),
}

# 3. Google Maps API Integration
report['3'] = {
    'maps_service': check_file('app/services/maps_service.py'),
    'calc_dist': check_content('app/services/maps_service.py', r'def calculate_distance'),
    'geocode': check_content('app/services/maps_service.py', r'def geocode_location'),
}

# 4. Environment Config
report['4'] = {
    'env_example': check_file('.env.example'),
    'config_py': check_file('app/config.py'),
    'gitignore': check_content('.gitignore', r'\.env'),
}

# 5. Firestore Schema
report['5'] = {
    'provider': check_file('app/models/provider.py'),
    'booking': check_file('app/models/booking.py'),
    'user': check_file('app/models/user.py'),
    'dispute': check_file('app/models/dispute.py'),
}

# 6. Core APIs
report['6'] = {
    'parse': check_content('app/routers/orchestrator.py', r'/parse-request') or check_content('app/routers/orchestrator.py', r'/parse-request'),
    'find': check_content('app/routers/orchestrator.py', r'/find-providers') or check_content('app/routers/orchestrator.py', r'/find-providers'),
    'rank': check_content('app/routers/orchestrator.py', r'/rank-providers') or check_content('app/routers/orchestrator.py', r'/rank-providers'),
}
# wait, orchestrator might be in routers/orchestrator.py or similar. Let's just grep all routers
report['6']['parse'] = check_content('app/main.py', r'/parse-request') or any(check_content(f'app/routers/{f}', r'/parse-request') for f in os.listdir('app/routers/') if f.endswith('.py'))
report['6']['find'] = any(check_content(f'app/routers/{f}', r'/find-providers') for f in os.listdir('app/routers/') if f.endswith('.py'))
report['6']['rank'] = any(check_content(f'app/routers/{f}', r'/rank-providers') for f in os.listdir('app/routers/') if f.endswith('.py'))

# 7. Firestore Integration + Mock Data
report['7'] = {
    'firestore_svc': check_file('app/services/firestore_service.py'),
    'mock_data_py': check_file('app/models/mock_data.py'),
    'seed_db': check_file('app/scripts/seed_db.py') or check_file('scripts/seed_db.py'),
}

# 8. Router Integration
report['8'] = {
    'v1_prefix': check_content('app/main.py', r'/api/v1'),
}

# 9. Pricing Engine
report['9'] = {
    'pricing_svc': check_file('app/services/pricing_engine.py'),
    'calc_endpoint': any(check_content(f'app/routers/{f}', r'/calculate-price') for f in os.listdir('app/routers/') if f.endswith('.py')),
}

# 10. Booking Executor
report['10'] = {
    'booking_svc': check_file('app/services/booking_executor.py'),
    'create_booking': any(check_content(f'app/routers/{f}', r'/create-booking') for f in os.listdir('app/routers/') if f.endswith('.py')),
}

# 11. Quality Monitor
report['11'] = {
    'quality_svc': check_file('app/services/quality_monitor.py'),
    'track': any(check_content(f'app/routers/{f}', r'/track-enroute') for f in os.listdir('app/routers/') if f.endswith('.py')),
    'feedback': any(check_content(f'app/routers/{f}', r'/submit-feedback') for f in os.listdir('app/routers/') if f.endswith('.py')),
}

# 12. 5 Additional Languages
report['12'] = {
    'lang_det': check_file('app/utils/language_detector.py'),
    'test_multi': check_file('tests/test_multilingual.py') or check_file('tests/unit/test_multilingual.py'),
}

# 13. End-to-End Integration Test
report['13'] = {
    'test_e2e': check_file('tests/test_full_workflow.py') or check_file('tests/integration/test_full_workflow.py'),
}

# 14. Dispute Resolver
report['14'] = {
    'dispute_svc': check_file('app/services/dispute_resolver.py'),
    'file_dispute': any(check_content(f'app/routers/{f}', r'/file-dispute') for f in os.listdir('app/routers/') if f.endswith('.py')),
}

# 15. Flutter ↔ FastAPI
report['15'] = {
    'mobile_api': check_file('app/routers/mobile_api.py'),
    'auth_mid': check_file('app/middleware/auth.py'),
}

# 16. Antigravity Tracing
report['16'] = {
    'tracing_py': check_file('app/utils/tracing.py'),
    'trace_ep': any(check_content(f'app/routers/{f}', r'/admin/trace') for f in os.listdir('app/routers/') if f.endswith('.py')),
}

# 17. Stress Tests
report['17'] = {
    'locust': check_file('tests/stress_tests/locustfile.py'),
    'run_stress': check_file('scripts/run_stress_tests.sh'),
}

# 18. Dashboard
report['18'] = {
    'index': check_file('dashboard/index.html'),
    'app_js': check_file('dashboard/app.js'),
    'style_css': check_file('dashboard/style.css'),
}

# 19. README + Mock Data
report['19'] = {
    'readme': check_file('README.md'),
    'providers_json': check_file('data/providers.json'),
}

# 20. Final README
report['20'] = {
    'team': check_content('README.md', r'(?i)team member bios'),
    'arch': check_content('README.md', r'(?i)architecture diagram'),
}

# 21. GitHub Repo Clean
report['21'] = {
    'security': check_file('SECURITY.md'),
}

# 22. Deliverables Checklist
report['22'] = {
    'checklist': check_file('CHECKLIST.md'),
}

# 23. Submission Package
report['23'] = {
    'pkg_sh': check_file('scripts/package_submission.sh'),
}

# 24. Final Verif
report['24'] = {
    'final_chk': check_file('scripts/final_check.py'),
}

print(json.dumps(report, indent=2))
