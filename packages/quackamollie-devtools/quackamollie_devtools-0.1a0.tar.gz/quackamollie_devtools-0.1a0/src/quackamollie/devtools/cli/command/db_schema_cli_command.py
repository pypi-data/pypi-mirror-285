# -*- coding: utf-8 -*-
__all__ = ["generate_db_schema"]
__author__ = "QuacktorAI"
__copyright__ = "Copyright 2024, Forge of Absurd Ducks"
__credits__ = ["QuacktorAI"]

import click
import logging
import os

from quackamollie.core import core_version
from quackamollie.core.database import model
from sqlalchemy_schemadisplay import create_uml_graph
from sqlalchemy.orm import class_mapper
from typing import Optional

from quackamollie.devtools import devtools_version
from quackamollie.devtools.defaults import (DEFAULT_SCHEMA_OUTPUT_DIR, DEFAULT_SCHEMA_OUTPUT_PATH,
                                            DEFAULT_SHOW_MULTIPLICITY_ONE, DEFAULT_SHOW_OPERATIONS)

log = logging.getLogger(__name__)


@click.command(name="schema")
@click.help_option('-h', '--help')
@click.version_option(version=click.style(f'devtools_version={devtools_version}', bold=True))
@click.option('-od', '--output-dir', type=click.Path(exists=False, dir_okay=True),
              default=DEFAULT_SCHEMA_OUTPUT_DIR,
              help=f"Directory path where to write the generated schema, default file name is"
                   f" 'quackamollie_schema_v{core_version}.png'")
@click.option('-of', '--output-file', type=click.Path(exists=False, file_okay=True),
              default=DEFAULT_SCHEMA_OUTPUT_PATH, help='File path where to write the generated schema')
@click.option('--show-multiplicity-one/--no-show-multiplicity-one', type=bool,
              default=DEFAULT_SHOW_MULTIPLICITY_ONE, show_default=True,
              help="Show the '1's on arrows in the database schema, or not")
@click.option('--show-operations/--no-show-operations', type=bool,
              default=DEFAULT_SHOW_OPERATIONS, show_default=True, help="Show operations associated to SQLAlchemy model")
@click.pass_context
def generate_db_schema(ctx, output_dir: click.Path, output_file: Optional[click.Path], show_multiplicity_one: bool,
                       show_operations: bool):
    """ Generate the schema of the current database as defined by the package `quackamollie-core`.\f

        :param ctx: Click context to pass between commands of quackamollie
        :type ctx: click.Context

        :param output_dir: Directory path where to write the generated schema, default file name is in the form
                           'quackamollie_schema_v{core_version}.png'
        :type output_dir: click.Path

        :param output_file: File path where to write the generated schema
        :type output_file: Optional[click.Path]

        :param show_multiplicity_one: Show the '1's on arrows in the database schema, or not
        :type show_multiplicity_one: bool

        :param show_operations: Show operations associated to SQLAlchemy model
        :type show_operations: bool
    """
    if output_file is None:
        os.makedirs(output_dir, exist_ok=True)
        schema_name = f"quackamollie_schema_v{core_version}.png"
        output_path = os.path.join(output_dir, schema_name)
    else:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        output_path = output_file

    # Log configuration for debug, with username partially hidden and password fully hidden
    log.debug(f"Database input settings are :"
              f"\n\toutput_dir: '{output_dir}' [from {ctx.get_parameter_source('output_dir').name}]"
              f"\n\toutput_file: '{output_file}' [from {ctx.get_parameter_source('output_file').name}]"
              f"\n\tshow_multiplicity_one: {show_multiplicity_one}"
              f" [from {ctx.get_parameter_source('show_multiplicity_one').name}]"
              f"\n\tshow_operations: {show_operations} [from {ctx.get_parameter_source('show_operations').name}]")

    log.info(f"Generating schema in '{output_path}'")
    graph = create_uml_graph(
        [class_mapper(x) for x in map(model.__dict__.get, model.__all__)],
        show_operations=show_operations,
        show_multiplicity_one=show_multiplicity_one
    )
    graph.set('scale', 2)
    graph.write_png(output_path)
