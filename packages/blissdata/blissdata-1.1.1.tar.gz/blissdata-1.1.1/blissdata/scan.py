# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
from .redis_engine.scan import Scan as RedisScan
from .redis_engine.scan import ScanState
from .redis_engine.stream import Stream
from .stream import LimaStream, FileBackedStream


class Scan(RedisScan):
    @property
    def streams(self):
        if self.state < ScanState.PREPARED:
            return {}
        if len(self._streams) != len(self._model.data_streams):

            for name, stream_model in self._model.data_streams.items():
                stream = Stream.open(self._data_store, name, stream_model)
                self._streams[name] = stream

                try:
                    self._streams[name] = LimaStream(stream)
                    continue
                except ValueError:
                    pass

                if self.info.get("save", False):
                    try:
                        file_path = self.path
                        data_path = stream.info["data_path"]
                    except KeyError:
                        pass
                    else:
                        self._streams[name] = FileBackedStream(
                            stream, file_path, data_path
                        )

        return self._streams.copy()
