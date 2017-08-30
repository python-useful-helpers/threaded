#    Copyright 2017 Alexey Stepanov aka penguinolog

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Wrap in ProcessPool/ThreadPool executors or asyncio.Task."""

import ast
import collections
import os.path
import sys

import setuptools

PY3 = sys.version_info[:2] > (2, 7)
PY34 = sys.version_info[:2] > (3, 3)

with open(
    os.path.join(
        os.path.dirname(__file__),
        'threaded', '__init__.py'
    )
) as f:
    source = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()


# noinspection PyUnresolvedReferences
def get_simple_vars_from_src(src):
    """Get simple (string/number/boolean and None) assigned values from source.

    :param src: Source code
    :type src: str
    :rtype: collections.OrderedDict
    """
    ast_data = (
        ast.Str, ast.Num,
        ast.List, ast.Set, ast.Dict, ast.Tuple
    )
    if PY3:
        ast_data += (ast.Bytes,)
    if PY34:
        ast_data += (ast.NameConstant,)

    tree = ast.parse(src)

    result = collections.OrderedDict()

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign):  # We parse assigns only
            continue
        try:
            if isinstance(node.value, ast_data):
                value = ast.literal_eval(node.value)
            elif isinstance(  # NameConstant in python < 3.4
                node.value, ast.Name
            ) and isinstance(
                node.value.ctx, ast.Load  # Read constant
            ):
                value = ast.literal_eval(node.value)
            else:
                continue
        except ValueError:
            continue
        for tgt in node.targets:
            if isinstance(
                tgt, ast.Name
            ) and isinstance(
                tgt.ctx, ast.Store
            ):
                result[tgt.id] = value
    return result


variables = get_simple_vars_from_src(source)

setuptools.setup(
    name='threaded',
    version=variables['__version__'],
    extras_require={
        ':python_version == "2.7"': [
            'futures>=3.1',
        ],
        ':python_version == "3.3"': [
            'asyncio>=3.4',
        ],
    },
    install_requires=required,
)
