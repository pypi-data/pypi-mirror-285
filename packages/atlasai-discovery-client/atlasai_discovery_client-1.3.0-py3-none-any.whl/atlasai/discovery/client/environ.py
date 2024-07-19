# Copyright 2024 AtlasAI PBC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from os import environ

__all__ = [
    'environment',
]

logger = logging.getLogger(__name__)

class EnvironContext:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __enter__(self):
        self._environ = {
            k: environ.get(k)
            for k in self._kwargs.keys()
        }

        for k, v in self._kwargs.items():
            if v is not None:
                environ[k] = v
                logger.debug(f'Set env var: {k} => {v}')
            elif environ.get(k) is not None:
                del environ[k]
                logger.debug(f'Cleared env var: {k} => {v}')

    def __exit__(self, *args, **kwargs):
        for k, v in self._environ.items():
            if v is not None:
                environ[k] = v
                logger.debug(f'Restored env var: {k} => {v}')
            elif environ.get(k) is not None:
                del environ[k]
                logger.debug(f'Cleared env var: {k} => {v}')

environment = EnvironContext
