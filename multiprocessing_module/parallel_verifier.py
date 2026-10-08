"""
VERIRESUME - Multiprocessing Parallel Verification Module
==========================================================
This module implements concurrent certificate verification across multiple CPU cores
using Python's native multiprocessing module (multiprocessing.Pool).

Key Multiprocessing Features Demonstrated:
1. Parallel worker pool allocation: multiprocessing.Pool(processes=N)
2. Task distribution with pool.map() across distinct OS processes
3. Process identification using os.getpid() and multiprocessing.current_process().name
4. Windows process safety with top-level picklable worker functions
5. Concurrency diagnostics and execution timing measurements
6. Integration with the Functional Programming Result Pipeline
"""

import os
import sys
import time
import logging
from multiprocessing import Pool, current_process
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from networking.socket_client import SocketVerificationClient
from functional.functional_processing import summarize_verification_batch, normalize_certificate_dict

logger = logging.getLogger("ParallelVerifier")


def verify_certificate_worker_task(certificate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Picklable top-level worker task executed inside a dedicated OS process.
    Connects to the TCP Socket Verification Server to verify the certificate claim.
    """
    start_time = time.perf_counter()
    pid = os.getpid()
    proc_name = current_process().name

    # Create worker-local socket client
    client = SocketVerificationClient(
        host=config.SOCKET_HOST,
        port=config.SOCKET_PORT,
        timeout=config.SOCKET_TIMEOUT
    )

    # Dispatch request to TCP Socket Server
    result = client.verify_certificate(certificate)

    end_time = time.perf_counter()
    duration_ms = round((end_time - start_time) * 1000, 2)

    # Attach multiprocessing audit metadata
    result["multiprocessing_meta"] = {
        "worker_pid": pid,
        "worker_name": proc_name,
        "execution_time_ms": duration_ms,
        "parallel_execution": True
    }

    return result


def verify_certificates_in_parallel(
    certificates: List[Dict[str, Any]],
    max_workers: Optional[int] = None
) -> Dict[str, Any]:
    """
    Distributes a list of certificate records across multiple worker processes
    using multiprocessing.Pool, then aggregates the results using Functional Programming.
    """
    if not certificates:
        return {
            "results": [],
            "summary": summarize_verification_batch([]),
            "diagnostics": {
                "total_certificates": 0,
                "workers_used": 0,
                "total_wall_time_ms": 0.0,
                "multiprocessing_enabled": True
            }
        }

    total_certs = len(certificates)
    # Determine optimal worker count (bounded by CPU count and certificate count)
    available_cpus = os.cpu_count() or 4
    workers_to_use = max(1, min(total_certs, available_cpus, max_workers or config.DEFAULT_WORKER_PROCESSES))

    wall_start = time.perf_counter()

    # Pre-normalize certificates
    normalized_inputs = [normalize_certificate_dict(c) for c in certificates]

    # Execute parallel verification via multiprocessing.Pool
    try:
        with Pool(processes=workers_to_use) as pool:
            verification_results = pool.map(verify_certificate_worker_task, normalized_inputs)
    except Exception as e:
        logger.error(f"Multiprocessing pool execution error: {e}. Falling back to sequential execution.")
        verification_results = [verify_certificate_worker_task(c) for c in normalized_inputs]

    wall_end = time.perf_counter()
    total_wall_time_ms = round((wall_end - wall_start) * 1000, 2)

    # Functional Programming Pipeline: Aggregate summary using FP reduce/filter/map
    summary = summarize_verification_batch(verification_results)

    # Extract worker PIDs used
    worker_pids = list(set([
        r.get("multiprocessing_meta", {}).get("worker_pid", 0)
        for r in verification_results
    ]))

    diagnostics = {
        "total_certificates": total_certs,
        "workers_used": workers_to_use,
        "worker_pids": worker_pids,
        "total_wall_time_ms": total_wall_time_ms,
        "average_time_per_cert_ms": round(total_wall_time_ms / total_certs, 2) if total_certs > 0 else 0,
        "multiprocessing_enabled": True,
        "pool_type": "multiprocessing.Pool"
    }

    return {
        "results": verification_results,
        "summary": summary,
        "diagnostics": diagnostics
    }


if __name__ == "__main__":
    # Test block for direct module execution
    test_certs = [
        {"certificate_id": "CERT1001", "candidate_name": "Alice Johnson", "certificate_name": "Python Programming", "issuing_organization": "Demo Institute"},
        {"certificate_id": "CERT1002", "candidate_name": "Bob Smith", "certificate_name": "Web Development", "issuing_organization": "Demo Institute"},
        {"certificate_id": "AWS-SAA-8842", "candidate_name": "Sarah Connor", "certificate_name": "AWS Certified Solutions Architect", "issuing_organization": "Amazon Web Services"},
        {"certificate_id": "CERT9999", "candidate_name": "Fake Candidate", "certificate_name": "Python Programming", "issuing_organization": "Demo Institute"},
    ]
    print("Testing Multiprocessing Verification...")
    res = verify_certificates_in_parallel(test_certs, max_workers=4)
    print(f"Verified {len(res['results'])} certificates in {res['diagnostics']['total_wall_time_ms']} ms across {res['diagnostics']['workers_used']} workers.")
    print(f"Summary: {res['summary']}")
