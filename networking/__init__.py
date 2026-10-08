"""
VERIRESUME Networking Module
Implements TCP Client-Server architecture for certificate verification requests.
"""

from .socket_server import SocketVerificationServer, run_server
from .socket_client import SocketVerificationClient, send_verification_request, is_socket_server_alive

__all__ = [
    "SocketVerificationServer",
    "run_server",
    "SocketVerificationClient",
    "send_verification_request",
    "is_socket_server_alive",
]
