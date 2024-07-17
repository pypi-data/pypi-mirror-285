==========================
Quackamollie CLI Dev Tools
==========================

:Name: Quackamollie CLI Dev Tools
:Package name: quackamollie-devtools
:Description: Development tools for the command line interface (CLI) of Quackamollie Telegram chat bot
:Version: 0.1a0
:Main page: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools
:PyPI package: https://pypi.org/project/quackamollie-devtools
:Documentation: https://devtools-forge-of-absurd-ducks-quackamollie-lib--0cee136bdd04d9.gitlab.io
:Build Status:
    :Master: |master_pipeline_badge| |master_coverage_badge|
    :Dev: |dev_pipeline_badge| |dev_coverage_badge|

.. |master_pipeline_badge| image:: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools/badges/master/pipeline.svg
   :target: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools/commits/master
   :alt: Master pipeline status
.. |master_coverage_badge| image:: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools/badges/master/coverage.svg
   :target: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools/commits/master
   :alt: Master coverage status

.. |dev_pipeline_badge| image:: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools/badges/dev/pipeline.svg
   :target: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools/commits/dev
   :alt: Dev pipeline status
.. |dev_coverage_badge| image:: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools/badges/dev/coverage.svg
   :target: https://gitlab.com/forge_of_absurd_ducks/quackamollie/lib/cli/quackamollie_devtools/commits/dev
   :alt: Dev coverage status

----

Project description
===================
Quackamollie is a Telegram chat bot in Python using the library `aiogram` to serve LLM models running locally using Ollama.
Quackamollie implements also a command line interface `quackamollie`.

This package is an extension of the command line interface `quackamollie` with common tools for development, for the Quackamollie project.
It contains:

 - a click command `generate_db_schema` registered through entrypoint for use with `quackamollie db schema`

Learn more about Quackamollie on the project main page : https://gitlab.com/forge_of_absurd_ducks/quackamollie/quackamollie


Requirements
============

System requirements
-------------------
Ensure you have `graphviz` installed on your system.

- For instance on Debian systems

.. code-block:: bash

  apt update
  apt install graphviz

Virtual environment
-------------------
- Setup a virtual environment in python 3.10

.. code-block:: bash

   make venv
   # or
   python3 -m venv venv

- Activate the environment

.. code-block:: bash

   source venv/bin/activate

- If you want to deactivate the environment

.. code-block:: bash

   deactivate


Tests
=====

Tests requirements
------------------
- Install test requirements

.. code-block:: bash

   make devtools
   # or
   pip install tox

Run pytest
----------
- Run the tests

.. code-block:: bash

   tox

Run lint
--------
- Run the lintage

.. code-block:: bash

   tox -e lint


Documentation
=============

- To auto-generate the documentation configuration

.. code-block:: bash

   tox -e gendocs

- To generate the documentation in Html

.. code-block:: bash

   tox -e docs

- An automatically generated version of this project documentation can be found at `here <https://devtools-forge-of-absurd-ducks-quackamollie-lib--0cee136bdd04d9.gitlab.io>`_


Install
=======
- Install the application from sources

.. code-block:: bash

   make install
   # or
   pip install .

- Or install it from distribution

.. code-block:: bash

   pip install dist/quackamollie-devtools-0.1a0.tar.gz

- Or install it from wheel

.. code-block:: bash

   pip install dist/quackamollie-devtools-0.1a0.whl

- Or install it from PyPi repository

.. code-block:: bash

   pip install quackamollie-devtools  # latest
   # or
   pip install "quackamollie-devtools==0.1a0"


Generating a schema
===================
`quackamollie-devtools` package is automatically discovered, through entrypoints, by the command tool line named `quackamollie`.
Therefore, once installed, you should automatically be able to call `quackamollie db schema -h` to see the help of this command.

You can generate a schema with:

.. code-block:: bash

   # Specify only the directory to generate a schema, here at path 'schemas/quackamollie_schema_v{core_version}.png'
   quackamollie db schema -od schemas

   # Specify a file name to generate a PNG schema with a specific name
   quackamollie db schema -of schemas/quackamollie_schema_latest.png


Authors
=======

- **QuacktorAI** - *Initial work* - `quacktorai <https://gitlab.com/quacktorai>`_


Contributing
============
Currently, contributions are frozen because the project is still in very early stages and I have yet to push the whole architecture.

For more details on the general contributing mindset of this project, please refer to `CONTRIBUTING.md <CONTRIBUTING.md>`_.


Credits
=======

Section in writing, sorry for the inconvenience.
