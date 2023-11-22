#    Copyright 2017 - 2020 Alexey Stepanov aka penguinolog

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

from __future__ import annotations

# Standard Library
import ast
import distutils.errors
import os.path
import shutil
import sys
from distutils.command import build_ext

# External Dependencies
import setuptools

try:
    # noinspection PyPackageRequirements
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

PACKAGE_NAME = "threaded"

with open(  # noqa: PTH123,FURB101,RUF100
    os.path.join(os.path.dirname(__file__), PACKAGE_NAME, "__init__.py"),  # noqa: PTH118, PTH120
    encoding="utf-8",
) as f:
    SOURCE = f.read()


# noinspection PyCallingNonCallable
if cythonize is not None:
    REQUIRES_OPTIMIZATION = [
        setuptools.Extension("threaded.class_decorator", ["threaded/class_decorator.pyx"]),
        setuptools.Extension("threaded._base_threaded", ["threaded/_base_threaded.py"]),
        setuptools.Extension("threaded._asynciotask", ["threaded/_asynciotask.pyx"]),
        setuptools.Extension("threaded._threaded", ["threaded/_threaded.pyx"]),
        setuptools.Extension("threaded._threadpooled", ["threaded/_threadpooled.py"]),
    ]
    if sys.platform != "win32":
        # NOTE: Do not make pyx/pxd - it kills windows
        REQUIRES_OPTIMIZATION.append(
            setuptools.Extension("threaded.__init__", ["threaded/__init__.py"]),
        )

    INTERFACES = ["class_decorator.pxd", "_asynciotask.pxd", "_threaded.pxd"]

    EXT_MODULES = cythonize(
        module_list=REQUIRES_OPTIMIZATION,
        compiler_directives=dict(  # noqa: C408
            always_allow_keywords=True,
            binding=True,
            embedsignature=True,
            overflowcheck=True,
            language_level=3,
        ),
    )
else:
    REQUIRES_OPTIMIZATION = []
    INTERFACES = []
    EXT_MODULES = []


class BuildFailed(Exception):
    """For install clear scripts."""


class AllowFailRepair(build_ext.build_ext):
    """This class allows C extension building to fail and repairs init."""

    def run(self):
        """Run.

        :raises BuildFailed: Build is failed and clean python code should be used.
        """
        try:
            build_ext.build_ext.run(self)

            # Copy __init__.py back to repair package.
            build_dir = os.path.abspath(self.build_lib)  # noqa: PTH100
            root_dir = os.path.abspath(os.path.join(__file__, ".."))  # noqa: PTH100,PTH118
            target_dir = build_dir if not self.inplace else root_dir

            src_file = os.path.join(PACKAGE_NAME, "__init__.py")  # noqa: PTH118

            src = os.path.join(root_dir, src_file)  # noqa: PTH118
            dst = os.path.join(target_dir, src_file)  # noqa: PTH118

            if src != dst:
                shutil.copyfile(src, dst)
        except (
            distutils.errors.DistutilsPlatformError,
            FileNotFoundError,
        ) as exc:
            raise BuildFailed() from exc

    def build_extension(self, ext):
        """build_extension.

        :raises BuildFailed: Build is failed and clean python code should be used.
        """
        try:
            build_ext.build_ext.build_extension(self, ext)
        except (
            distutils.errors.CCompilerError,
            distutils.errors.DistutilsExecError,
            distutils.errors.DistutilsPlatformError,
            ValueError,
        ) as exc:
            raise BuildFailed() from exc


# noinspection PyUnresolvedReferences
def get_simple_vars_from_src(
    src: str,
) -> dict[str, str | bytes | int | float | complex | list | set | dict | tuple | None | bool | Ellipsis]:
    """Get simple (string/number/boolean and None) assigned values from source.

    :param src: Source code
    :type src: str
    :return: OrderedDict with keys, values = variable names, values
    :rtype: dict[
                str,
                Union[
                    str, bytes,
                    int, float, complex,
                    list, set, dict, tuple,
                    None, bool, Ellipsis
                ]
            ]

    Limitations: Only defined from scratch variables.
    Not supported by design:
        * Imports
        * Executable code, including string formatting and comprehensions.

    Examples:
    >>> string_sample = "a = '1'"
    >>> get_simple_vars_from_src(string_sample)
    {'a': '1'}

    >>> int_sample = "b = 1"
    >>> get_simple_vars_from_src(int_sample)
    {'b': 1}

    >>> list_sample = "c = [u'1', b'1', 1, 1.0, 1j, None]"
    >>> result = get_simple_vars_from_src(list_sample)
    >>> result == {'c': [u'1', b'1', 1, 1.0, 1j, None]}
    True

    >>> iterable_sample = "d = ([1], {1: 1}, {1})"
    >>> get_simple_vars_from_src(iterable_sample)
    {'d': ([1], {1: 1}, {1})}

    >>> multiple_assign = "e = f = g = 1"
    >>> get_simple_vars_from_src(multiple_assign)
    {'e': 1, 'f': 1, 'g': 1}
    """
    tree = ast.parse(src)

    result = {}

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign) or not isinstance(
            node.value, (ast.Constant, ast.List, ast.Set, ast.Dict, ast.Tuple)
        ):
            continue
        try:
            value = ast.literal_eval(node.value)
        except ValueError:
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and isinstance(tgt.ctx, ast.Store):
                result[tgt.id] = value
    return result


VARIABLES = get_simple_vars_from_src(SOURCE)

SETUP_ARGS = dict(  # noqa: C408
    name=PACKAGE_NAME,
    url=VARIABLES["__url__"],
    python_requires=">=3.8.0",
    # While setuptools cannot deal with pre-installed incompatible versions,
    # setting a lower bound is not harmful - it makes error messages cleaner. DO
    # NOT set an upper bound on setuptools, as that will lead to uninstallable
    # situations as progressive releases of projects are done.
    # Blacklist setuptools 34.0.0-34.3.2 due to https://github.com/pypa/setuptools/issues/951
    # Blacklist setuptools 36.2.0 due to https://github.com/pypa/setuptools/issues/1086
    setup_requires=[
        "setuptools >= 61.0.0",
        "setuptools_scm[toml]>=6.2",
        "wheel",
    ],
    package_data={PACKAGE_NAME: [*INTERFACES, "py.typed"]},
)
if cythonize is not None:
    SETUP_ARGS["ext_modules"] = EXT_MODULES
    SETUP_ARGS["cmdclass"] = {"build_ext": AllowFailRepair}

try:
    setuptools.setup(**SETUP_ARGS)
except BuildFailed:
    print("*" * 80 + "\n* Build Failed!\n* Use clear scripts version.\n" + "*" * 80 + "\n")
    del SETUP_ARGS["ext_modules"]
    del SETUP_ARGS["cmdclass"]
    SETUP_ARGS["package_data"][PACKAGE_NAME] = ["py.typed"]
    setuptools.setup(**SETUP_ARGS)
