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

"""
## Bulk operations on Releases
"""

from sgqlc.operation import Operation

from . import endpoint, misc, schema
from .release import build_input

__all__ = [
    'create',
    'update',
    'delete',
]

CreateInput = misc.build_namespace_input(schema.CreateReleaseInput)
UpdateInput = misc.build_namespace_input(schema.UpdateReleaseInputWithId)

def create(*inputs, return_objects=False):
    """
    Bulk create Releases. Each Release can be expressed as either a `CreateInput` object or a python dictionary

    #### Usage

    Using `CreateInput`

    ```python
    from atlasai.discovery import client

    response = client.releases.create(
      client.releases.CreateInput(
        product_id_or_name=<PRODUCT_ID_OR_NAME>,
        ...
      ),
      ...
      client.releases.CreateInput(
        product_id_or_name=<PRODUCT_ID_OR_NAME>,
        ...
      ),
    )
    ```

    or using dictionaries

    ```python
    from atlasai.discovery import client

    response = client.releases.create(
      {
        "product_id_or_name": <PRODUCT_ID_OR_NAME>,
        ...
      },
      ...
      {
        "product_id_or_name": <PRODUCT_ID_OR_NAME>,
        ...
      },
    )
    ```
    """

    _inputs = [
        build_input(
            schema.CreateReleaseInput,
            **misc.input_as_dict(input_),
        )
        for input_ in inputs
    ]

    op = Operation(schema.Mutation)
    op.create_releases(inputs=_inputs).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.create_releases
    else:
        return response

def update(*inputs, return_objects=False):
    """
    Bulk update Releases. Each Release can be expressed as either a `UpdateInput` object or a python dictionary

    #### Usage

    Using `UpdateInput`

    ```python
    from atlasai.discovery import client

    response = client.releases.update(
      client.releases.UpdateInput(
        id=<RELEASE_ID>,
        ...
      ),
      ...
      client.releases.UpdateInput(
        id=<RELEASE_ID>,
        ...
      ),
    )
    ```

    or using dictionaries

    ```python
    from atlasai.discovery import client

    response = client.releases.update(
      {
        "id": <RELEASE_ID>,
        ...
      },
      ...
      {
        "id": <RELEASE_ID>,
        ...
      },
    )
    ```
    """

    _inputs = [
        build_input(
            schema.UpdateReleaseInputWithId,
            **misc.input_as_dict(input_),
        )
        for input_ in inputs
    ]

    op = Operation(schema.Mutation)
    op.update_releases(inputs=_inputs).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.update_releases
    else:
        return response

def delete(*ids, return_objects=False):
    """
    Bulk delete Releases by providing `id`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.releases.delete(<RELEASE_ID>, ...)
    ```
    """

    op = Operation(schema.Mutation)
    op.delete_releases(
        ids=ids,
    ).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.delete_releases
    else:
        return response
