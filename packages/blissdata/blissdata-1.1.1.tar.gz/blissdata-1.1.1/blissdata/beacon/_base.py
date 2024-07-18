"""Base client to communicate with Beacon."""

import platform
import socket
import struct
import threading
from typing import Optional
from . import config


class IncompleteBeaconMessage(Exception):
    """Raised when a received message is incomplete"""


class BeaconClient:
    """Synchronous blocking Beacon client.

    It takes a host and port to a beacon server to be instantiated or
    uses the BEACON_HOST environment variable when when missing.
    """

    HEADER_SIZE = struct.calcsize("<ii")

    def __init__(
        self, host: Optional[str] = None, port: Optional[int] = None, timeout=3.0
    ):
        if host is None or port is None:
            address = config.get_beacon_address()
        else:
            address = host, port
        self._connect(address, timeout)
        self._cursor_id = 0
        self._lock = threading.Lock()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(host='{self._address[0]}', port={self._address[1]})"
        )

    def _connect(self, address, timeout):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if platform.system() != "Windows":
            connection.setsockopt(socket.SOL_IP, socket.IP_TOS, 0x10)
        connection.connect(address)
        connection.settimeout(timeout)
        self._address = address
        self._connection = connection

    def close(self):
        """Close the connection to Beacon."""
        self._connection.close()
        self._connection = None

    def _request(self, message_id, param1):
        """Send a request and returns (message_type, data)"""
        while True:
            try:
                message_key = self._gen_message_key()
                content = f"{message_key}|{param1}".encode()
                header = struct.pack("<ii", message_id, len(content))
                msg = b"%s%s" % (header, content)
                self._connection.sendall(msg)
                return self._read(message_key)
            except BrokenPipeError:
                self._connect(self._address, self._connection.timeout)

    def _gen_message_key(self):
        """Generate a unique message key.

        This is not really needed for a synchronous service.
        It could be a fixed value.
        """
        self._cursor_id = (self._cursor_id + 1) % 100000
        return "%s" % self._cursor_id

    def _unpack_message(self, s):
        header_size = self.HEADER_SIZE
        if len(s) < header_size:
            raise IncompleteBeaconMessage
        message_type, message_len = struct.unpack("<ii", s[:header_size])
        if len(s) < header_size + message_len:
            raise IncompleteBeaconMessage
        message = s[header_size : header_size + message_len]
        remaining = s[header_size + message_len :]
        return message_type, message, remaining

    def _read(self, expected_message_key):
        data = b""
        while True:
            raw_data = self._connection.recv(16 * 1024)
            if not raw_data:
                # socket closed on server side (would have raised otherwise)
                raise BrokenPipeError
            data = b"%s%s" % (data, raw_data)
            try:
                message_type, message, data = self._unpack_message(data)
            except IncompleteBeaconMessage:
                continue
            break
        message_key, data = self._get_msg_key(message)
        if message_key != expected_message_key:
            raise RuntimeError(f"Unexpected message key '{message_key}'")
        return message_type, data

    def _get_msg_key(self, message):
        pos = message.find(b"|")
        if pos < 0:
            return message.decode(), None
        return message[:pos].decode(), message[pos + 1 :]
