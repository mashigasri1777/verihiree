"""
VERIRESUME - TCP Socket Verification Server
===========================================
This module implements a dedicated TCP verification server using Python's native
socket library (AF_INET, SOCK_STREAM).

Key Socket Programming Features Demonstrated:
1. Low-level socket creation: socket.socket(socket.AF_INET, socket.SOCK_STREAM)
2. Binding to IP/Port: server_socket.bind((HOST, PORT))
3. Listening for connections: server_socket.listen(backlog)
4. Accepting client connections: client_socket, addr = server_socket.accept()
5. Framing protocol: 4-byte big-endian length-prefixed JSON messaging
6. Multi-threaded request dispatching for concurrent client servicing
7. Graceful socket teardown and error handling
8. Server logging to file and console
"""

import socket
import threading
import struct
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from backend.verification_engine import default_verification_engine
from verification.mock_verifier import MOCK_OFFICIAL_REGISTRY

# Configure Logging
log_file = config.LOGS_DIR / "socket_server.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SocketServer] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SocketServer")


def send_msg(sock: socket.socket, msg_dict: Dict[str, Any]) -> None:
    """Helper: Serializes dict to JSON and sends with a 4-byte length prefix."""
    payload = json.dumps(msg_dict, default=str).encode('utf-8')
    # Pack 4-byte length header in big-endian network byte order (!I)
    header = struct.pack('!I', len(payload))
    sock.sendall(header + payload)


def recv_msg(sock: socket.socket) -> Optional[Dict[str, Any]]:
    """Helper: Receives 4-byte length header followed by the exact JSON payload."""
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
        logger.error(f"Error decoding incoming socket message: {e}")
        return None


def recvall(sock: socket.socket, n: int) -> Optional[bytes]:
    """Helper: Ensures all n bytes are received from the socket stream."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)


class SocketVerificationServer:
    """
    Standalone TCP Socket Server for handling certificate verification requests.
    """

    def __init__(self, host: str = config.SOCKET_HOST, port: int = config.SOCKET_PORT):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.threads = []

    def start(self):
        """Initializes and binds the TCP socket server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of local addresses
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(128)
            self.is_running = True
            logger.info(f"VERIRESUME Socket Server listening on TCP {self.host}:{self.port}")
            logger.info("Ready to accept verification requests from FastAPI, Tkinter GUI, and Multiprocessing workers...")

            while self.is_running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"Accepted TCP connection from {client_address[0]}:{client_address[1]}")
                    
                    # Spawn client handler thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    self.threads.append(client_thread)
                except socket.error:
                    if not self.is_running:
                        break
        except Exception as e:
            logger.error(f"Socket server startup failure on {self.host}:{self.port}: {e}")
        finally:
            self.stop()

    def handle_client(self, client_socket: socket.socket, client_address: Any):
        """Processes client request payload and transmits JSON response."""
        try:
            client_socket.settimeout(10.0)
            request = recv_msg(client_socket)
            
            if not request:
                logger.debug(f"Connection probe closed from {client_address}")
                return

            req_type = request.get("request_type", "verify_certificate")
            logger.info(f"Received request '{req_type}' from {client_address}")

            if req_type == "ping" or req_type == "health":
                response = {
                    "status": "healthy",
                    "server": "VERIRESUME TCP Socket Server",
                    "protocol": "TCP/JSON Framing",
                    "port": self.port
                }

            elif req_type == "verify_certificate":
                certificate = request.get("certificate", {})
                res = default_verification_engine.verify_single_certificate(certificate)
                response = {
                    "status": "success",
                    "result": res
                }

            elif req_type == "batch_verify":
                certificates = request.get("certificates", [])
                results = [default_verification_engine.verify_single_certificate(c) for c in certificates]
                response = {
                    "status": "success",
                    "results": results,
                    "count": len(results)
                }

            elif req_type == "get_official_records":
                response = {
                    "status": "success",
                    "records": list(MOCK_OFFICIAL_REGISTRY.values())
                }

            else:
                response = {
                    "status": "error",
                    "message": f"Unknown request type: {req_type}"
                }

            send_msg(client_socket, response)
            logger.info(f"Response successfully sent to {client_address}")

        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
            try:
                error_response = {
                    "status": "error",
                    "message": str(e)
                }
                send_msg(client_socket, error_response)
            except Exception:
                pass
        finally:
            try:
                client_socket.close()
            except Exception:
                pass

    def stop(self):
        """Gracefully stops the socket server."""
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
                logger.info("Socket server successfully stopped.")
            except Exception as e:
                logger.error(f"Error closing server socket: {e}")


def run_server():
    """CLI Entrypoint for running the socket server."""
    server = SocketVerificationServer()
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down...")
        server.stop()


if __name__ == "__main__":
    run_server()
