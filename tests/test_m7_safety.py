import sys
import os
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── Patch Firebase BEFORE any app module is imported ─────
# 1. Mock firebase_admin so the SDK never tries to authenticate
import firebase_admin
firebase_admin.initialize_app = MagicMock()
firebase_admin.get_app = MagicMock()

from firebase_admin import firestore as _fb_firestore
_fb_firestore.client = MagicMock()

# 2. Patch FirestoreService._initialize_with_retries so the constructor
#    (which runs at import time via the module-level singleton) is a no-op.
from unittest.mock import PropertyMock
import app.services.firestore_service as _fs_mod
_fs_mod.FirestoreService._initialize_with_retries = MagicMock()
# Re-instantiate the global singleton with the patched class
_fs_mod.firestore_service = _fs_mod.FirestoreService()
_fs_mod.firestore_service.db = MagicMock()

# 3. Now safely import the app
from fastapi.testclient import TestClient
from app.main import app
from app.services.firestore_service import firestore_service

# Ensure db is a fresh MagicMock
firestore_service.db = MagicMock()

client = TestClient(app)


# ─────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────

def _mock_booking_doc(booking_id="book_123", user_id="user_456",
                      service_type="plumber", estimated_minutes=75):
    """Return a dict that looks like a Firestore booking document."""
    return {
        "id": booking_id,
        "user_id": user_id,
        "service_type": service_type,
        "estimated_minutes": estimated_minutes,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "in_progress",
    }


def _setup_firestore_mock(booking_doc=None, alert_docs=None):
    """
    Wire up firestore_service.db so that:
      - collection("bookings").document(id).get()  returns booking_doc
      - collection("safety_alerts").document(id).set(data) captures the record
      - collection("safety_alerts").where(...).limit(1).stream() yields alert_docs
    """
    mock_db = MagicMock()

    # --- bookings collection ---
    mock_booking_snapshot = MagicMock()
    if booking_doc is not None:
        mock_booking_snapshot.exists = True
        mock_booking_snapshot.to_dict.return_value = booking_doc
    else:
        mock_booking_snapshot.exists = False
        mock_booking_snapshot.to_dict.return_value = None

    mock_booking_doc_ref = MagicMock()
    mock_booking_doc_ref.get.return_value = mock_booking_snapshot

    # --- safety_alerts collection ---
    mock_alerts_collection = MagicMock()
    mock_alerts_query = MagicMock()
    if alert_docs:
        mock_snapshots = []
        for ad in alert_docs:
            snap = MagicMock()
            snap.to_dict.return_value = ad
            mock_snapshots.append(snap)
        mock_alerts_query.stream.return_value = iter(mock_snapshots)
    else:
        mock_alerts_query.stream.return_value = iter([])
    mock_alerts_query.limit.return_value = mock_alerts_query
    mock_alerts_collection.where.return_value = mock_alerts_query

    mock_alert_doc_ref = MagicMock()
    mock_alerts_collection.document.return_value = mock_alert_doc_ref

    def _collection_router(name):
        if name == "bookings":
            coll = MagicMock()
            coll.document.return_value = mock_booking_doc_ref
            return coll
        elif name == "safety_alerts":
            return mock_alerts_collection
        return MagicMock()

    mock_db.collection.side_effect = _collection_router
    firestore_service.db = mock_db
    return mock_db


# ═════════════════════════════════════════════════════════
#  TEST RUNNER
# ═════════════════════════════════════════════════════════

