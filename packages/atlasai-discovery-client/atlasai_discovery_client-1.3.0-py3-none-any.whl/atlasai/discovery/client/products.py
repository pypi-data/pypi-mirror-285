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
## Bulk operations on Products
"""

from sgqlc.operation import Operation

from . import endpoint, misc, schema
from .product import build_input

__all__ = [
    'create',
    'update',
    'delete',
]

CreateInput = misc.build_namespace_input(schema.CreateProductInput)
UpdateInput = misc.build_namespace_input(schema.UpdateProductInputWithId)

def create(*inputs, return_objects=False):
    """
    Bulk create Products. Each Product can be expressed as either a `CreateInput` object or a python dictionary

    #### Usage

    Using `CreateInput`

    ```python
    from atlasai.discovery import client

    response = client.products.create(
      client.products.CreateInput(
        internal_name=<INTERNAL_NAME>,
        ...
      ),
      ...
      client.products.CreateInput(
        internal_name=<INTERNAL_NAME>,
        ...
      ),
    )
    ```

    or using dictionaries

    ```python
    from atlasai.discovery import client

    response = client.products.create(
      {
        "internal_name": <INTERNAL_NAME>,
        ...
      },
      ...
      {
        "internal_name": <INTERNAL_NAME>,
        ...
      },
    )
    ```
    """

    _inputs = [
        build_input(
            schema.CreateProductInput,
            **misc.input_as_dict(input_)
        )
        for input_ in inputs
    ]

    op = Operation(schema.Mutation)
    op.create_products(inputs=_inputs).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.create_products
    else:
        return response

def update(*inputs, return_objects=False):
    """
    Bulk update Products. Each Product can be expressed as either a `UpdateInput` object or a python dictionary

    #### Usage

    Using `UpdateInput`

    ```python
    from atlasai.discovery import client

    response = client.products.update(
      client.products.UpdateInput(
        id=<PRODUCT_ID_OR_NAME>,
        ...
      ),
      ...
      client.products.UpdateInput(
        id=<PRODUCT_ID_OR_NAME>,
        ...
      ),
    )
    ```

    or using dictionaries

    ```python
    from atlasai.discovery import client

    response = client.products.update(
      {
        "id": <PRODUCT_ID_OR_NAME>,
        ...
      },
      ...
      {
        "id": <PRODUCT_ID_OR_NAME>,
        ...
      },
    )
    ```
    """

    _inputs = [
        build_input(
            schema.UpdateProductInputWithId,
            **misc.input_as_dict(input_)
        )
        for input_ in inputs
    ]

    op = Operation(schema.Mutation)
    op.update_products(inputs=_inputs).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.update_products
    else:
        return response

def delete(*ids, return_objects=False):
    """
    Bulk delete Products by providing `id` or `internal_name`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.products.delete(
        <PRODUCT_ID_OR_NAME>,
        ...
        <PRODUCT_ID_OR_NAME>,
    )
    ```
    """

    op = Operation(schema.Mutation)
    op.delete_products(
        ids=ids,
    ).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.delete_products
    else:
        return response
