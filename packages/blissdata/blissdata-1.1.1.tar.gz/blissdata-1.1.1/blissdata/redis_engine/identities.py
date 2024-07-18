# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
from typing import Optional
from redis_om import HashModel, Field


class _UninitializedRedis:
    """Fake redis connection to raise clear exception if no Redis database has been configured"""

    def execute_command(*args, **kwargs):
        raise RuntimeError("Redis URL not initialized.")


class ESRFIdentityModel(HashModel):
    """Institute specific information used to link scans in Redis to external services."""

    class Meta:
        global_key_prefix = "esrf"
        model_key_prefix = "id"
        database = _UninitializedRedis()

    name: str = Field(index=True)
    number: int = Field(index=True)
    data_policy: str = Field(index=True)

    # ESRF data policy
    session: Optional[str] = Field(index=True, default=None)
    proposal: Optional[str] = Field(index=True, default=None)
    collection: Optional[str] = Field(index=True, default=None)
    dataset: Optional[str] = Field(index=True, default=None)

    # Without data policy
    path: Optional[str] = Field(index=True, default=None)
