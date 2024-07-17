# -*- coding: utf-8 -*-
__author__ = "QuacktorAI"
__copyright__ = "Copyright 2024, Forge of Absurd Ducks"
__credits__ = ["QuacktorAI"]

import os
import filecmp

from click.testing import CliRunner, Result
from quackamollie.core import core_version
from quackamollie.core.quackamollie import quackamollie

from quackamollie.devtools import devtools_version


def test_generate_db_schema_devtools_version_displays_library_version():
    """ Test `quackamollie db schema --version` option

        Arrange/Act: Run the `quackamollie db schema --version` option.
        Assert: The output matches the devtools library version.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(quackamollie, ['db', 'schema', '--version'])
    assert devtools_version in result.output.strip(), 'Version number should match devtools library version.'


def test_generate_db_schema_help():
    """ Testing schema command integration by calling `quackamollie db schema -h/--help`

        Arrange/Act: Run the help of the command `schema` to verify its import.
        Assert: The output contains the command description
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(quackamollie, ['db', 'schema', '-h'])
    print(f"result.output.strip()={result.output.strip()}")
    assert "Generate the schema of the current database as defined by the package" in result.output.strip(), \
        "Command docstring should be displayed."


def test_generate_db_schema_dir_gen():
    """ Testing schema command integration by calling `quackamollie db schema -od tests/output`

        Arrange/Act: Run the generation of the schema with default file name
        Assert: The output is created at expected path, and it matches the latest version in the 'schemas' directory
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(quackamollie, ['-vvvv', 'db', 'schema', '-od', 'tests/output'])
    fp_generated_schema = f"tests/output/quackamollie_schema_v{core_version}.png"
    fp_reference_schema = "schemas/quackamollie_schema_latest.png"
    print(f"fp_generated_schema='{fp_generated_schema}'")
    print(f"fp_reference_schema='{fp_reference_schema}'")
    print(f"result.output.strip()={result.output.strip()}")
    print(f"files in 'tests/config':\n{os.listdir('tests/output')}")
    assert os.path.isfile(fp_generated_schema), f"A schema should have been generated at '{fp_generated_schema}'"
    assert filecmp.cmp(fp_generated_schema, fp_reference_schema), \
        f"Generated schema differs from the reference schema in '{fp_reference_schema}'."


def test_generate_db_schema_file_gen():
    """ Testing schema command integration by calling `quackamollie db schema -of tests/output/test_schema.png`

        Arrange/Act: Run the generation of the schema with specific file name
        Assert: The output is created at expected path, and it matches the latest version in the 'schemas' directory
    """
    runner: CliRunner = CliRunner()
    fp_generated_schema = "tests/output/test_schema.png"
    result: Result = runner.invoke(quackamollie, ['-vvvv', 'db', 'schema', '-of', fp_generated_schema])
    fp_reference_schema = "schemas/quackamollie_schema_latest.png"
    print(f"fp_generated_schema='{fp_generated_schema}'")
    print(f"fp_reference_schema='{fp_reference_schema}'")
    print(f"result.output.strip()={result.output.strip()}")
    print(f"files in 'tests/config':\n{os.listdir('tests/output')}")
    assert os.path.isfile(fp_generated_schema), f"A schema should have been generated at '{fp_generated_schema}'"
    assert filecmp.cmp(fp_generated_schema, fp_reference_schema), \
        f"Generated schema differs from the reference schema in '{fp_reference_schema}'."
