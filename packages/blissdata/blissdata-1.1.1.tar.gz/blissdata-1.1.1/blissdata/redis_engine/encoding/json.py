# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
import json
from collections.abc import Mapping
from . import EncodedBatch, StreamDecoder, StreamEncoder


class JsonStreamEncoder(StreamEncoder):
    def info(self):
        return {"type": "json"}

    def encode(self, data):
        assert isinstance(data, Mapping)
        return EncodedBatch(json.dumps(data).encode())


class JsonStreamDecoder(StreamDecoder):
    def __init__(self, encoding):
        assert encoding["type"] == "json"

    def decode(self, batches):
        return [json.loads(batch.payload) for batch in batches]
