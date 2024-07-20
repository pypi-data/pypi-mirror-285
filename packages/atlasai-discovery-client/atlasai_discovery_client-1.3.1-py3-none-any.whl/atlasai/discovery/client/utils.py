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

def paginate(fn, *args, **kwargs):
    """
    Helper function for handling paginated responses

    Given that all search methods (e.g. `product.search()`) are paginated,
    it is tedious to iterate through all search results. The `paginate` function
    makes it easy to loop through the results in a repeatable manner
    #### Usage

    ```python
    from atlasai.discovery import client

    query = client.paginate(CLIENT_FUNCTION, *args **kwargs)
    ```

    `*args` and `*kwargs` are directly passed to the `CLIENT_FUNCTION`

    Returns a python generator that can be used in a for loop

    ```python
    for obj in query:
        pass
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: query = client.paginate(
       ...:   client.product.search,
       ...:   odata='''contains(product.internal_name, 'atlasai.')'''
       ...: )

    In [3]: for product in query:
       ...:     print(product.internal_name)
    ```
    """

    offset = kwargs.pop('offset', 0)
    while True:
        response = fn(*args, offset=offset, **kwargs)
        objects = getattr(
            response,
            next(
                k
                for k in dir(response)
                if (
                    not k.startswith('_') and
                    hasattr(getattr(response, k), 'results')
                )
            )
        )
        for result in objects.results:
            yield result

        if not objects.more:
            break

        offset = objects.next_offset

paginator = paginate
