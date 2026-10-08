# VERIRESUME – Intelligent Resume and Certificate Authenticity Verification System

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![SymPy](https://img.shields.io/badge/Math%20Engine-SymPy-3B5526.svg)](https://www.sympy.org/)
[![Socket](https://img.shields.io/badge/Protocol-TCP%20Sockets-00F0FF.svg)]()
[![Multiprocessing](https://img.shields.io/badge/Parallelism-Multiprocessing.Pool-FF6B6B.svg)]()
[![GUI](https://img.shields.io/badge/Desktop%20GUI-Tkinter%2Fttk-FFD43B.svg)]()

> **Academic Project: Advanced Programming Practice**  
> An intelligent, end-to-end credential integrity verification system that parses candidate resumes (PDF/DOCX), validates certifications over a low-level TCP socket client–server architecture, distributes concurrent verification jobs across CPU cores via multiprocessing, evaluates multi-variable authenticity equations using SymPy symbolic mathematics, and processes results using Functional Programming.

---

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [5 Core Python Concepts Demonstrated](#-5-core-python-concepts-demonstrated)
3. [System Architecture](#-system-architecture)
4. [Technology Stack](#-technology-stack)
5. [Installation & Setup](#-installation--setup)
6. [How to Run the Application](#-how-to-run-the-application)
7. [How to Demonstrate the 5 Concepts During Viva](#-how-to-demonstrate-the-5-concepts-during-viva)
8. [Test Scenarios & Demo Data](#-test-scenarios--demo-data)
9. [API Endpoints](#-api-endpoints)
10. [Database Architecture](#-database-architecture)
11. [Automated Test Suite](#-automated-test-suite)

---

## 🎯 Project Overview

VERIRESUME addresses resume and credential fraud by providing an automated, mathematical, and multi-interface auditing system.

### Key Capabilities:
- **Multi-Format Document Parsing**: PyMuPDF vector text extraction for PDF and `python-docx` for Word documents with OCR fallback.
- **Automated Credential Detection**: Context-aware heuristic and regular expression recognition of certification names, IDs, dates, issuing bodies, and verification URLs.
- **Decoupled TCP Socket Verification**: Verification queries are dispatched over raw TCP sockets (`AF_INET`, `SOCK_STREAM`) with JSON length-prefixed protocol framing.
- **Multiprocessing Worker Pool**: Batch credential verification is distributed across CPU cores concurrently using `multiprocessing.Pool`.
- **SymPy Symbolic Scoring Engine**: Authenticity scores are derived mathematically from a multi-variable symbolic equation with partial derivative sensitivity analysis.
- **Functional Programming Pipeline**: Data cleaning, record validation, scoring, and statistical aggregation are built with pure functions, closures, `map()`, `filter()`, and `reduce()`.
- **Dual User Interfaces**: A responsive cybersecurity-themed Web Dashboard (FastAPI/HTML5/CSS3/JS) and a native Desktop Admin GUI (Tkinter/ttk).

---

## 🧠 5 Core Python Concepts Demonstrated

| # | Advanced Concept | Primary Source File | Description & Concrete Implementation |
|---|---|---|---|
| 1 | **Functional Programming** | [`functional/functional_processing.py`](functional/functional_processing.py) | Pure deterministic functions, higher-order functions (`compose`, closure predicate factories), and a complete `map -> filter -> map -> reduce` pipeline for data normalization and score aggregation. |
| 2 | **Socket Programming** | [`networking/socket_server.py`](networking/socket_server.py)<br>[`networking/socket_client.py`](networking/socket_client.py) | Low-level TCP Client–Server architecture using `socket.socket(AF_INET, SOCK_STREAM)`, `bind()`, `listen()`, `accept()`, `recv()`, `sendall()`, big-endian length header message framing, client timeouts, and graceful offline fallback. |
| 3 | **Multiprocessing** | [`multiprocessing_module/parallel_verifier.py`](multiprocessing_module/parallel_verifier.py) | Parallel task distribution with `multiprocessing.Pool(processes=N)`, `pool.map()`, OS worker Process ID logging (`os.getpid()`), wall-time timing, and Windows-safe process spawning (`if __name__ == '__main__':`). |
| 4 | **SymPy Mathematics** | [`mathematics/authenticity_model.py`](mathematics/authenticity_model.py) | Symbolic variables (`sp.Symbol`), weighted expression formulation, exact value substitution (`expr.subs()`), numerical evaluation (`evalf()`), LaTeX output, and partial derivatives ($\frac{\partial \text{Score}}{\partial v_i}$) for weight sensitivity. |
| 5 | **Tkinter Desktop GUI** | [`gui/tkinter_app.py`](gui/tkinter_app.py) | Standalone desktop management panel with `ttk` widgets, file picker (`filedialog`), form validation, preset scenario loading, live socket health monitor, score badge, and an interactive `ttk.Treeview` audit log. |

---

## 🏗️ System Architecture

```
                                  USER INTERFACES
                 +-----------------------------------------------+
                 |  Web Dashboard (FastAPI)  |  Tkinter Admin GUI |
                 +-----------------------+-------+---------------+
                                         |       |
                                         |       | TCP Socket Request
                                         v       | (Length-Prefixed JSON)
                 +-------------------------------+               |
                 |      DOCUMENT PARSER          |               |
                 |  - PyMuPDF / python-docx      |               |
                 |  - Credential Detector & OCR  |               |
                 +---------------+---------------+               |
                                 |                               |
                                 v                               |
                 +-------------------------------+               |
                 |    MULTIPROCESSING POOL       |               |
                 | (multiprocessing.Pool Map)    |               |
                 +---------------+---------------+               |
                                 |                               |
                   Worker Process| Dispatches TCP Request         |
                                 +-----------------------+-------+
                                                         |
                                                         v
                                         +-------------------------------+
                                         |   TCP SOCKET SERVER (:9099)   |
                                         |    (AF_INET / SOCK_STREAM)    |
                                         +---------------+---------------+
                                                         |
                                                         v
                                         +-------------------------------+
                                         |   OFFICIAL / MOCK REGISTRY    |
                                         |     & COMPARISON ENGINE       |
                                         +---------------+---------------+
                                                         |
                                                         v
                                         +-------------------------------+
                                         |   SYMPY MATHEMATICAL SCORER   |
                                         |  Score = 30(Name) + 30(ID)... |
                                         +---------------+---------------+
                                                         |
                                                         v
                                         +-------------------------------+
                                         |     FUNCTIONAL FP PIPELINE    |
                                         |    map -> filter -> reduce    |
                                         +---------------+---------------+
                                                         |
                                                         v
                                         +-------------------------------+
                                         |    SQLITE DATABASE & REPORT   |
                                         +-------------------------------+
```

---

## 💻 Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, Pydantic
- **Document Processing**: PyMuPDF (fitz), python-docx, Pillow, pytesseract (OCR)
- **Symbolic Mathematics**: SymPy
- **Networking**: Native Python `socket`, `struct` (binary framing), `threading`
- **Concurrency**: Native Python `multiprocessing`
- **Desktop GUI**: Native Python `tkinter`, `ttk`
- **Database**: SQLite
- **Web Frontend**: HTML5, CSS3 (Cyber Glassmorphism theme), Vanilla JS, FontAwesome, SVG

---

## 📦 Installation & Setup

### 1. Clone or Open Workspace
```powershell
cd "d:\APP - Resume Recoganizer using AI"
```

### 2. Create and Activate Virtual Environment (Optional but Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Generate Test Sample Files (Pre-Created)
```powershell
python sample_data/create_samples.py
```

---

## 🚀 How to Run the Application

The application consists of three decoupled components that can be launched independently in separate terminals:

### Step 1: Start the TCP Socket Verification Server (Terminal 1)
```powershell
python run_socket_server.py
```
*Alternatively:*
```powershell
python -m networking.socket_server
```
> **Log Output:** `VERIRESUME Socket Server listening on TCP 127.0.0.1:9099`

---

### Step 2: Start the FastAPI Web Dashboard (Terminal 2)
```powershell
python run_server.py
```
*Alternatively:*
```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
> Open your web browser and navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### Step 3: Launch the Tkinter Desktop Admin Panel (Terminal 3)
```powershell
python run_gui.py
```
*Alternatively:*
```powershell
python -m gui.tkinter_app
```

---

## 🎓 How to Demonstrate the 5 Concepts During Viva

When presenting this project to an examiner or professor, follow this structured demonstration script:

### Concept 1: Functional Programming
- **File**: `functional/functional_processing.py`
- **Explanation**: Show the examiner that all data normalization uses **Pure Functions** that avoid mutating input dictionaries.
- **Key Code**:
  ```python
  # Pure function with immutability
  def normalize_certificate_dict(cert: Dict[str, Any]) -> Dict[str, Any]:
      return {**cert, "name_normalized": normalize_certificate_name(cert.get("name"))}

  # Functional pipeline: map -> filter -> map -> reduce
  normalized = list(map(normalize_certificate_dict, raw_certificates))
  valid = list(filter(is_valid_certificate_structure, normalized))
  results = list(map(verification_fn, valid))
  total_score = reduce(lambda acc, val: acc + val, [r["score"] for r in results], 0.0)
  ```
- **Where to show in UI**: Open the web page at `/tech#functional` or run `pytest tests/test_functional.py -v`.

---

### Concept 2: Socket Programming (Client–Server)
- **Files**: `networking/socket_server.py` and `networking/socket_client.py`
- **Explanation**: Explain that the verification logic does **not** run inside the web server process. Instead, verification requests are encoded as JSON packets, prefixed with a 4-byte network length header, and transmitted over TCP sockets (`AF_INET`, `SOCK_STREAM`).
- **Key Code**:
  ```python
  # Server
  self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  self.server_socket.bind((self.host, 9099))
  self.server_socket.listen(128)
  client_sock, addr = self.server_socket.accept()

  # Client Message Framing (4-byte length prefix)
  payload = json.dumps(req_dict).encode('utf-8')
  header = struct.pack('!I', len(payload))
  client_sock.sendall(header + payload)
  ```
- **Viva Demo**: Stop `run_socket_server.py` to demonstrate that the UI gracefully catches connection errors, displays `Socket: OFFLINE`, and flags credentials as `UNABLE TO VERIFY` without crashing.

---

### Concept 3: Multiprocessing
- **File**: `multiprocessing_module/parallel_verifier.py`
- **Explanation**: When a candidate has multiple credentials, verification tasks are mapped across separate operating system worker processes concurrently using `multiprocessing.Pool`.
- **Key Code**:
  ```python
  with Pool(processes=workers_to_use) as pool:
      verification_results = pool.map(verify_certificate_worker_task, normalized_inputs)
  ```
- **Viva Demo**:
  1. Upload `sample_data/sample_multi_cert_resume.pdf` (which contains 4 credentials).
  2. Click **"Verify All Credentials (Parallel)"**.
  3. Show the resulting diagnostics on the results dashboard displaying **4 separate worker PIDs** (e.g. `[33904, 14440, 1668, 25704]`).

---

### Concept 4: SymPy Symbolic Mathematics
- **File**: `mathematics/authenticity_model.py`
- **Explanation**: Rather than using arbitrary if-else math, SymPy creates a formal mathematical equation using symbolic variables:
  $$\text{Score} = 30 \cdot \text{name\_match} + 30 \cdot \text{certificate\_id\_match} + 20 \cdot \text{course\_match} + 10 \cdot \text{organization\_match} + 10 \cdot \text{date\_match}$$
- **Key Code**:
  ```python
  name_match, id_match, course_match, org_match, date_match = sp.symbols('name_match id_match ...')
  score_expr = 30*name_match + 30*id_match + 20*course_match + 10*org_match + 10*date_match
  # Substitution
  res = score_expr.subs({name_match: 1.0, id_match: 1.0, ...})
  numerical_score = float(res.evalf())
  ```
- **Viva Demo**: Show the partial derivatives sensitivity matrix ($\frac{\partial \text{Score}}{\partial \text{name\_match}} = 30$) rendered on `/tech#sympy` and in the formal printable report.

---

### Concept 5: Tkinter Desktop Admin GUI
- **File**: `gui/tkinter_app.py`
- **Explanation**: Demonstrates dual frontend integration. The desktop application communicates over TCP sockets with the same verification daemon as the web UI.
- **Viva Demo**:
  1. Run `python run_gui.py`.
  2. Click **"Sample: Valid"** and click **"VERIFY VIA TCP SOCKET"** (displays 100% VERIFIED).
  3. Click **"Sample: Mismatch"** and click **"VERIFY VIA TCP SOCKET"** (displays 70% REVIEW REQUIRED).
  4. Inspect the interactive Treeview history table.

---

## 🧪 Test Scenarios & Demo Data

The project includes pre-built sample test resumes in `sample_data/`:

| Scenario | Sample File | Candidate | Credential / ID | Expected Result | Score |
|---|---|---|---|---|---|
| **1. Exact Match** | `sample_alice_johnson_valid.pdf` | Alice Johnson | Python Programming (`CERT1001`) | **VERIFIED** | 100% |
| **2. Name Mismatch** | `sample_bob_smith_mismatch.pdf` | John Doe | Web Development (`CERT1002`) | **REVIEW REQUIRED** | 70% |
| **3. Revoked / Flagged** | `sample_revoked_cert_resume.pdf` | Fake Candidate | Python (`CERT9999`) | **FAILED** | 0% |
| **4. Multiprocessing (4 Certs)** | `sample_multi_cert_resume.pdf` | Alice Johnson | 4 Certs (`CERT1001`, `AWS-SAA-8842`, `DEEP-AI-991`, `CS50-HARVARD-2023`) | **PARALLEL POOL (4 PIDs)** | 92.5% |
| **5. DOCX Format** | `sample_resume_charlie.docx` | David Miller | GCP Data Engineer (`GCP-PDE-3011`) | **VERIFIED** | 100% |
| **6. Socket Offline** | Stop socket server | Any candidate | Any certificate | **UNABLE TO VERIFY** | 0% |

---

## 🌐 API Endpoints

| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web Dashboard Landing Page |
| `GET` | `/upload` | Resume Upload & Ingestion Page |
| `GET` | `/review/{resume_id}` | Certificate Review & Parallel Verify Trigger |
| `GET` | `/results/{resume_id}` | Results Dashboard with circular SymPy score gauge |
| `GET` | `/report/{resume_id}` | Formal Printable PDF Audit Report |
| `GET` | `/history` | SQLite Database Audit Log |
| `GET` | `/tech` | Academic Viva Demonstration Page |
| `GET` | `/health` | JSON Health Check & Socket Status |
| `POST` | `/upload-resume` | Upload & Parse PDF/DOCX resume |
| `POST` | `/verify-certificate` | Verify single certificate via TCP Socket |
| `POST` | `/verify-all` | Batch verification via `multiprocessing.Pool` |
| `GET` | `/resume/{resume_id}` | Fetch parsed resume and detected certificates |
| `GET` | `/api/report/{resume_id}` | Fetch JSON report metadata |

---

## 🗄️ Database Architecture

SQLite database initialized automatically in `data/veriresume.db` with the following SQLAlchemy models:
- **`candidates`**: Candidate name, email, phone, created_at.
- **`resumes`**: File name, type, size, raw extracted text, skills JSON, education JSON.
- **`certificates`**: Certificate title, ID, issuing organization, issue date, verification URL.
- **`verification_results`**: Status (`VERIFIED`, `REVIEW REQUIRED`, `SUSPICIOUS`, `FAILED`), SymPy score, field match flags (`name_match`, `id_match`, etc.), breakdown JSON, official record snapshot.
- **`verification_logs`**: System audit event log stream.

---

## 🧪 Automated Test Suite

To run all 25 automated unit and integration tests:

```powershell
pytest -v
```

### Run individual module tests:
```powershell
# Functional Programming tests
pytest tests/test_functional.py -v

# SymPy scoring tests
pytest tests/test_sympy.py -v

# Socket Server & Client tests
pytest tests/test_socket.py -v

# Multiprocessing Pool tests
pytest tests/test_multiprocessing.py -v

# Verification and Comparison tests
pytest tests/test_verification.py -v
```

---

## 📜 License
Academic Project – Developed for Advanced Programming Practice course evaluation.
