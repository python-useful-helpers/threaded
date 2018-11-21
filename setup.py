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
from distutils.command import build_ext
import distutils.errors
import os.path
import shutil
import sys
try:
    import typing
except ImportError:
    typing = None

import setuptools

try:
    # noinspection PyPackageRequirements
    from Cython.Build import cythonize

except ImportError:
    cythonize = None


with open(os.path.join(os.path.dirname(__file__), "threaded", "__init__.py")) as f:
    source = f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

with open("README.rst") as f:
    long_description = f.read()


def _extension(modpath: str) -> setuptools.Extension:
    """Make setuptools.Extension."""
    return setuptools.Extension(modpath, [modpath.replace(".", "/") + ".py"])


requires_optimization = [
    setuptools.Extension("threaded.class_decorator", ["threaded/class_decorator.pyx"]),
    _extension("threaded._base_threaded"),
    setuptools.Extension("threaded._asynciotask", ["threaded/_asynciotask.pyx"]),
    setuptools.Extension("threaded._threaded", ["threaded/_threaded.pyx"]),
    _extension("threaded._threadpooled"),
]

if "win32" != sys.platform:
    requires_optimization.append(_extension("threaded.__init__"))

# noinspection PyCallingNonCallable
ext_modules = (
    cythonize(
        requires_optimization,
        compiler_directives=dict(
            always_allow_keywords=True, binding=True, embedsignature=True, overflowcheck=True, language_level=3
        ),
    )
    if cythonize is not None
    else []
)


class BuildFailed(Exception):
    """For install clear scripts."""

    pass


class AllowFailRepair(build_ext.build_ext):
    """This class allows C extension building to fail and repairs init."""

    def run(self):
        """Run.

        :raises BuildFailed: cythonize impossible
        """
        try:
            build_ext.build_ext.run(self)

            # Copy __init__.py back to repair package.
            build_dir = os.path.abspath(self.build_lib)
            root_dir = os.path.abspath(os.path.join(__file__, ".."))
            target_dir = build_dir if not self.inplace else root_dir

            src_file = os.path.join("threaded", "__init__.py")

            src = os.path.join(root_dir, src_file)
            dst = os.path.join(target_dir, src_file)

            if src != dst:
                shutil.copyfile(src, dst)
        except (
            distutils.errors.DistutilsPlatformError,
            getattr(globals()["__builtins__"], "FileNotFoundError", OSError),
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
            ValueError,
        ):
            raise BuildFailed()


# noinspection PyUnresolvedReferences
def get_simple_vars_from_src(
    src: str
) -> "typing.Dict[str, typing.Union[str, bytes, int, float, complex, list, set, dict, tuple, None]]":
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
    ast_data = (ast.Str, ast.Num, ast.List, ast.Set, ast.Dict, ast.Tuple, ast.Bytes, ast.NameConstant)

    tree = ast.parse(src)

    result = collections.OrderedDict()

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign):  # We parse assigns only
            continue
        try:
            if isinstance(node.value, ast_data):
                value = ast.literal_eval(node.value)
            elif isinstance(node.value, ast.Name) and isinstance(  # NameConstant in python < 3.4
                node.value.ctx, ast.Load  # Read constant
            ):
                value = ast.literal_eval(node.value)
            else:
                continue
        except ValueError:
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and isinstance(tgt.ctx, ast.Store):
                result[tgt.id] = value
    return result


variables = get_simple_vars_from_src(source)

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
]

keywords = ["pooling", "multithreading", "threading", "asyncio", "development"]

setup_args = dict(
    name="threaded",
    author=variables["__author__"],
    author_email=variables["__author_email__"],
    maintainer=", ".join(
        "{name} <{email}>".format(name=name, email=email) for name, email in variables["__maintainers__"].items()
    ),
    url=variables["__url__"],
    license=variables["__license__"],
    description=variables["__description__"],
    long_description=long_description,
    classifiers=classifiers,
    keywords=keywords,
    python_requires=">=3.4",
    # While setuptools cannot deal with pre-installed incompatible versions,
    # setting a lower bound is not harmful - it makes error messages cleaner. DO
    # NOT set an upper bound on setuptools, as that will lead to uninstallable
    # situations as progressive releases of projects are done.
    # Blacklist setuptools 34.0.0-34.3.2 due to https://github.com/pypa/setuptools/issues/951
    # Blacklist setuptools 36.2.0 due to https://github.com/pypa/setuptools/issues/1086
    setup_requires=[
        "setuptools >= 21.0.0,!=24.0.0,"
        "!=34.0.0,!=34.0.1,!=34.0.2,!=34.0.3,!=34.1.0,!=34.1.1,!=34.2.0,!=34.3.0,!=34.3.1,!=34.3.2,"
        "!=36.2.0",
        "setuptools_scm",
    ],
    use_scm_version=True,
    install_requires=required,
    package_data={"threaded": ["py.typed"]},
)
if cythonize is not None:
    setup_args["ext_modules"] = ext_modules
    setup_args["cmdclass"] = dict(build_ext=AllowFailRepair)

try:
    setuptools.setup(**setup_args)
except BuildFailed:
    print("*" * 80 + "\n" "* Build Failed!\n" "* Use clear scripts version.\n" "*" * 80 + "\n")
    del setup_args["ext_modules"]
    del setup_args["cmdclass"]
    setuptools.setup(**setup_args)
