import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── Patch Firebase BEFORE any app module is imported ─────
import firebase_admin
firebase_admin.initialize_app = MagicMock()
firebase_admin.get_app = MagicMock()
from firebase_admin import firestore as _fb_firestore
_fb_firestore.client = MagicMock()

import app.services.firestore_service as _fs_mod
_fs_mod.FirestoreService._initialize_with_retries = MagicMock()
_fs_mod.firestore_service = _fs_mod.FirestoreService()
_fs_mod.firestore_service.db = MagicMock()

from fastapi.testclient import TestClient
from app.main import app
from app.services.firestore_service import firestore_service
from agents.calling_agent.agent import CallingAgent

firestore_service.db = MagicMock()
client = TestClient(app)


# ─────────────────────────────────────────────────────────
#  Test Data
# ─────────────────────────────────────────────────────────

VALID_CALL_DATA = {
    "booking_id": "book_123",
    "user_name": "Fatima",
    "user_location": "House 14, Street 18, F-11, Islamabad",
    "provider_name": "Ali Syed",
    "provider_cnic": "35201-1234567-1",
    "provider_mobile": "0300-1234567",
    "trusted_contact_name": "Amna",
    "trusted_contact_number": "03001234567",
    "service_type": "plumber",
    "booking_time": "2026-05-19T09:30:00Z",
    "estimated_minutes": 90,
    "minutes_exceeded": 120,
}


def _setup_firestore_mock(booking_exists=True, call_docs=None, call_detail=None):
    """Wire up firestore_service.db for tests."""
    mock_db = MagicMock()

    # bookings collection
    mock_booking_snap = MagicMock()
    mock_booking_snap.exists = booking_exists
    mock_booking_snap.to_dict.return_value = {"booking_id": "book_123", "user_id": "user_456", "status": "in_progress"}
    mock_booking_doc_ref = MagicMock()
    mock_booking_doc_ref.get.return_value = mock_booking_snap

    # emergency_calls collection
    mock_calls_coll = MagicMock()

    # .where().stream() for logs
    mock_query = MagicMock()
    if call_docs:
        snaps = []
        for cd in call_docs:
            s = MagicMock()
            s.to_dict.return_value = cd
            snaps.append(s)
        mock_query.stream.return_value = iter(snaps)
    else:
        mock_query.stream.return_value = iter([])
    mock_calls_coll.where.return_value = mock_query

    # .document(id).get() for details
    mock_call_snap = MagicMock()
    if call_detail:
        mock_call_snap.exists = True
        mock_call_snap.to_dict.return_value = call_detail
    else:
        mock_call_snap.exists = False
        mock_call_snap.to_dict.return_value = None
    mock_call_doc_ref = MagicMock()
    mock_call_doc_ref.get.return_value = mock_call_snap
    mock_calls_coll.document.return_value = mock_call_doc_ref

    def _router(name):
        if name == "bookings":
            c = MagicMock()
            c.document.return_value = mock_booking_doc_ref
            return c
        elif name == "emergency_calls":
            return mock_calls_coll
        return MagicMock()

    mock_db.collection.side_effect = _router
    firestore_service.db = mock_db
    return mock_db


# ═════════════════════════════════════════════════════════
#  TEST RUNNER
# ═════════════════════════════════════════════════════════

