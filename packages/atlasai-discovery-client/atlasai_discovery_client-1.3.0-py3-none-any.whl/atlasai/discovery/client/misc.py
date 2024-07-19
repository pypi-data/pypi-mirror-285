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

def build_input_builder(helpers=None):
    helpers = helpers or {}

    def wrapper(Input, **kwargs):
        params = {}
        for field in Input:
            k = field.name
            if k not in kwargs:
                continue

            v = kwargs[k]
            params[k] = helpers[k](v) if k in helpers else v

        return Input(**params)

    return wrapper

def build_namespace_input(input_, class_name=None):
    assert hasattr(input_, '__field_names__')

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        if name not in self.__field_names__:
            raise ValueError(f'Unsupported attribute: {name}')
        self.__dict__[name] = value

    attributes = {
        '__field_names__': input_.__field_names__,
        '__init__': __init__,
        '__setattr__': __setattr__,
    }

    return type(
        class_name or 'NamespacedInput',
        (),
        attributes
    )

def input_as_dict(input_):
    if isinstance(input_, dict):
        return input_
    elif hasattr(input_, '__dict__'):
        return input_.__dict__
    else:
        raise ValueError(f'Unsupported input: {input_}')
