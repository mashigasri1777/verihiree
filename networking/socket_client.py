"""
VERIRESUME - TCP Socket Verification Client
===========================================
This module implements the TCP client that communicates with the Verification Server.
Used by FastAPI endpoints, Multiprocessing workers, and the Tkinter Desktop Admin GUI.

Key Features:
1. Low-level TCP socket connection creation
2. JSON framing with length prefix header
3. Socket timeout configuration and connection error handling
4. Graceful fallback when socket server is offline
"""

import socket
import struct
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config

logger = logging.getLogger("SocketClient")


def send_msg(sock: socket.socket, msg_dict: Dict[str, Any]) -> None:
    """Serializes dict to JSON and sends with a 4-byte length prefix."""
    payload = json.dumps(msg_dict, default=str).encode('utf-8')
    header = struct.pack('!I', len(payload))
    sock.sendall(header + payload)


def recv_msg(sock: socket.socket) -> Optional[Dict[str, Any]]:
    """Receives length header followed by JSON payload."""
    try:
        header_data = recvall(sock, 4)
        if not header_data or len(header_data) < 4:
            return None
        
        msg_len = struct.unpack('!I', header_data)[0]
        payload_data = recvall(sock, msg_len)
        if not payload_data:
            return None
            
        return json.loads(payload_data.decode('utf-8'))
    except Exception as e:
        logger.error(f"Error decoding socket response: {e}")
        return None


def recvall(sock: socket.socket, n: int) -> Optional[bytes]:
    """Receives exact byte count from stream."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)


class SocketVerificationClient:
    """
    Client for transmitting verification payloads over TCP sockets.
    """

    def __init__(self, host: str = config.SOCKET_HOST, port: int = config.SOCKET_PORT, timeout: float = config.SOCKET_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout

    def _execute_request(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Opens TCP connection, sends payload, receives response, closes connection."""
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.settimeout(self.timeout)

        try:
            client_sock.connect((self.host, self.port))
            send_msg(client_sock, request_payload)
            response = recv_msg(client_sock)
            
            if response is None:
                return {
                    "status": "error",
                    "message": "Empty response received from verification server."
                }
            return response

        except (ConnectionRefusedError, TimeoutError, socket.timeout) as e:
            logger.warning(f"Socket connection error to {self.host}:{self.port} - {e}")
            return {
                "status": "connection_failed",
                "error": str(e),
                "message": f"Could not connect to TCP Verification Server at {self.host}:{self.port}. Please ensure socket server is running."
            }
        except Exception as e:
            logger.error(f"Socket client error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": f"Socket client error: {e}"
            }
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def ping(self) -> bool:
        """Checks if the socket server is online and accepting connections."""
        res = self._execute_request({"request_type": "ping"})
        return res.get("status") == "healthy"

    def verify_certificate(self, certificate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends single certificate verification request over TCP socket.
        """
        req = {
            "request_type": "verify_certificate",
            "certificate": certificate
        }
        res = self._execute_request(req)

        if res.get("status") == "success" and "result" in res:
            return res["result"]
        elif res.get("status") == "connection_failed":
            # Return graceful UNABLE_TO_VERIFY result so caller never crashes
            return {
                "certificate_name": certificate.get("certificate_name") or certificate.get("name") or "Unnamed",
                "candidate_name": certificate.get("candidate_name") or certificate.get("candidate") or "Unknown",
                "certificate_id": certificate.get("certificate_id") or certificate.get("id") or "N/A",
                "issuing_organization": certificate.get("issuing_organization") or certificate.get("organization") or "N/A",
                "issue_date": certificate.get("issue_date") or certificate.get("date") or "N/A",
                "verification_url": certificate.get("verification_url") or "",
                "status": "UNABLE_TO_VERIFY",
                "score": 0.0,
                "checks": {
                    "name_match": False,
                    "certificate_id_match": False,
                    "course_match": False,
                    "organization_match": False,
                    "date_match": False,
                },
                "official_record": None,
                "verification_source": "TCP SOCKET CLIENT (OFFLINE)",
                "details": res.get("message", "TCP Socket Server offline."),
                "breakdown": {}
            }
        else:
            return {
                "certificate_name": certificate.get("certificate_name") or certificate.get("name") or "Unnamed",
                "candidate_name": certificate.get("candidate_name") or certificate.get("candidate") or "Unknown",
                "certificate_id": certificate.get("certificate_id") or certificate.get("id") or "N/A",
                "issuing_organization": certificate.get("issuing_organization") or certificate.get("organization") or "N/A",
                "issue_date": certificate.get("issue_date") or certificate.get("date") or "N/A",
                "verification_url": certificate.get("verification_url") or "",
                "status": "UNABLE_TO_VERIFY",
                "score": 0.0,
                "checks": {},
                "official_record": None,
                "verification_source": "TCP SOCKET ERROR",
                "details": res.get("message", "Verification service error."),
                "breakdown": {}
            }

    def batch_verify(self, certificates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sends batch verification request over TCP socket."""
        req = {
            "request_type": "batch_verify",
            "certificates": certificates
        }
        res = self._execute_request(req)
        if res.get("status") == "success" and "results" in res:
            return res["results"]
        # Fallback to single verification loop if batch failed
        return [self.verify_certificate(c) for c in certificates]

    def get_official_records(self) -> List[Dict[str, Any]]:
        """Fetches known official registry records from the socket server."""
        req = {"request_type": "get_official_records"}
        res = self._execute_request(req)
        return res.get("records", [])


# Default client instance
default_socket_client = SocketVerificationClient()


def send_verification_request(certificate: Dict[str, Any]) -> Dict[str, Any]:
    """Top-level convenience function for sending verification requests over TCP socket."""
    return default_socket_client.verify_certificate(certificate)


def is_socket_server_alive() -> bool:
    """Top-level convenience check for socket server health."""
    return default_socket_client.ping()