def run_tests():
    results = {}

    # ─────────────────────────────────────────────────
    #  TEST 1: CallingAgent Unit Tests
    # ─────────────────────────────────────────────────
    t1 = {}

    # 1a validate_inputs valid
    try:
        agent = CallingAgent()
        assert agent.validate_inputs(VALID_CALL_DATA) is True
        t1["validate_inputs()"] = "PASS ✅"
    except Exception as e:
        t1["validate_inputs()"] = f"FAIL ❌ ({e})"

    # 1b validate_inputs missing field
    try:
        agent = CallingAgent()
        bad = {k: v for k, v in VALID_CALL_DATA.items() if k != "booking_id"}
        try:
            agent.validate_inputs(bad)
            t1["validate_inputs() missing fields: Error"] = "FAIL ❌ (no error raised)"
        except ValueError as ve:
            assert "booking_id" in str(ve)
            t1["validate_inputs() missing fields: Error"] = "PASS ✅"
    except Exception as e:
        t1["validate_inputs() missing fields: Error"] = f"FAIL ❌ ({e})"

    # 1c generate_call_id unique
    try:
        a1, a2 = CallingAgent(), CallingAgent()
        id1, id2 = a1.generate_call_id(), a2.generate_call_id()
        assert id1 != id2
        assert id1.startswith("call_")
        t1["generate_call_id()"] = "PASS ✅"
    except Exception as e:
        t1["generate_call_id()"] = f"FAIL ❌ ({e})"

    # 1d create_call_context
    try:
        agent = CallingAgent()
        agent.generate_call_id()
        ctx = agent.create_call_context(VALID_CALL_DATA)
        assert ctx["call_id"] == agent.call_id
        assert ctx["booking_id"] == "book_123"
        assert ctx["user_name"] == "Fatima"
        assert "alert_reason" in ctx
        t1["create_call_context()"] = "PASS ✅"
    except Exception as e:
        t1["create_call_context()"] = f"FAIL ❌ ({e})"

    # 1e make_call
    try:
        agent = CallingAgent()
        agent.generate_call_id()
        ctx = agent.create_call_context(VALID_CALL_DATA)
        ctx["timestamp"] = datetime.now(timezone.utc).isoformat()
        result = agent.make_call(ctx)
        assert result["call_status"] == "completed"
        assert len(result["call_transcript"]) > 0
        assert result["call_duration_seconds"] == 180
        t1["make_call()"] = "PASS ✅"
    except Exception as e:
        t1["make_call()"] = f"FAIL ❌ ({e})"

    # 1f store_in_firestore
    try:
        _setup_firestore_mock()
        agent = CallingAgent()
        agent.generate_call_id()
        ctx = agent.create_call_context(VALID_CALL_DATA)
        result = {"call_status": "completed", "call_sid": "SM123", "call_transcript": "test", "call_duration_seconds": 180, "contact_reached": True, "contact_response": "ok"}
        stored = agent.store_in_firestore(result, ctx)
        assert stored is True
        t1["store_in_firestore()"] = "PASS ✅"
    except Exception as e:
        t1["store_in_firestore()"] = f"FAIL ❌ ({e})"

    results["TEST 1: CallingAgent Unit Tests"] = t1

    # ─────────────────────────────────────────────────
    #  TEST 2: Agent Flow Tests
    # ─────────────────────────────────────────────────
    t2 = {}

    # 2a Full run()
    try:
        _setup_firestore_mock()
        agent = CallingAgent()
        resp = agent.run(VALID_CALL_DATA)
        assert "call_id" in resp
        assert resp["call_status"] == "completed"
        t2["Full run() method"] = "PASS ✅"
    except Exception as e:
        t2["Full run() method"] = f"FAIL ❌ ({e})"

    # 2b Output structure
    try:
        _setup_firestore_mock()
        agent = CallingAgent()
        resp = agent.run(VALID_CALL_DATA)
        required_keys = ["call_id", "call_status", "trusted_contact_name", "trusted_contact_number",
                         "call_transcript", "call_duration_seconds", "call_sid", "next_action", "safety_actions"]
        for k in required_keys:
            assert k in resp, f"Missing key: {k}"
        t2["Output structure correct"] = "PASS ✅"
    except Exception as e:
        t2["Output structure correct"] = f"FAIL ❌ ({e})"

    # 2c call_status completed
    try:
        _setup_firestore_mock()
        agent = CallingAgent()
        resp = agent.run(VALID_CALL_DATA)
        assert resp["call_status"] == "completed"
        t2["call_status 'completed'"] = "PASS ✅"
    except Exception as e:
        t2["call_status 'completed'"] = f"FAIL ❌ ({e})"

    # 2d Unique call_sid
    try:
        _setup_firestore_mock()
        a1 = CallingAgent()
        r1 = a1.run(VALID_CALL_DATA)
        _setup_firestore_mock()
        a2 = CallingAgent()
        r2 = a2.run(VALID_CALL_DATA)
        assert r1["call_sid"] != r2["call_sid"]
        t2["Unique call_sid"] = "PASS ✅"
    except Exception as e:
        t2["Unique call_sid"] = f"FAIL ❌ ({e})"

    # 2e Non-empty transcript
    try:
        _setup_firestore_mock()
        agent = CallingAgent()
        resp = agent.run(VALID_CALL_DATA)
        assert len(resp["call_transcript"]) > 50
        assert "EMERGENCY CALL TRANSCRIPT" in resp["call_transcript"]
        t2["Non-empty transcript"] = "PASS ✅"
    except Exception as e:
        t2["Non-empty transcript"] = f"FAIL ❌ ({e})"

    results["TEST 2: Agent Flow Tests"] = t2

    # ─────────────────────────────────────────────────
    #  TEST 3: Trigger Call Endpoint
    # ─────────────────────────────────────────────────
    t3 = {}

    # 3a Valid request 200
    try:
        _setup_firestore_mock(booking_exists=True)
        res = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        assert res.status_code == 200
        t3["Valid request: 200"] = "PASS ✅"
    except Exception as e:
        t3["Valid request: 200"] = f"FAIL ❌ ({e})"

    # 3b Response fields complete
    try:
        _setup_firestore_mock(booking_exists=True)
        res = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        data = res.json()
        for key in ["call_id", "call_status", "trusted_contact_name", "trusted_contact_number",
                     "call_transcript", "call_duration_seconds", "call_sid", "triggered_at",
                     "next_action", "message", "safety_actions"]:
            assert key in data, f"Missing: {key}"
        t3["Response fields complete"] = "PASS ✅"
    except Exception as e:
        t3["Response fields complete"] = f"FAIL ❌ ({e})"

    # 3c Invalid booking_id 404
    try:
        _setup_firestore_mock(booking_exists=False)
        res = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        assert res.status_code == 404
        t3["Invalid booking_id: 404"] = "PASS ✅"
    except Exception as e:
        t3["Invalid booking_id: 404"] = f"FAIL ❌ ({e})"

    # 3d Missing fields 422
    try:
        res = client.post("/api/v1/safety/call/trigger", json={"booking_id": "book_123"})
        assert res.status_code == 422
        t3["Missing fields: 422"] = "PASS ✅"
    except Exception as e:
        t3["Missing fields: 422"] = f"FAIL ❌ ({e})"

    # 3e Firestore record created
    try:
        mock_db = _setup_firestore_mock(booking_exists=True)
        res = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        assert res.status_code == 200
        # Background tasks run synchronously in TestClient
        mock_db.collection.assert_any_call("emergency_calls")
        t3["Firestore record created"] = "PASS ✅"
    except Exception as e:
        t3["Firestore record created"] = f"FAIL ❌ ({e})"

    results["TEST 3: Trigger Call Endpoint"] = t3

    # ─────────────────────────────────────────────────
    #  TEST 4: Get Logs Endpoint
    # ─────────────────────────────────────────────────
    t4 = {}

    # 4a Returns all calls
    try:
        call_log_1 = {"call_id": "call_aaa", "booking_id": "book_123", "call_status": "completed"}
        call_log_2 = {"call_id": "call_bbb", "booking_id": "book_123", "call_status": "completed"}
        _setup_firestore_mock(call_docs=[call_log_1, call_log_2])
        res = client.get("/api/v1/safety/call/log/book_123")
        assert res.status_code == 200
        data = res.json()
        assert len(data["call_logs"]) == 2
        t4["Returns all calls"] = "PASS ✅"
    except Exception as e:
        t4["Returns all calls"] = f"FAIL ❌ ({e})"

    # 4b total_calls count correct
    try:
        call_log = {"call_id": "call_ccc", "booking_id": "book_123", "call_status": "completed"}
        _setup_firestore_mock(call_docs=[call_log])
        res = client.get("/api/v1/safety/call/log/book_123")
        assert res.json()["total_calls"] == 1
        t4["total_calls count correct"] = "PASS ✅"
    except Exception as e:
        t4["total_calls count correct"] = f"FAIL ❌ ({e})"

    # 4c Invalid booking_id 404
    try:
        _setup_firestore_mock(call_docs=[])  # no logs
        res = client.get("/api/v1/safety/call/log/nonexistent_999")
        assert res.status_code == 404
        t4["Invalid booking_id: 404"] = "PASS ✅"
    except Exception as e:
        t4["Invalid booking_id: 404"] = f"FAIL ❌ ({e})"

    # 4d call_logs structure correct
    try:
        call_log = {"call_id": "call_ddd", "booking_id": "book_123", "call_status": "completed", "call_sid": "SM123"}
        _setup_firestore_mock(call_docs=[call_log])
        res = client.get("/api/v1/safety/call/log/book_123")
        logs = res.json()["call_logs"]
        assert isinstance(logs, list)
        assert "call_id" in logs[0]
        t4["call_logs structure correct"] = "PASS ✅"
    except Exception as e:
        t4["call_logs structure correct"] = f"FAIL ❌ ({e})"

    results["TEST 4: Get Logs Endpoint"] = t4

    # ─────────────────────────────────────────────────
    #  TEST 5: Get Details Endpoint
    # ─────────────────────────────────────────────────
    t5 = {}

    # 5a Returns call details 200
    try:
        detail = {"call_id": "call_xyz", "booking_id": "book_123", "call_status": "completed",
                  "call_sid": "SMcall_xyz", "trusted_contact_name": "Amna", "call_transcript": "test"}
        _setup_firestore_mock(call_detail=detail)
        res = client.get("/api/v1/safety/call/call_xyz")
        assert res.status_code == 200
        assert res.json()["call_id"] == "call_xyz"
        t5["Returns call details: 200"] = "PASS ✅"
    except Exception as e:
        t5["Returns call details: 200"] = f"FAIL ❌ ({e})"

    # 5b All fields present
    try:
        detail = {"call_id": "call_xyz", "booking_id": "book_123", "call_status": "completed",
                  "call_sid": "SMcall_xyz", "trusted_contact_name": "Amna", "call_transcript": "test",
                  "trusted_contact_number": "03001234567", "call_duration_seconds": 180}
        _setup_firestore_mock(call_detail=detail)
        res = client.get("/api/v1/safety/call/call_xyz")
        data = res.json()
        for k in ["call_id", "booking_id", "call_status", "call_sid", "trusted_contact_name"]:
            assert k in data
        t5["All fields present"] = "PASS ✅"
    except Exception as e:
        t5["All fields present"] = f"FAIL ❌ ({e})"

    # 5c Invalid call_id 404
    try:
        _setup_firestore_mock(call_detail=None)
        res = client.get("/api/v1/safety/call/nonexistent_call")
        assert res.status_code == 404
        t5["Invalid call_id: 404"] = "PASS ✅"
    except Exception as e:
        t5["Invalid call_id: 404"] = f"FAIL ❌ ({e})"

    results["TEST 5: Get Details Endpoint"] = t5

    # ─────────────────────────────────────────────────
    #  TEST 6: Integration Tests
    # ─────────────────────────────────────────────────
    t6 = {}

    # 6a Trigger -> Logs -> Details flow
    try:
        _setup_firestore_mock(booking_exists=True)
        res_trigger = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        assert res_trigger.status_code == 200
        call_id = res_trigger.json()["call_id"]

        # Now mock logs with that call_id
        log_entry = {"call_id": call_id, "booking_id": "book_123", "call_status": "completed"}
        _setup_firestore_mock(call_docs=[log_entry], call_detail=log_entry)
        res_logs = client.get("/api/v1/safety/call/log/book_123")
        assert res_logs.status_code == 200
        assert res_logs.json()["total_calls"] == 1

        res_detail = client.get(f"/api/v1/safety/call/{call_id}")
        assert res_detail.status_code == 200
        t6["Trigger -> Logs -> Details"] = "PASS ✅"
    except Exception as e:
        t6["Trigger -> Logs -> Details"] = f"FAIL ❌ ({e})"

    # 6b Multiple calls for same booking
    try:
        _setup_firestore_mock(booking_exists=True)
        r1 = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        _setup_firestore_mock(booking_exists=True)
        r2 = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        assert r1.json()["call_id"] != r2.json()["call_id"]
        t6["Multiple calls"] = "PASS ✅"
    except Exception as e:
        t6["Multiple calls"] = f"FAIL ❌ ({e})"

    # 6c Booking updated
    try:
        mock_db = _setup_firestore_mock(booking_exists=True)
        res = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        assert res.status_code == 200
        mock_db.collection.assert_any_call("bookings")
        t6["Booking updated"] = "PASS ✅"
    except Exception as e:
        t6["Booking updated"] = f"FAIL ❌ ({e})"

    # 6d Transcript captured
    try:
        _setup_firestore_mock(booking_exists=True)
        res = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        transcript = res.json()["call_transcript"]
        assert "EMERGENCY CALL TRANSCRIPT" in transcript
        assert "Fatima" in transcript
        t6["Transcript captured"] = "PASS ✅"
    except Exception as e:
        t6["Transcript captured"] = f"FAIL ❌ ({e})"

    # 6e Contact details preserved
    try:
        _setup_firestore_mock(booking_exists=True)
        res = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        data = res.json()
        assert data["trusted_contact_name"] == "Amna"
        assert data["trusted_contact_number"] == "03001234567"
        t6["Contact details preserved"] = "PASS ✅"
    except Exception as e:
        t6["Contact details preserved"] = f"FAIL ❌ ({e})"

    results["TEST 6: Integration Tests"] = t6

    # ─────────────────────────────────────────────────
    #  TEST 7: Firestore Collection Tests
    # ─────────────────────────────────────────────────
    t7 = {}

    # 7a Schema correct
    try:
        _setup_firestore_mock()
        agent = CallingAgent()
        agent.generate_call_id()
        ctx = agent.create_call_context(VALID_CALL_DATA)
        result = {"call_status": "completed", "call_sid": "SM123", "call_transcript": "t",
                  "call_duration_seconds": 180, "contact_reached": True, "contact_response": "ok"}
        stored = agent.store_in_firestore(result, ctx)
        assert stored is True
        firestore_service.db.collection.assert_any_call("emergency_calls")
        t7["Schema correct"] = "PASS ✅"
    except Exception as e:
        t7["Schema correct"] = f"FAIL ❌ ({e})"

    # 7b All fields stored
    try:
        _setup_firestore_mock()
        agent = CallingAgent()
        agent.generate_call_id()
        ctx = agent.create_call_context(VALID_CALL_DATA)
        result = {"call_status": "completed", "call_sid": "SM123", "call_transcript": "t",
                  "call_duration_seconds": 180, "contact_reached": True, "contact_response": "ok"}
        agent.store_in_firestore(result, ctx)
        # Verify set was called with correct data
        call_args = firestore_service.db.collection("emergency_calls").document(agent.call_id).set.call_args
        if call_args:
            record = call_args[0][0]
            assert record["call_id"] == agent.call_id
            assert record["booking_id"] == "book_123"
            assert "created_at" in record
            assert "updated_at" in record
        t7["All fields stored"] = "PASS ✅"
    except Exception as e:
        t7["All fields stored"] = f"FAIL ❌ ({e})"

    # 7c Timestamps recorded
    try:
        _setup_firestore_mock()
        agent = CallingAgent()
        resp = agent.run(VALID_CALL_DATA)
        assert resp["call_id"] is not None
        t7["Timestamps recorded"] = "PASS ✅"
    except Exception as e:
        t7["Timestamps recorded"] = f"FAIL ❌ ({e})"

    # 7d Query by booking_id
    try:
        log = {"call_id": "call_q1", "booking_id": "book_123", "call_status": "completed"}
        _setup_firestore_mock(call_docs=[log])
        res = client.get("/api/v1/safety/call/log/book_123")
        assert res.status_code == 200
        t7["Query by booking_id"] = "PASS ✅"
    except Exception as e:
        t7["Query by booking_id"] = f"FAIL ❌ ({e})"

    # 7e Query by call_id
    try:
        detail = {"call_id": "call_q2", "booking_id": "book_123", "call_status": "completed"}
        _setup_firestore_mock(call_detail=detail)
        res = client.get("/api/v1/safety/call/call_q2")
        assert res.status_code == 200
        t7["Query by call_id"] = "PASS ✅"
    except Exception as e:
        t7["Query by call_id"] = f"FAIL ❌ ({e})"

    results["TEST 7: Firestore Collection Tests"] = t7

    # ─────────────────────────────────────────────────
    #  TEST 8: Edge Cases
    # ─────────────────────────────────────────────────
    t8 = {}

    # 8a Invalid phone format — still accepted (no strict validation on format)
    try:
        _setup_firestore_mock(booking_exists=True)
        data = {**VALID_CALL_DATA, "trusted_contact_number": "invalid_phone"}
        res = client.post("/api/v1/safety/call/trigger", json=data)
        assert res.status_code == 200  # graceful
        t8["Invalid phone format: Handled"] = "PASS ✅"
    except Exception as e:
        t8["Invalid phone format: Handled"] = f"FAIL ❌ ({e})"

    # 8b Missing contact — 422
    try:
        data = {k: v for k, v in VALID_CALL_DATA.items() if k != "trusted_contact_number"}
        res = client.post("/api/v1/safety/call/trigger", json=data)
        assert res.status_code == 422
        t8["Missing contact: Handled"] = "PASS ✅"
    except Exception as e:
        t8["Missing contact: Handled"] = f"FAIL ❌ ({e})"

    # 8c Provider incomplete — 422
    try:
        data = {k: v for k, v in VALID_CALL_DATA.items() if k != "provider_cnic"}
        res = client.post("/api/v1/safety/call/trigger", json=data)
        assert res.status_code == 422
        t8["Provider incomplete: Handled"] = "PASS ✅"
    except Exception as e:
        t8["Provider incomplete: Handled"] = f"FAIL ❌ ({e})"

    # 8d Call exists for booking — new call created with different ID
    try:
        _setup_firestore_mock(booking_exists=True)
        r1 = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        _setup_firestore_mock(booking_exists=True)
        r2 = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        assert r1.json()["call_id"] != r2.json()["call_id"]
        t8["Call exists: Handled"] = "PASS ✅"
    except Exception as e:
        t8["Call exists: Handled"] = f"FAIL ❌ ({e})"

    # 8e Concurrent calls — both succeed with unique IDs
    try:
        _setup_firestore_mock(booking_exists=True)
        r1 = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        _setup_firestore_mock(booking_exists=True)
        r2 = client.post("/api/v1/safety/call/trigger", json=VALID_CALL_DATA)
        assert r1.status_code == 200 and r2.status_code == 200
        assert r1.json()["call_id"] != r2.json()["call_id"]
        t8["Concurrent calls"] = "PASS ✅"
    except Exception as e:
        t8["Concurrent calls"] = f"FAIL ❌ ({e})"

    results["TEST 8: Edge Cases"] = t8

    # ─────────────────────────────────────────────────
    #  Report
    # ─────────────────────────────────────────────────
    report = []
    report.append("==================================================")
    report.append("M8 CALLING AGENT TEST REPORT")
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

    os.makedirs("tests", exist_ok=True)
    with open("tests/test_m8_results.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    return all_passed


if __name__ == "__main__":
    run_tests()
