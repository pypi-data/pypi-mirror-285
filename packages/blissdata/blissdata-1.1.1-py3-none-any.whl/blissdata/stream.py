# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
from blissdata.h5api import dynamic_hdf5
from blissdata.lima.client import lima_client_factory
from blissdata.redis_engine.exceptions import (
    EndOfStream,
    IndexWontBeThereError,
    IndexNotYetThereError,
    IndexNoMoreThereError,
)


class FileBackedStream:
    def __init__(self, stream, file_path, data_path):
        self._stream = stream
        self._file_path = file_path
        self._data_path = data_path

    @property
    def name(self):
        return self._stream.name

    @property
    def info(self):
        return self._stream.info

    def is_sealed(self):
        return self._stream.is_sealed()

    def __len__(self):
        return len(self._stream)

    def __getitem__(self, key):
        # TODO do not reopen File for every __getitem__
        # TODO cache expired indexes for faster fallback
        try:
            return self._stream[key]
        except IndexNoMoreThereError:
            with dynamic_hdf5.File(
                self._file_path, retry_timeout=0, retry_period=0
            ) as nxroot:
                return nxroot[self._data_path][key]

    def cursor(self):
        return FileBackedStreamCursor(self)


class FileBackedStreamCursor:
    def __init__(self, stream):
        assert isinstance(stream, FileBackedStream)
        self._stream = stream
        self._fallback = False
        self._position = 0

        self._sub_stream = self._stream._stream
        self._sub_cursor = self._sub_stream.cursor()

    @property
    def position(self):
        return self._position

    def read(self, block=True, timeout=0, count=0):
        if not self._fallback:
            try:
                data = self._sub_cursor.read(block, timeout, count)
                if len(data):
                    self._position = self._sub_cursor.position
                return data
            except IndexNoMoreThereError:
                self._fallback = True
        if count == 0:
            key = slice(self._position, None)
        elif count > 0:
            key = slice(self._position, self._position + count)
        else:
            raise NotImplementedError(
                "FileBackedStream doesn't support negative index on files"
            )

        with dynamic_hdf5.File(
            self._stream._file, retry_timeout=0, retry_period=0
        ) as nxroot:
            while not self._stream._stream.is_sealed() or self._position < len(
                self._stream._stream
            ):
                data = nxroot[self._stream._path][key]
                if len(data) > 0:
                    retval = (self._position, data)
                    self._position += len(data)
                    return retval
            raise EndOfStream


class LimaStream:
    """Same API as a Stream but with a lima client inside to dereference events into images.
    Will support any Lima version as long as there is a client for it."""

    def __init__(self, stream, ref_mode=False):
        self._client = lima_client_factory(stream._data_store, stream.info, ref_mode)
        self._json_stream = stream
        self._cursor = stream.cursor()

    @property
    def name(self):
        return self._json_stream.name

    @property
    def info(self):
        return self._json_stream.info

    def is_sealed(self):
        return self._json_stream.is_sealed()

    def __len__(self):
        self._update_client()
        return len(self._client)

    def _update_client(self, block=False, timeout=0):
        try:
            _, data = self._cursor.read(block, timeout, count=-1)
        except EndOfStream:
            return
        if len(data):
            self._client.update(**data[0])

    def __getitem__(self, key):
        if isinstance(key, slice):
            need_update = key.stop is None or not (0 <= key.stop < len(self._client))
        else:
            need_update = not (0 <= key < len(self._client))

        if need_update:
            self._update_client()

        try:
            return self._client[key]
        except IndexError:
            # TODO could be verified before asking the client
            index = key.start if isinstance(key, slice) else key
            if index < 0:
                index += len(self._client)
            if index >= len(self._client):
                if self._json_stream.is_sealed():
                    raise IndexWontBeThereError
                else:
                    raise IndexNotYetThereError
            else:
                raise IndexNoMoreThereError

    def cursor(self):
        return LimaStreamCursor(self)


class LimaStreamCursor:
    def __init__(self, stream):
        assert isinstance(stream, LimaStream)
        self._lima_stream = stream
        self._position = 0

    @property
    def position(self):
        return self._position

    def read(self, block=True, timeout=0, count=0):
        available_frames = len(self._lima_stream._client) - self._position
        need_update = count < 0 or count > available_frames
        if need_update:
            if available_frames > 0:
                # update but don't wait for 'count' frames if some are already available
                block = False
            self._lima_stream._update_client(block, timeout)
            if self._position >= len(self._lima_stream._client):
                if self._lima_stream._json_stream._seal:
                    raise EndOfStream
                else:
                    return self._lima_stream._client[0:0]  # empty list or array

        if count == 0:
            key = slice(self._position, None)
        elif count > 0:
            key = slice(self._position, self._position + count)
        elif count == -1:
            key = slice(-1, None)
        else:
            raise NotImplementedError(
                f"-1 is the only supported negative index in {type(self).__name__}"
            )

        frames = self._lima_stream._client[key]

        if len(frames) == 0:
            return (self._position, frames)

        if count >= 0:
            retval = (self._position, frames)
            self._position += len(frames)
            return retval
        else:
            self._position = len(self._lima_stream._client) + count
            return (self._position, frames)
