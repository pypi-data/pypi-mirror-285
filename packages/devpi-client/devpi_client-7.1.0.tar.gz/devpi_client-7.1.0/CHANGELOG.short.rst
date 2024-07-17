

=========
Changelog
=========




.. towncrier release notes start

7.1.0 (2024-07-17)
==================

Features
--------

- Support upload command configuration from ``pyproject.toml`` in ``[tool.devpi.upload]`` section.

- The ``--fallback-ini`` option of ``devpi test`` can now be relative to the package root. This allows using ``pyproject.toml`` or similar instead of ``tox.ini``.

- Add ``sdist`` and ``wheel`` options for ``setup.cfg``.

- Add detection of tox configs in pyproject.toml and setup.cfg for ``devpi test``.



Bug Fixes
---------

- In ``setup.cfg`` any value for upload settings was interpreted as True, now a warning is printed if it looks like False was meant and how to fix that. For backward compatibility the behavior wasn't changed.



7.0.3 (2024-04-20)
==================

Bug Fixes
---------

- Require ``build>=0.7.0`` to prevent import error with older versions.

- Fix check for extracted path when testing packages related to PEP 625 changes in setuptools.

- If the server returns a message on toxresult upload, then print it as a warning.

- Provide proper error message if the API request for ``devpi use`` fails.

- Fix #1011: change HTTP status codes >=400 to use self.fatal instead of raw SystemExit, protect 403 and 404 errors from SystemExit



7.0.2 (2023-10-19)
==================

Bug Fixes
---------

- Fix #992: Fix error added in 6.0.4 when old authentication data from before 6.x exists.


7.0.1 (2023-10-15)
==================

Bug Fixes
---------

- Fix #1005: use ``shutil.move`` instead of ``Path.rename`` to move distribution after building to prevent cross-device link errors.

- Fix #1008: pass ``--no-isolation`` option to ``build`` when determining name/version for documentation.


7.0.0 (2023-10-11)
==================

Deprecations and Removals
-------------------------

- Use ``build`` instead of deprecated ``pep517`` package.

- Removed dependency on py package.
  Plugins which expect py.path.local need to be adjusted to work with pathlib.Path.

- Dropped support for Python <= 3.6.



Other Changes
-------------

- .. note::
      Potentially breaking fix #939: devpi-common 4.x now has custom legacy version parsing (non PEP 440) after packaging >= 22.0 removed support. This might affect commands like ``devpi remove`` if used with version ranges. Legacy versions were always and still are sorted before PEP 440 compliant versions, but the ordering between legacy versions might be affected.

- Fix #946: output ``name==version`` instead of ``name-version`` for ``devpi list -v``.

