pytest plugin for efficiently checking PEP8 compliance 
======================================================

.. image:: https://img.shields.io/pypi/v/pytest-flake8.svg
    :target: https://pypi.python.org/pypi/pytest-flake8

.. image:: https://img.shields.io/pypi/pyversions/pytest-flake8.svg
    :target: https://pypi.python.org/pypi/pytest-flake8

.. image:: https://img.shields.io/pypi/implementation/pytest-flake8.svg
    :target: https://pypi.python.org/pypi/pytest-flake8

.. image:: https://img.shields.io/pypi/status/pytest-flake8.svg
    :target: https://pypi.python.org/pypi/pytest-flake8

.. image:: https://img.shields.io/github/issues/coherent-oss/pytest-flake8.svg
    :target: https://github.com/coherent-oss/pytest-flake8/issues

.. image:: https://img.shields.io/github/issues-pr/coherent-oss/pytest-flake8.svg
    :target: https://github.com/coherent-oss/pytest-flake8/pulls

Usage
-----

Install it into a test environment, then run tests with the option::

    pytest --flake8

Every file ending in ``.py`` will be discovered and checked with
flake8.

.. note::

    If optional flake8 plugins are installed, those will
    be used automatically. No provisions have been made for
    configuring these via `pytest`_.

.. warning::

    Running flake8 tests on your project is likely to cause a number 
    of issues. The plugin allows one to configure on a per-project and
    per-file basis which errors or warnings to ignore, see
    flake8-ignore_.

.. _flake8-ignore:

Configuring Flake8
------------------

See the Flake8
`docs on configuring <https://flake8.pycqa.org/en/latest/user/configuration.html>`_.

FAQs
-----

All the Flake8 tests are skipping!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By design, results are cached and only changed files are checked.

Run with ``pytest --cache-clear --flake8`` to bypass.

Notes
-----

For more info on `pytest`_ see http://pytest.org

The code is partially based on Ronny Pfannschmidt's `pytest-codecheckers`_ plugin.

.. _`pytest`: http://pytest.org
.. _`flake8`: https://pypi.python.org/pypi/flake8
.. _`pycodestyle`: https://pypi.python.org/pypi/pycodestyle
.. _`pytest-codecheckers`: https://pypi.python.org/pypi/pytest-codecheckers
