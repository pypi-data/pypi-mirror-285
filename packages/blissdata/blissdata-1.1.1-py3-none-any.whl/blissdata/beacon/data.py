"""Get Bliss data information from Beacon."""

import struct
from ._base import BeaconClient
from ._base import IncompleteBeaconMessage


class BeaconData(BeaconClient):
    """Provides the API to read the redis databases urls."""

    REDIS_QUERY = 30
    REDIS_QUERY_ANSWER = 31

    REDIS_DATA_SERVER_QUERY = 32
    REDIS_DATA_SERVER_FAILED = 33
    REDIS_DATA_SERVER_OK = 34

    def get_redis_db(self) -> str:
        """Returns the URL of the Redis database that contains the Bliss settings.
        For example 'redis://foobar:25001' or 'unix:///tmp/redis.sock'."""
        while True:
            try:
                message_type, message, data = self._raw_get_redis_db()
                break
            except BrokenPipeError:
                self._connect(self._address, self._connection.timeout)

        if message_type != self.REDIS_QUERY_ANSWER:
            raise RuntimeError(f"Unexpected message type '{message_type}'")
        host, port = message.decode().split(":")
        if host == "localhost":
            return f"unix://{port}"
        else:
            return f"redis://{host}:{port}"

    def get_redis_data_db(self) -> str:
        """Returns the URL of the Redis database that contains the Bliss scan data.
        For example 'redis://foobar:25002' or 'unix:///tmp/redis_data.sock'."""
        response_type, data = self._request(self.REDIS_DATA_SERVER_QUERY, "")
        if response_type == self.REDIS_DATA_SERVER_OK:
            host, port = data.decode().split("|")[:2]
            if host == "localhost":
                return f"unix://{port}"
            else:
                return f"redis://{host}:{port}"
        elif response_type == self.REDIS_DATA_SERVER_FAILED:
            raise RuntimeError(data.decode())
        raise RuntimeError(f"Unexpected Beacon response type {response_type}")

    def _raw_get_redis_db(self):
        """redis_db cannot be retrieved with self._request(). Some commands are
        custom among the already custom beacon protocol."""
        msg = b"%s%s" % (struct.pack("<ii", self.REDIS_QUERY, 0), b"")
        self._connection.sendall(msg)
        data = b""
        while True:
            raw_data = self._connection.recv(16 * 1024)
            if not raw_data:
                # socket closed on server side (would have raised otherwise)
                raise BrokenPipeError
            data = b"%s%s" % (data, raw_data)
            try:
                return self._unpack_message(data)
            except IncompleteBeaconMessage:
                continue
