# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
import redis
from functools import wraps
from dataclasses import dataclass
from collections.abc import Mapping
from beartype import beartype

from .encoding import EncodedBatch
from .encoding.json import JsonStreamDecoder
from .encoding.numeric import NumericStreamDecoder
from .exceptions import (
    EndOfStream,
    IndexNoMoreThereError,
    IndexNotYetThereError,
    IndexWontBeThereError,
    NoWritePermission,
    UnknownEncodingError,
)

try:
    from gevent.monkey import is_anything_patched
except ImportError:
    use_gevent = False
else:
    use_gevent = is_anything_patched()

if use_gevent:
    from .sink import DualStageGeventSink as RedisSink

    # from .sink import SingleStageGeventSink as RedisSink
else:
    from .sink import DualStageThreadSink as RedisSink

    # from .sink import SingleStageThreadSink as RedisSink

_MAX_STREAM_ID = 2**64 - 1


@dataclass
class StreamEntry:
    id: int
    length: int
    batch: EncodedBatch
    is_seal: bool

    @classmethod
    def from_raw(cls, raw):
        id = int(raw[0].split(b"-")[0])
        if id < _MAX_STREAM_ID:
            length = int(raw[1].get(b"len", 1))
            batch = EncodedBatch(raw[1][b"payload"], length)
            return cls(id=id, length=length, batch=batch, is_seal=False)
        else:
            # STREAM SEALING ENTRY
            # Don't use _MAX_STREAM_ID but get 'id' field instead,
            # so the following assert keeps true for any entry:
            #     total length = entry.id + entry.length
            id = int(raw[1][b"id"])
            return cls(id=id, length=0, batch=None, is_seal=True)


