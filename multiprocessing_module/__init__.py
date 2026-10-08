"""
VERIRESUME Multiprocessing Module
Implements parallel certificate verification across CPU worker processes.
"""

from .parallel_verifier import (
    verify_certificates_in_parallel,
    verify_certificate_worker_task,
)

__all__ = [
    "verify_certificates_in_parallel",
    "verify_certificate_worker_task",
]
