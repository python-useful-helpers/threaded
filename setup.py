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

from __future__ import print_function

import ast
import collections
from distutils.command import build_ext
import distutils.errors
import os.path
import shutil
import sys

try:
    from Cython.Build import cythonize
    import gevent
except ImportError:
    gevent = cythonize = None

import setuptools

PY3 = sys.version_info[:2] > (2, 7)

with open(
    os.path.join(
        os.path.dirname(__file__),
        'threaded', '__init__.py'
    )
) as f:
    source = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('README.rst',) as f:
    long_description = f.read()


def _extension(modpath):
    """Make setuptools.Extension."""
    return setuptools.Extension(modpath, [modpath.replace('.', '/') + '.py'])


requires_optimization = [
    _extension('threaded._class_decorator'),
    _extension('threaded._base_threaded'),
    _extension('threaded._py3_helpers'),
    _extension('threaded._threaded3'),
    _extension('threaded._base_gthreadpooled'),
    _extension('threaded._gthreadpooled3'),
]

if 'win32' != sys.platform:
    requires_optimization.append(
        _extension('threaded.__init__')
    )

ext_modules = cythonize(
    requires_optimization,
    compiler_directives=dict(
        always_allow_keywords=True,
        binding=True,
        embedsignature=True,
        overflowcheck=True,
        language_level=3,
    )
) if cythonize is not None and PY3 else []


class BuildFailed(Exception):
    """For install clear scripts."""
    pass


class AllowFailRepair(build_ext.build_ext):
    """This class allows C extension building to fail and repairs init."""

    def run(self):
        """Run."""
        try:
            build_ext.build_ext.run(self)

            # Copy __init__.py back to repair package.
            build_dir = os.path.abspath(self.build_lib)
            root_dir = os.path.abspath(os.path.join(__file__, '..'))
            target_dir = build_dir if not self.inplace else root_dir

            src_file = os.path.join('threaded', '__init__.py')

            src = os.path.join(root_dir, src_file)
            dst = os.path.join(target_dir, src_file)

            if src != dst:
                shutil.copyfile(src, dst)
        except (
            distutils.errors.DistutilsPlatformError,
            globals()['__builtins__'].get('FileNotFoundError', OSError)
        ):
            raise BuildFailed()

    def build_extension(self, ext):
        """build_extension."""
        try:
            build_ext.build_ext.build_extension(self, ext)
        except (
            distutils.errors.CCompilerError,
            distutils.errors.DistutilsExecError,
            distutils.errors.DistutilsPlatformError,
            ValueError
        ):
            raise BuildFailed()


# noinspection PyUnresolvedReferences
def get_simple_vars_from_src(src):
    """Get simple (string/number/boolean and None) assigned values from source.

    :param src: Source code
    :type src: str
    :returns: OrderedDict with keys, values = variable names, values
    :rtype: typing.Dict[
                str,
                typing.Union[
                    str, bytes,
                    int, float, complex,
                    list, set, dict, tuple,
                    None,
                ]
            ]

    Limitations: Only defined from scratch variables.
    Not supported by design:
        * Imports
        * Executable code, including string formatting and comprehensions.

    Examples:

    >>> string_sample = "a = '1'"
    >>> get_simple_vars_from_src(string_sample)
    OrderedDict([('a', '1')])

    >>> int_sample = "b = 1"
    >>> get_simple_vars_from_src(int_sample)
    OrderedDict([('b', 1)])

    >>> list_sample = "c = [u'1', b'1', 1, 1.0, 1j, None]"
    >>> result = get_simple_vars_from_src(list_sample)
    >>> result == collections.OrderedDict(
    ...     [('c', [u'1', b'1', 1, 1.0, 1j, None])]
    ... )
    True

    >>> iterable_sample = "d = ([1], {1: 1}, {1})"
    >>> get_simple_vars_from_src(iterable_sample)
    OrderedDict([('d', ([1], {1: 1}, {1}))])

    >>> multiple_assign = "e = f = g = 1"
    >>> get_simple_vars_from_src(multiple_assign)
    OrderedDict([('e', 1), ('f', 1), ('g', 1)])
    """
    ast_data = (
        ast.Str, ast.Num,
        ast.List, ast.Set, ast.Dict, ast.Tuple
    )
    if PY3:
        ast_data += (ast.Bytes, ast.NameConstant,)

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

classifiers = [
    'Development Status :: 4 - Beta',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',

    'License :: OSI Approved :: Apache Software License',

    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',

    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
]

keywords = [
    'pooling',
    'multithreading',
    'threading',
    'asyncio',
    'gevent',
    'development',
]

setup_args = dict(
    name='threaded',
    author=variables['__author__'],
    author_email=variables['__author_email__'],
    url=variables['__url__'],
    version=variables['__version__'],
    license=variables['__license__'],
    description=variables['__description__'],
    long_description=long_description,
    classifiers=classifiers,
    keywords=keywords,
    extras_require={
        ':python_version == "2.7"': [
            'futures>=3.1',
        ],
        'gevent': [
            'gevent >= 1.2'
        ],
    },
    install_requires=required,
)
if PY3 and cythonize is not None:
    setup_args['ext_modules'] = ext_modules
    setup_args['cmdclass'] = dict(build_ext=AllowFailRepair)

try:
    setuptools.setup(**setup_args)
except BuildFailed:
    print(
        '*' * 80 + '\n'
        '* Build Failed!\n'
        '* Use clear scripts version.\n'
        '*' * 80 + '\n'
    )
    del setup_args['ext_modules']
    del setup_args['cmdclass']
    setuptools.setup(**setup_args)
