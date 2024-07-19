Python Goja ECMAScript 5.1 runtime
########################################################

.. image:: https://github.com/DmitriyMakeev/goja-py/actions/workflows/build.yml/badge.svg?branch=main
  :alt: Build status

``goja-py`` a library that allows you to use the Goja ECMAScript 5.1 (JavaScript) runtime with Python.

.. code-block:: python

    from goja_py import execute

    assert execute('1 + 1;') == 2

Module tested on Python versions from 3.10 to 3.12.


TODO
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

 - pass ``console.log()`` to ``logging.log()``
 - convert native types from JavaScript to Python
 - error handling
