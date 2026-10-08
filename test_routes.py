"""
VeriHire AI – Direct Route & Controller Unit Test
Tests all HTML page templates and API logic directly with database sessions.
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from starlette.requests import Request
from backend.database import SessionLocal, Candidate, init_db
import main

# Ensure database is seeded
init_db()

db = SessionLocal()

# Mock Starlette Request
def make_mock_request(path: str = "/"):
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [],
        "query_string": b"",
        "server": ("127.0.0.1", 8000),
    }
    return Request(scope)

passed = 0
failed = 0

print("=" * 65)
print(" VERIHIRE AI – DIRECT ROUTE CONTROLLER & TEMPLATE TESTS")
print("=" * 65)

# 1. Landing Page
try:
    res = main.page_landing(make_mock_request("/"))
    assert res.status_code == 200
    assert "Verify Resumes" in res.body.decode("utf-8")
    print(" [PASS] GET / (Landing Page)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /: {e}")
    failed += 1

# 2. Auth Page
try:
    res = main.page_auth(make_mock_request("/login"))
    assert res.status_code == 200
    assert "Recruiter Portal" in res.body.decode("utf-8")
    print(" [PASS] GET /login (Recruiter Auth)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /login: {e}")
    failed += 1

# 3. Dashboard Page
try:
    res = main.page_dashboard(make_mock_request("/dashboard"), db=db)
    assert res.status_code == 200
    assert "Recruiter Command Center" in res.body.decode("utf-8")
    print(" [PASS] GET /dashboard (Recruiter Dashboard)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /dashboard: {e}")
    failed += 1

# 4. Candidates Directory
try:
    res = main.page_candidates(make_mock_request("/candidates"), db=db)
    assert res.status_code == 200
    assert "Candidate Directory" in res.body.decode("utf-8")
    print(" [PASS] GET /candidates (Candidate Directory)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /candidates: {e}")
    failed += 1

# 5. Upload Page
try:
    res = main.page_upload(make_mock_request("/upload"), db=db)
    assert res.status_code == 200
    assert "Upload Candidate Resume" in res.body.decode("utf-8")
    print(" [PASS] GET /upload (Resume Dropzone & Stepper)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /upload: {e}")
    failed += 1

# 6. Candidate Profile Pages (All 4 Demo Candidates)
for cid, expected_name in [(1, "Sarah Chen"), (2, "Marcus Vance"), (3, "Elena Rostova"), (4, "David Kim")]:
    try:
        res = main.page_candidate_profile(candidate_id=cid, request=make_mock_request(f"/candidate/{cid}"), db=db)
        assert res.status_code == 200
        body_text = res.body.decode("utf-8")
        assert expected_name in body_text
        print(f" [PASS] GET /candidate/{cid} ({expected_name} Profile & Verification Checks)")
        passed += 1
    except Exception as e:
        print(f" [FAIL] GET /candidate/{cid}: {e}")
        failed += 1

# 7. Verification Queue Page
try:
    res = main.page_verification_queue(make_mock_request("/verification-queue"), db=db)
    assert res.status_code == 200
    assert "Verification Queue" in res.body.decode("utf-8")
    print(" [PASS] GET /verification-queue (Human Review Queue)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /verification-queue: {e}")
    failed += 1

# 8. Interviews Page
try:
    res = main.page_interviews(make_mock_request("/interviews"), db=db)
    assert res.status_code == 200
    assert "Interview Coordination" in res.body.decode("utf-8")
    print(" [PASS] GET /interviews (Interviews Management)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /interviews: {e}")
    failed += 1

# 9. Analytics Page
try:
    res = main.page_analytics(make_mock_request("/analytics"), db=db)
    assert res.status_code == 200
    assert "Analytics" in res.body.decode("utf-8")
    print(" [PASS] GET /analytics (Analytics Dashboard)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /analytics: {e}")
    failed += 1

# 10. Formal Verification Report Page
try:
    res = main.page_report("1", make_mock_request("/report/1"), db=db)
    assert res.status_code == 200
    assert "Official Candidate Verification Audit" in res.body.decode("utf-8")
    print(" [PASS] GET /report/1 (Downloadable / Printable Audit Report)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /report/1: {e}")
    failed += 1

# 11. Security Page
try:
    res = main.page_security(make_mock_request("/security"), db=db)
    assert res.status_code == 200
    assert "Enterprise Security" in res.body.decode("utf-8")
    print(" [PASS] GET /security (Security & Compliance)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /security: {e}")
    failed += 1

# 12. Settings Page
try:
    res = main.page_settings(make_mock_request("/settings"), db=db)
    assert res.status_code == 200
    assert "Platform Settings" in res.body.decode("utf-8")
    print(" [PASS] GET /settings (Settings)")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /settings: {e}")
    failed += 1

# 13. API: Recruiter Decision Endpoint
try:
    dec_res = main.api_candidate_decision(candidate_id=1, payload={"decision": "SHORTLISTED"}, db=db)
    assert dec_res["status"] == "success"
    assert dec_res["decision"] == "SHORTLISTED"
    print(" [PASS] POST /api/candidate/1/decision (Shortlist Action)")
    passed += 1
except Exception as e:
    print(f" [FAIL] POST /api/candidate/1/decision: {e}")
    failed += 1

# 14. API: Schedule Interview Endpoint
try:
    inv_res = main.api_schedule_interview(
        candidate_id=1,
        payload={
            "interview_type": "Technical Screening Round",
            "interviewer_name": "Sarah Jenkins",
            "scheduled_at": "2026-10-15T15:00:00",
            "notes": "Automated test unit interview"
        },
        db=db
    )
    assert inv_res["status"] == "success"
    print(" [PASS] POST /api/candidate/1/schedule-interview (Schedule Interview)")
    passed += 1
except Exception as e:
    print(f" [FAIL] POST /api/candidate/1/schedule-interview: {e}")
    failed += 1

# 15. API: Manual Verify Override Endpoint
try:
    ov_res = main.api_candidate_manual_verify(candidate_id=3, db=db)
    assert ov_res["status"] == "success"
    print(" [PASS] POST /api/candidate/3/verify-manual (Human Verification Override)")
    passed += 1
except Exception as e:
    print(f" [FAIL] POST /api/candidate/3/verify-manual: {e}")
    failed += 1

# 16. Health Endpoint
try:
    h_res = main.health_check()
    assert h_res["status"] == "healthy"
    print(" [PASS] GET /health")
    passed += 1
except Exception as e:
    print(f" [FAIL] GET /health: {e}")
    failed += 1

db.close()

print("=" * 65)
print(f" FINAL RESULT: {passed} PASSED, {failed} FAILED")
print("=" * 65)

if failed > 0:
    sys.exit(1)