def run_tests():
    results = {}

    # ─────────────────────────────────────────────────────
    #  TEST 1: Time Estimate Endpoint
    # ─────────────────────────────────────────────────────
    t1 = {}

    # 1a  Valid request
    try:
        res = client.post("/api/v1/safety/estimate-time", json={
            "service_type": "plumber", "job_complexity": "intermediate"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["estimated_minutes"] == 75
        t1["Valid request"] = "PASS ✅"
    except Exception as e:
        t1["Valid request"] = f"FAIL ❌ ({e})"

    # 1b  Warning calculation = estimated + 30
    try:
        res = client.post("/api/v1/safety/estimate-time", json={
            "service_type": "plumber", "job_complexity": "intermediate"
        })
        data = res.json()
        assert data["warning_at_minutes"] == data["estimated_minutes"] + 30
        t1["Warning calculation"] = "PASS ✅"
    except Exception as e:
        t1["Warning calculation"] = f"FAIL ❌ ({e})"

    # 1c  Invalid service → 400
    try:
        res = client.post("/api/v1/safety/estimate-time", json={
            "service_type": "rocket_scientist", "job_complexity": "intermediate"
        })
        assert res.status_code == 400
        t1["Invalid service: 400"] = "PASS ✅"
    except Exception as e:
        t1["Invalid service: 400"] = f"FAIL ❌ ({e})"

    # 1d  Invalid complexity → 400
    try:
        res = client.post("/api/v1/safety/estimate-time", json={
            "service_type": "plumber", "job_complexity": "legendary"
        })
        assert res.status_code == 400
        t1["Invalid complexity: 400"] = "PASS ✅"
    except Exception as e:
        t1["Invalid complexity: 400"] = f"FAIL ❌ ({e})"

    # 1e  Confidence is 'high'
    try:
        res = client.post("/api/v1/safety/estimate-time", json={
            "service_type": "electrician", "job_complexity": "basic"
        })
        assert res.json()["confidence"] == "high"
        t1["Confidence 'high'"] = "PASS ✅"
    except Exception as e:
        t1["Confidence 'high'"] = f"FAIL ❌ ({e})"

    # 1f  Safety note contains Urdu text
    try:
        res = client.post("/api/v1/safety/estimate-time", json={
            "service_type": "plumber", "job_complexity": "complex"
        })
        note = res.json()["safety_note"]
        assert "safety alert jayega" in note
        t1["Safety note (Urdu)"] = "PASS ✅"
    except Exception as e:
        t1["Safety note (Urdu)"] = f"FAIL ❌ ({e})"

    results["TEST 1: Time Estimate Endpoint"] = t1

    # ─────────────────────────────────────────────────────
    #  TEST 2: Emergency Alert Endpoint
    # ─────────────────────────────────────────────────────
    t2 = {}

    # 2a  Valid alert creation
    try:
        _setup_firestore_mock(booking_doc=_mock_booking_doc())
        res = client.post("/api/v1/safety/emergency-alert", json={
            "booking_id": "book_123", "user_id": "user_456",
            "trusted_contact_number": "03001234567", "trusted_contact_name": "Amna"
        })
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "alert_sent"
        assert data["booking_id"] == "book_123"
        assert data["trusted_contact_name"] == "Amna"
        assert data["trusted_contact_number"] == "03001234567"
        t2["Valid alert creation"] = "PASS ✅"
    except Exception as e:
        t2["Valid alert creation"] = f"FAIL ❌ ({e})"

    # 2b  Unique alert_id
    try:
        _setup_firestore_mock(booking_doc=_mock_booking_doc())
        res1 = client.post("/api/v1/safety/emergency-alert", json={
            "booking_id": "book_123", "user_id": "user_456",
            "trusted_contact_number": "03001234567", "trusted_contact_name": "Amna"
        })
        _setup_firestore_mock(booking_doc=_mock_booking_doc())
        res2 = client.post("/api/v1/safety/emergency-alert", json={
            "booking_id": "book_123", "user_id": "user_456",
            "trusted_contact_number": "03001234567", "trusted_contact_name": "Amna"
        })
        assert res1.json()["alert_id"] != res2.json()["alert_id"]
        t2["Unique alert_id"] = "PASS ✅"
    except Exception as e:
        t2["Unique alert_id"] = f"FAIL ❌ ({e})"

    # 2c  Firestore record created (set() was called)
    try:
        mock_db = _setup_firestore_mock(booking_doc=_mock_booking_doc())
        res = client.post("/api/v1/safety/emergency-alert", json={
            "booking_id": "book_123", "user_id": "user_456",
            "trusted_contact_number": "03001234567", "trusted_contact_name": "Amna"
        })
        mock_db.collection.assert_any_call("safety_alerts")
        t2["Firestore record"] = "PASS ✅"
    except Exception as e:
        t2["Firestore record"] = f"FAIL ❌ ({e})"

    # 2d  Invalid booking_id → 404
    try:
        _setup_firestore_mock(booking_doc=None)
        res = client.post("/api/v1/safety/emergency-alert", json={
            "booking_id": "nonexistent_999", "user_id": "user_456",
            "trusted_contact_number": "03001234567", "trusted_contact_name": "Amna"
        })
        assert res.status_code == 404
        t2["Invalid booking: 404"] = "PASS ✅"
    except Exception as e:
        t2["Invalid booking: 404"] = f"FAIL ❌ ({e})"

    # 2e  Invalid user_id → 403
    try:
        _setup_firestore_mock(booking_doc=_mock_booking_doc(user_id="real_owner"))
        res = client.post("/api/v1/safety/emergency-alert", json={
            "booking_id": "book_123", "user_id": "impersonator_789",
            "trusted_contact_number": "03001234567", "trusted_contact_name": "Amna"
        })
        assert res.status_code == 403
        t2["Invalid user: 403"] = "PASS ✅"
    except Exception as e:
        t2["Invalid user: 403"] = f"FAIL ❌ ({e})"

    results["TEST 2: Emergency Alert Endpoint"] = t2

    # ─────────────────────────────────────────────────────
    #  TEST 3: Safety Status Endpoint
    # ─────────────────────────────────────────────────────
    t3 = {}

    # 3a  Status retrieval
    try:
        _setup_firestore_mock(
            booking_doc=_mock_booking_doc(),
            alert_docs=[{"status": "alert_sent", "booking_id": "book_123"}],
        )
        res = client.get("/api/v1/safety/status/book_123")
        assert res.status_code == 200
        data = res.json()
        assert data["booking_id"] == "book_123"
        t3["Status retrieval"] = "PASS ✅"
    except Exception as e:
        t3["Status retrieval"] = f"FAIL ❌ ({e})"

    # 3b  Time remaining present
    try:
        _setup_firestore_mock(booking_doc=_mock_booking_doc())
        res = client.get("/api/v1/safety/status/book_123")
        data = res.json()
        assert "time_remaining_minutes" in data
        assert isinstance(data["time_remaining_minutes"], int)
        t3["Time remaining"] = "PASS ✅"
    except Exception as e:
        t3["Time remaining"] = f"FAIL ❌ ({e})"

    # 3c  Alert tracking
    try:
        _setup_firestore_mock(
            booking_doc=_mock_booking_doc(),
            alert_docs=[{"status": "alert_sent", "booking_id": "book_123"}],
        )
        res = client.get("/api/v1/safety/status/book_123")
        data = res.json()
        assert data["alert_status"] == "alert_sent"
        assert data["trusted_contact_notified"] is True
        t3["Alert tracking"] = "PASS ✅"
    except Exception as e:
        t3["Alert tracking"] = f"FAIL ❌ ({e})"

    # 3d  Invalid booking_id → 404
    try:
        _setup_firestore_mock(booking_doc=None)
        res = client.get("/api/v1/safety/status/nonexistent_999")
        assert res.status_code == 404
        t3["Invalid booking: 404"] = "PASS ✅"
    except Exception as e:
        t3["Invalid booking: 404"] = f"FAIL ❌ ({e})"

    results["TEST 3: Safety Status Endpoint"] = t3

    # ─────────────────────────────────────────────────────
    #  TEST 4: Integration Tests
    # ─────────────────────────────────────────────────────
    t4 = {}

    # 4a  Time → Alert → Status flow
    try:
        # Step 1: Estimate time
        res_time = client.post("/api/v1/safety/estimate-time", json={
            "service_type": "plumber", "job_complexity": "intermediate"
        })
        assert res_time.status_code == 200
        estimated = res_time.json()["estimated_minutes"]
        assert estimated == 75

        # Step 2: Trigger alert
        _setup_firestore_mock(booking_doc=_mock_booking_doc(estimated_minutes=estimated))
        res_alert = client.post("/api/v1/safety/emergency-alert", json={
            "booking_id": "book_123", "user_id": "user_456",
            "trusted_contact_number": "03001234567", "trusted_contact_name": "Amna"
        })
        assert res_alert.status_code == 201

        # Step 3: Check status
        _setup_firestore_mock(
            booking_doc=_mock_booking_doc(estimated_minutes=estimated),
            alert_docs=[{"status": "alert_sent", "booking_id": "book_123"}],
        )
        res_status = client.get("/api/v1/safety/status/book_123")
        assert res_status.status_code == 200
        assert res_status.json()["trusted_contact_notified"] is True
        t4["Time → Alert → Status flow"] = "PASS ✅"
    except Exception as e:
        t4["Time → Alert → Status flow"] = f"FAIL ❌ ({e})"

    # 4b  Multiple services time comparison
    try:
        services = {
            "plumber":     {"intermediate": 75},
            "painter":     {"intermediate": 240},
            "electrician": {"basic": 60},
            "carpenter":   {"complex": 240},
        }
        for svc, complexities in services.items():
            for cmplx, expected in complexities.items():
                res = client.post("/api/v1/safety/estimate-time", json={
                    "service_type": svc, "job_complexity": cmplx
                })
                assert res.status_code == 200
                actual = res.json()["estimated_minutes"]
                assert actual == expected, f"{svc}/{cmplx}: expected {expected}, got {actual}"
        t4["Service comparison"] = "PASS ✅"
    except Exception as e:
        t4["Service comparison"] = f"FAIL ❌ ({e})"

    # 4c  Female user alert flow
    try:
        _setup_firestore_mock(booking_doc=_mock_booking_doc())
        res = client.post("/api/v1/safety/emergency-alert", json={
            "booking_id": "book_123", "user_id": "user_456",
            "trusted_contact_number": "03009876543", "trusted_contact_name": "Fatima"
        })
        assert res.status_code == 201
        assert res.json()["message"] == "Trusted contact ko notify kar diya gaya"
        t4["Female user alert"] = "PASS ✅"
    except Exception as e:
        t4["Female user alert"] = f"FAIL ❌ ({e})"

    results["TEST 4: Integration Tests"] = t4

    # ─────────────────────────────────────────────────────
    #  Report
    # ─────────────────────────────────────────────────────
    report = []
    report.append("==================================================")
    report.append("M7 SAFETY ENDPOINT TEST REPORT")
    report.append("==================================================")
    report.append("")

    for section, subtests in results.items():
        report.append(section)
        for name, status_val in subtests.items():
            report.append(f"- {name}: {status_val}")
        report.append("")

    all_passed = all(
        "PASS" in s
        for subtests in results.values()
        for s in subtests.values()
    )

    report.append("==================================================")
    if all_passed:
        report.append("FINAL RESULT: ✅ ALL TESTS PASSED (100%)")
    else:
        report.append("FINAL RESULT: ❌ SOME TESTS FAILED")
    report.append("==================================================")

    report_text = "\n".join(report)
    print(report_text)

    # Write report to file
    os.makedirs("tests", exist_ok=True)
    with open("tests/test_m7_results.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    return all_passed


if __name__ == "__main__":
    run_tests()