class Stream:
    """Stream objects are created in Read-Only or Read-Write mode. Two factory methods exist for this:
        - Stream.open(...)
        - Stream.create(...)

    For writing, it is very important to use a single RW instance per stream. Because each instance
    owns a socket, and writing to multiple sockets in parallel can't guarantee data ordering. You don't
    have to care when using a Scan object as it will handle Stream instantiation for you.

    Stream can be accessed like arrays, with index or slices, eg:
        my_stream[42]
        my_stream[20:203]
        my_stream[50:300:20]
        my_stream[-1] # be careful, this is only the current last, but it will likely change
        len(my_stream)

    Stream objects are simple to use when picking values by index, but if you need to keep up with
    many streams in a running scan. Then you should use a StreamingClient which provides synchronous
    primitives, like a blocking read, on multiple streams at the same time (based on redis xread).
    """

    def __init__(self, name, model):
        self._name = name
        self._model = model
        self._seal = None

    def needs_write_permission(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._write_permission:
                return func(self, *args, **kwargs)
            else:
                raise NoWritePermission(f"Stream {self} is read-only")

        return wrapper

    @property
    def name(self):
        return self._name

    @property
    def key(self):
        return self._model.key()

    @property
    def encoding(self):
        return self._model.encoding

    @property
    def info(self):
        return self._model.info

    def __len__(self):
        if self._seal is not None:
            return self._seal.id

        try:
            entry = self._revrange(count=1)[0]
            # TODO could check for seal here to update on the fly
        except IndexError:
            return 0
        return entry.length + entry.id

    def _range(self, max="+", min="-", count=None):
        raw = self._data_store._redis.xrange(self.key, min=min, max=max, count=count)
        if raw:
            return [StreamEntry.from_raw(item) for item in raw]
        else:
            return []

    def _revrange(self, max="+", min="-", count=None):
        raw = self._data_store._redis.xrevrange(self.key, min=min, max=max, count=count)
        if raw:
            return [StreamEntry.from_raw(item) for item in reversed(raw)]
        else:
            return []

    def is_sealed(self):
        # cache sealing info as it is final
        if self._seal is None:
            try:
                self._seal = self._revrange(min=_MAX_STREAM_ID)[0]
                assert self._seal.is_seal
            except IndexError:
                return False
        return True

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._get_index(key)
        elif isinstance(key, slice):
            return self._get_slice(key.start, key.stop, key.step)
        else:
            raise TypeError(
                f"stream indices must be integers or slices, not {type(key).__name__}"
            )

    def _get_index(self, index):
        if index < 0:
            if self.is_sealed():
                index += self._seal.id
                if index < 0:
                    raise IndexError("index out of range")
            else:
                raise IndexNotYetThereError(
                    "Negative index have no meaning before stream is sealed"
                )

        # succeed fast...
        result = self._revrange(max=index, count=1)
        if result:
            entry = result[0]
            if entry.id + entry.length > index:
                decoded = self._decoder.decode([entry.batch])
                return decoded[index - entry.id]

        # ...or fail slow
        # In case the requested index is not returned directly, it is read again
        # along with the last entry of the stream in a transaction. This way we
        # have an instant view of the stream length and sealing to raise the
        # proper exception.
        pipe = self._data_store._redis.pipeline(transaction=True)
        pipe.xrevrange(self.key, max=index, count=1)
        pipe.xrevrange(self.key, count=1)
        results = pipe.execute()
        entry, last_entry = [
            StreamEntry.from_raw(raw[0]) if raw else None for raw in results
        ]

        if last_entry is None:
            # the stream does not even exist
            raise IndexNotYetThereError(f"Index {index} not yet published")

        if entry is None:
            stream_len = last_entry.length + last_entry.id
            # ex: in [0, 1] array, [-2, -1, 0, 1] are valid indexes
            if -stream_len <= index < stream_len:
                raise IndexNoMoreThereError(f"Index {index} have been trimmed off")
            elif last_entry.is_seal:
                raise IndexWontBeThereError(
                    f"Stream is closed, there will be no index {index}"
                )
            else:
                raise IndexNotYetThereError(f"Index {index} not yet published")

        if entry.id + entry.length <= index:
            if last_entry.is_seal:
                raise IndexWontBeThereError(
                    f"Stream is closed, there will be no index {index}"
                )
            else:
                raise IndexNotYetThereError(f"Index {index} not yet published")

        decoded = self._decoder.decode([entry.batch])
        return decoded[index - entry.id]

    def _get_slice(self, start, stop, step):
        if start is None:
            start = 0
        elif start < 0:
            if self.is_sealed():
                start = max(start + self._seal.id, 0)
            else:
                raise IndexNotYetThereError(
                    "Negative index have no meaning before stream is sealed"
                )

        if stop is None or stop < 0:
            if self.is_sealed():
                if stop is None:
                    stop = self._seal.id
                else:
                    stop = max(stop + self._seal.id, 0)
            else:
                raise IndexNotYetThereError(
                    "Negative index have no meaning before stream is sealed"
                )

        if stop <= start:
            # Return empty data but in the decoder format.
            # Could be an empty numpy array, but with a precise shape for example.
            return self._decoder.decode([])

        entries = self._range(min=start, max=stop - 1)

        # if our slice is not aligned with batches in redis, we may need to retrieve
        # one more batch at the beginning.
        if not entries or entries[0].id > start:
            try:
                prev_entry = self._revrange(max=start, count=1)[0]
            except IndexError:
                if start < len(self):
                    raise IndexNoMoreThereError(f"Index {start} have been trimmed off")
                else:
                    # exceptions are only raised when part of the slice is trimmed
                    # otherwise return empty data, just like numpy.arange(3)[10:20]
                    return self._decoder.decode([])

            entries.insert(0, prev_entry)

        batches = (entry.batch for entry in entries)
        data = self._decoder.decode(batches)

        first_recv_id = entries[0].id
        stop = None if stop is None else (stop - first_recv_id)
        return data[(start - first_recv_id) : stop : step]

    @needs_write_permission
    def send(self, data):
        try:
            batch = self._encoder.encode(data)
        except TypeError as e:
            raise TypeError(f"Encoding of '{self.name}': {e}")

        self._sink.xadd(
            name=self.key,
            fields=batch.todict(),
            id=f"{self._write_index}-1",
        )
        self._write_index += batch.len

    @needs_write_permission
    def join(self):
        self._sink.join()

    @needs_write_permission
    def seal(self):
        self._sink.stop()
        try:
            return self._data_store._redis.fcall("seal_stream", 1, self.key)
        except redis.exceptions.ResponseError as e:
            if "is already sealed" in str(e):
                return len(self)
            else:
                raise

    def __del__(self):
        # Thread based sinks can't be garbage collected, because their internal thread
        # still hold a reference. Then it is sink's owner responsibility to stop them.
        if hasattr(self, "_sink"):
            try:
                self._sink.stop()
            except Exception:
                # Errors raised by sinks are ignored at garbage collection time.
                pass

    @classmethod
    def open(cls, data_store, name, model):
        stream = cls(name, model)
        stream._data_store = data_store
        if stream.encoding["type"] == "numeric":
            stream._decoder = NumericStreamDecoder(stream.encoding)
        elif stream.encoding["type"] == "json":
            stream._decoder = JsonStreamDecoder(stream.encoding)
        else:
            raise UnknownEncodingError(f"Unknow stream encoding {stream.encoding}")

        stream._write_permission = False
        return stream

    @classmethod
    def create(cls, data_store, name, model, encoder):
        stream = cls.open(data_store, name, model)
        stream._sink = RedisSink(data_store)
        stream._write_index = 0
        stream._encoder = encoder
        stream._write_permission = True
        return stream

    def cursor(self):
        return StreamCursor(self)

    def _parse_new_entries(self, entries):
        if entries[-1].is_seal:
            self._seal = entries.pop()

        if entries:
            batches = (entry.batch for entry in entries)
            data = self._decoder.decode(batches)
            return (entries[0].id, data)

        if self._seal is not None:
            raise EndOfStream()
        else:
            return None


class StreamCursor:
    @beartype
    def __init__(self, stream: Stream):
        self._stream = stream
        self._streaming_client = StreamingClient([stream])

    @property
    def position(self):
        return self._streaming_client.position[self._stream.key]

    def read(self, block=True, timeout=0, count=0):
        try:
            try:
                return self._streaming_client.read(block, timeout, count)[self._stream]
            except KeyError:
                if self._stream._seal:
                    raise EndOfStream()
                else:
                    return (self.position, [])
        except EndOfStream as e:
            raise EndOfStream from e


class StreamingClient:
    """Synchronous client to read multiple streams at once.
    A StreamingClient is created from a list of streams and keeps an index for each of them.
    Indexes are initialized to the origin of each stream.

    Calls to .read() will get data from the beginning of each stream, but you can skip past
    data with:
        _ = client.read(block=False, count=-1)
    This will read only the last available entry of each stream, updating the indexes
    accordingly.
    """

    def __init__(self, streams):
        if isinstance(streams, Mapping):
            streams = streams.values()

        data_store_set = {stream._data_store for stream in streams}
        if len(data_store_set) > 1:
            raise NotImplementedError(
                "StreamingClient cannot read streams from different data stores."
            )
        try:
            self._data_store = data_store_set.pop()
        except KeyError:
            self._data_store = None

        # reversed dictionary to associate data received to its Stream object
        self._key_to_stream = {stream.key: stream for stream in streams}
        self._stream_ids = {stream.key: 0 for stream in streams}
        self._sealed_ids = {}

    @property
    def position(self):
        return {**self._stream_ids, **self._sealed_ids}

    def _read_from_end(self, count=0):
        # Read last n available entries from each stream:
        # xread can read multiple streams at once, but it can't ask for the last n entries.
        # Instead we send one xrevrange command per stream and group them in a pipeline.
        pipe = self._data_store._redis.pipeline(transaction=False)
        stream_ids = list(self._stream_ids.items())
        for key, idx in stream_ids:
            pipe.xrevrange(key, min=idx, count=count)
        raw = pipe.execute()
        entries = {
            key: [StreamEntry.from_raw(raw_entry) for raw_entry in reversed(raw_stream)]
            for (key, _), raw_stream in zip(stream_ids, raw)
            if raw_stream
        }

        # When a seal is found, we need to read one more entry to compensate for the count.
        # Otherwise read(count=-1) on a sealed stream returns [] instead of the last value.
        # This doesn't cost much as it happens only once in a stream.
        pipe = self._data_store._redis.pipeline(transaction=False)
        sealed_streams = []  # but needs another reading
        for key, stream_entries in entries.items():
            if stream_entries and stream_entries[-1].is_seal:
                prev_entry_id = stream_entries[0].id - 1
                if prev_entry_id < self._stream_ids[key]:
                    continue
                pipe.xrevrange(
                    key, min=self._stream_ids[key], max=prev_entry_id, count=1
                )
                sealed_streams.append(key)
        raw = pipe.execute()

        for key, raw_entry in zip(sealed_streams, raw):
            try:
                entry = StreamEntry.from_raw(raw_entry[0])
            except IndexError:
                stream = self._key_to_stream[key]
                stream._seal = entries[key][-1]
                self._sealed_ids[key] = len(stream)
                del self._stream_ids[key]
                raise IndexNoMoreThereError(
                    f"{stream.name}: requested index has expired."
                )
            entries[key].insert(0, entry)

        output = {}
        for key, stream_entries in entries.items():
            stream = self._key_to_stream[key]
            try:
                data = stream._parse_new_entries(stream_entries)
                if data:
                    output[stream] = data
                    self._stream_ids[key] = (
                        stream_entries[-1].id + stream_entries[-1].length
                    )
            except EndOfStream:
                self._sealed_ids[key] = len(stream)
                del self._stream_ids[key]

        return output

    def read(self, block=True, timeout=0, count=0):
        """For each stream, read N entries between the last known index and the actual end of
        the stream in Redis (where N depends on 'count' argument).

        Important note: A stream entry can contain several data points. This is the writer of
        the stream to choose to batch or not.

        - When 'count' is zero, all entries since the last index position are read and index
        is moved to the end of the stream. (No entry is skipped)

        - When 'count' is positive, at most 'count' entries are read in each stream and indexes
        are moved accordingly. (No entry is skipped)

        - When 'count' is negative, at most 'abs(count)' entries are read in each stream, but if
        more are available, only the last ones are returned while the other are simply skipped.
        This reading mode can be used for monitoring, because it allows to pick up entries only
        when needed while skipping the rest.

        Note: It is perfectly possible to switch between modes on the fly:
            For example, monitoring values every 5 seconds (count=-1), then switch to contiguous
            reading when it becomes interesting (count=0).
        """
        assert timeout >= 0
        if not self._stream_ids:
            raise EndOfStream("All streams have been read until the end")

        expect_contiguous = count >= 0

        if not block:
            timeout = None
        else:
            timeout = int(timeout * 1000)

        if count < 0:
            count = -count
            streams_data = self._read_from_end(count)

            if streams_data:
                return streams_data
            elif not self._stream_ids:
                raise EndOfStream("All streams have been read until the end")
            elif not block:
                return {}

            #  _read_from_end returned no data and block is true, we can now fallback to blocking xread

        # TODO should we add a count limit to protect Redis from big requests (can slow down server)
        if count == 0:
            count = None

        # use N-0 indices with xread
        raw = self._data_store._redis.xread(
            self._stream_ids, block=timeout, count=count
        )
        entries = {
            raw_key.decode(): [
                StreamEntry.from_raw(raw_entry) for raw_entry in raw_stream
            ]
            for raw_key, raw_stream in raw
            if raw_stream
        }

        output = {}
        for key, stream_entries in entries.items():
            stream = self._key_to_stream[key]

            if expect_contiguous:
                expected_index = self._stream_ids[key]
                actual_index = stream_entries[0].id
                if expected_index != actual_index:
                    raise IndexNoMoreThereError()

            try:
                data = stream._parse_new_entries(stream_entries)
                if data:
                    output[stream] = data
                    self._stream_ids[key] = (
                        stream_entries[-1].id + stream_entries[-1].length
                    )
            except EndOfStream:
                self._sealed_ids[key] = len(stream)
                del self._stream_ids[key]

        if output:
            return output
        elif not self._stream_ids:
            raise EndOfStream("All streams have been read until the end")
        else:
            return {}
