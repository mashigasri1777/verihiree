"""
VeriHire AI – Automated Route & Feature Verification Test
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

routes_to_test = [
    ("/", 200, "Verify Resumes"),
    ("/dashboard", 200, "Recruiter Command Center"),
    ("/candidates", 200, "Candidate Directory"),
    ("/upload", 200, "Upload Candidate Resume"),
    ("/candidate/1", 200, "Sarah Chen"),
    ("/candidate/2", 200, "Marcus Vance"),
    ("/candidate/3", 200, "Elena Rostova"),
    ("/candidate/4", 200, "David Kim"),
    ("/verification-queue", 200, "Verification Queue"),
    ("/interviews", 200, "Interview Coordination"),
    ("/analytics", 200, "Analytics"),
    ("/report/1", 200, "Official Candidate Verification Audit"),
    ("/security", 200, "Enterprise Security"),
    ("/settings", 200, "Platform Settings"),
    ("/login", 200, "Recruiter Portal"),
    ("/health", 200, "healthy"),
]

passed = 0
failed = 0

print("=" * 60)
print(" VERIHIRE AI – RUNNING ROUTE INTEGRITY TESTS")
print("=" * 60)

for path, expected_status, expected_text in routes_to_test:
    res = client.get(path)
    if res.status_code == expected_status and expected_text in res.text:
        print(f" [PASS] {path} -> HTTP {res.status_code} (Verified '{expected_text}')")
        passed += 1
    else:
        print(f" [FAIL] {path} -> HTTP {res.status_code} (Expected {expected_status}, found '{expected_text}' in text: {expected_text in res.text})")
        failed += 1

# Test Decision Action
decision_res = client.post("/api/candidate/1/decision", json={"decision": "SHORTLISTED"})
if decision_res.status_code == 200:
    print(" [PASS] POST /api/candidate/1/decision -> SHORTLISTED")
    passed += 1
else:
    print(f" [FAIL] POST /api/candidate/1/decision -> {decision_res.status_code}")
    failed += 1

# Test Interview Scheduling
inv_res = client.post("/api/candidate/1/schedule-interview", json={
    "interview_type": "System Design & Architecture",
    "interviewer_name": "Sarah Jenkins",
    "scheduled_at": "2026-10-15T14:00:00",
    "notes": "Testing automated scheduling"
})
if inv_res.status_code == 200:
    print(" [PASS] POST /api/candidate/1/schedule-interview -> HTTP 200")
    passed += 1
else:
    print(f" [FAIL] POST /api/candidate/1/schedule-interview -> {inv_res.status_code}")
    failed += 1

# Test Sample Upload with sample PDF
sample_pdf = Path("sample_data/sample_alice_johnson_valid.pdf")
if sample_pdf.exists():
    with open(sample_pdf, "rb") as f:
        upload_res = client.post("/api/upload-resume", files={"file": ("sample_alice.pdf", f, "application/pdf")})
        if upload_res.status_code == 200 and "redirect_url" in upload_res.json():
            print(f" [PASS] POST /api/upload-resume -> HTTP 200 (Redirect: {upload_res.json()['redirect_url']})")
            passed += 1
        else:
            print(f" [FAIL] POST /api/upload-resume -> {upload_res.status_code}: {upload_res.text}")
            failed += 1

print("=" * 60)
print(f" SUMMARY: {passed} PASSED, {failed} FAILED")
print("=" * 60)

if failed > 0:
    sys.exit(1)
