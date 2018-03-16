CHANGELOG
=========
Version 0.9.0
-------------
* Changed function wrappers for correct processing of methods in non-argumented mode.

Version 0.8.0
-------------
* Python 3.3 support is ended. EOL is coming, test was run rarely.
* Move data from setup.cfg to __init__.py and setup.py

Version 0.7.0
-------------
Cythonize python 3, if possible (and gevent present).

Version 0.6.0
-------------
Gevent is supported.

Version 0.5.0
-------------
CI/CD pipelines.
Class decorator without __slots__
Docs.

Version 0.4.1
-------------
Initial documentation.
Fix readme.
Update setup.py from doctedsted get_simple_vars_from_src.

Version 0.4.0
-------------
Class decorator updated to the last version
Added lowercase aliases
Fixed docstrings and type hints
Travis should run pypy and pypy3

Version 0.3.2
-------------
Base class for decorator has been extracted.

Version 0.3.1
-------------
Fix Readme.

Version 0.3.0
-------------
Old famous Threaded is come back.

Version 0.2.0
-------------
Renamed to threaded: more correct due to not process pool support.

Version 0.1.2
-------------
Use requirements.txt.
Prepare for travis.

Version 0.1.2
-------------
Dropped out never worked ProcessPooled: not picklable.
Added unit tests

Version 0.1.1
-------------
Fixed and returned not argumented usage.
Refactored python 3 loop getter.

Version 0.1.0
-------------
Initial version.
