# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
# required by python 3.8
from __future__ import annotations

import enum
import redis
import json
import math
import numpy as np
from functools import wraps

from redis_om.model import model
from pydantic import ValidationError

from .stream import Stream
from .exceptions import (
    UnauthorizeStateTransition,
    ScanNotFoundError,
    ScanValidationError,
    NoWritePermission,
)

scan_creation_stream = "_SCAN_HISTORY_"


class ScanState(enum.IntEnum):
    """A scan can only evolve to a state with a strictly greater order.
    This allows to wait for a state to be over, without enumerating all the next possible cases.
    """

    CREATED = 0
    PREPARED = 1
    STARTED = 2
    STOPPED = 3
    CLOSED = 4


def add_property(inst, name, getter, setter=None, deleter=None):
    cls = type(inst)
    module = cls.__module__
    if not hasattr(cls, "__perinstance"):
        cls = type(cls.__name__, (cls,), {})
        cls.__perinstance = True
        cls.__module__ = module
        inst.__class__ = cls
    setattr(cls, name, property(getter, setter, deleter))


class Scan:
    def needs_write_permission(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._write_permission:
                return func(self, *args, **kwargs)
            else:
                raise NoWritePermission(f"Scan {self} is read-only")

        return wrapper

    @classmethod
    def _load(cls, data_store, key):
        scan = cls()
        scan._write_permission = False
        scan._data_store = data_store

        prefix = scan._data_store._scan_model.make_key("")
        if not key.startswith(prefix):
            raise RuntimeError(f"Scan key should be prefixed by '{prefix}'")

        id_model = cls._get_identity_model_cls(scan)
        cls._expose_identity_model_fields(scan, id_model)

        scan._streams = {}
        scan._last_entry_id = b"0-0"
        try:
            # pk is just unprefixed version of key
            pk = key[len(prefix) :]
            scan._model = scan._data_store._scan_model.get(pk)
        except model.NotFoundError as e:
            raise ScanNotFoundError(
                "Scan has been deleted from Redis, or key is wrong"
            ) from e
        except ValidationError as e:
            raise ScanValidationError(
                "Scan exists in Redis but is invalid, most likely the scan model version on the publisher side is different"
            ) from e
        else:
            scan._state = ScanState.CREATED
            scan.update(block=False)

        return scan

    @classmethod
    def _create(cls, data_store, identity, info={}):
        scan = cls()
        scan._write_permission = True
        scan._data_store = data_store

        id_model = cls._get_identity_model_cls(scan)
        scan._model = scan._data_store._scan_model(
            id=id_model(**identity),
            info=info,
            state_stream=scan._data_store._stream_model(),
            data_streams={},
        )
        cls._expose_identity_model_fields(scan, id_model)

        scan._streams = {}
        scan._writer_streams = {}
        scan._state = ScanState.CREATED

        scan._model.info = Scan._filter_nan_values(scan._model.info)

        def _create_scan(pipe: redis.client.Pipeline) -> None:
            scan._model.save(pipeline=pipe)
            pipe.xadd(scan_creation_stream, {"key": scan.key}, maxlen=2048)
            pipe.xadd(scan._model.state_stream.key(), {"state": scan.state.value})

        scan._data_store._redis.transaction(_create_scan)
        scan.json_info = ""  # TODO to be removed, used to check info modification between state transitions
        return scan

    @staticmethod
    def _get_identity_model_cls(scan):
        """Get the scan identity class."""
        # pydantic v2
        #  id.field: <class 'pydantic.fields.FieldInfo'>
        #  id.field.annotation: <class 'redis_om.model.model.ModelMeta'>
        #
        # pydantic v1
        #  id.field:  <class 'pydantic.fields.ModelField'>
        #  id.field.annotation: <class 'redis_om.model.model.ModelMeta'>
        return scan._data_store._scan_model.id.field.annotation

    @staticmethod
    def _expose_identity_model_fields(scan, id_model):
        """Expose scan identity fields as properties of the scan instance."""
        # id_model: <class 'redis_om.model.model.ModelMeta'>
        #
        #  pydantic v2: id_model.model_fields or id_model.__fields__
        #  pydantic v1: id_model.__fields__
        try:
            prop_names = list(id_model.model_fields)
        except AttributeError:
            prop_names = list(id_model.__fields__)
        for prop_name in prop_names:
            if prop_name == "pk":
                continue

            def get_id_field(self, field=prop_name):
                return getattr(self._model.id, field, None)

            add_property(scan, prop_name, get_id_field)

    @classmethod
    def _load_rw(cls, data_store, key):
        scan = Scan._load(data_store, key)
        scan._write_permission = True
        scan._writer_streams = {}
        scan.json_info = ""
        return scan

    @staticmethod
    def _filter_nan_values(obj):
        # json_constant_map = {
        #     "-Infinity": float("-Infinity"),
        #     "Infinity": float("Infinity"),
        #     "NaN": None,
        # }

        class NumpyEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, np.ndarray):
                    return o.tolist()
                else:
                    return json.JSONEncoder.default(self, o)

        def format_bytes(nbytes):
            suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
            exp = int(math.log(nbytes, 1024))
            return f"{nbytes/1024**exp:.4g}{suffixes[exp]}"

        # Inspired from https://stackoverflow.com/a/65317610
        # Only solution found to replace NaN values with null, which is valid in JSON.
        # Other solutions imply new dependency or overriding methods which are not
        # supposed to be in json module.
        def json_nan_to_none(obj):
            json_string = NumpyEncoder().encode(obj)
            json_size = len(json_string)
            if json_size > 2**20:
                raise RuntimeError(
                    f"Scan JSON metadata is taking {format_bytes(json_size)} (limit 1MB)"
                )
            return json.loads(json_string, parse_constant=lambda constant: None)
            # OR to define specific value for each constant
            # return json.loads(json_string, parse_constant=lambda constant: json_constant_map[constant])

        return json_nan_to_none(obj)

    @property
    def key(self):
        return self._model.key()

    @property
    def info(self):
        return self._model.info

    @info.setter
    @needs_write_permission
    def info(self, info):
        self._model.info = info

    @property
    def state(self):
        return self._state

    @property
    def streams(self):
        if self.state < ScanState.PREPARED:
            return {}
        if len(self._streams) != len(self._model.data_streams):
            self._streams = {
                name: Stream.open(self._data_store, name, model)
                for name, model in self._model.data_streams.items()
            }
        return self._streams.copy()

    def __str__(self):
        return f'{type(self).__name__}(key:"{self.key}")'

    def update(self, block=True, timeout=0) -> bool:
        """Update scan state and its content.
        If the scan is already in a terminal state, False is returned immediately.
        Otherwise it depends on 'block' and 'timeout' in seconds (timeout=0: wait forever).
        Return a True if the scan state has changed.
        Raise ScanNotFoundError if the scan is deleted."""
        # Updating a scan in RW mode makes no sense, there should be one writer only, so he never needs to read.
        assert not self._write_permission

        # Ensure scan is not deleted, neither it is soon to be
        # -1: scan has no planned expiration
        # -2: scan already expired
        #  n: scan expire in n seconds
        ttl = self._data_store._redis.ttl(self.key)
        if ttl != -1 and ttl <= 10:
            raise ScanNotFoundError("Scan has been deleted from Redis")

        if self.state == ScanState.CLOSED:
            return False

        if not block:
            timeout = None
        else:
            timeout = int(timeout * 1000)

        # Because of expiration time, the scan can't have disappeared after the check we made at the beginning of
        # this function. Therefore scan.state_stream exists and we won't get stucked on a non-existing stream.
        result = self._data_store._redis.xread(
            {self._model.state_stream.key(): self._last_entry_id}, block=timeout
        )
        if not result:
            if timeout == 0:
                raise RuntimeError(
                    "Redis blocking XREAD returned empty value, this is very unexpected !"
                )
            else:
                return False

        # Entries contain state, only last one is meaningful
        last_entry = result[0][1][-1]
        self._last_entry_id = last_entry[0].decode()
        self._state = ScanState(int(last_entry[1][b"state"]))

        # refresh json local copy on state change
        try:
            self._model = self._data_store._scan_model.get(self._model.pk)
        except model.NotFoundError as e:
            raise ScanNotFoundError("Scan has been deleted from Redis") from e
        except ValidationError as e:
            raise ScanValidationError(
                "Scan exists in Redis but is invalid, most likely the scan model version on the publisher side is different"
            ) from e

        return True

    @needs_write_permission
    def create_stream(self, name, encoder, info={}) -> Stream:
        """Create a new data stream for the scan and return the associated Stream"""
        if name in self._model.data_streams.keys():
            raise RuntimeError(f'Stream "{name}" already exists.')
        model = self._data_store._stream_model(encoding=encoder.info(), info=info)
        stream = Stream.create(self._data_store, name, model, encoder)
        self._model.data_streams[name] = model
        self._writer_streams[name] = stream
        return stream

    @needs_write_permission
    def _close_stream_writers(self):
        """Seal streams that are not sealed yet.
        In the case of multiple processes/threads writing to the scan's streams,
        it is each writer's responsibility to seal its stream. Then the scan owner
        can wait for streams to be sealed and close the scan smoothly.
        Eventually, it may timeout and force the closure of all streams, making
        the still running writers to fail.
        """
        for stream_writer in self._writer_streams.values():
            stream_writer.seal()
        self._writer_streams = {}

    @needs_write_permission
    def prepare(self):
        if self.state is ScanState.CREATED:
            self._set_state(ScanState.PREPARED)
        else:
            raise UnauthorizeStateTransition(self.state, ScanState.PREPARED)

    @needs_write_permission
    def start(self):
        if self.state is ScanState.PREPARED:
            self._set_state(ScanState.STARTED)
        else:
            raise UnauthorizeStateTransition(self.state, ScanState.STARTED)

    @needs_write_permission
    def stop(self):
        if self.state is ScanState.STARTED:
            self._close_stream_writers()
            self._set_state(ScanState.STOPPED)
        else:
            raise UnauthorizeStateTransition(self.state, ScanState.STOPPED)

    @needs_write_permission
    def close(self):
        self._close_stream_writers()
        self._set_state(ScanState.CLOSED)

    @needs_write_permission
    def _set_state(self, state):
        prev_state = self._state
        self._state = state

        self._model.info = Scan._filter_nan_values(self._model.info)

        def update_scan_state(pipe: redis.client.Pipeline) -> None:
            json_info = json.dumps(self._model.info)

            if json_info != self.json_info:
                assert (
                    prev_state is ScanState.CREATED and state is ScanState.PREPARED
                ) or state is ScanState.CLOSED, f"Scan info changed between states {ScanState(prev_state).name} and {ScanState(state).name}"
            self.json_info = json_info

            self._model.save(pipeline=pipe)
            pipe.xadd(self._model.state_stream.key(), {"state": self.state.value})

        self._data_store._redis.transaction(update_scan_state)
