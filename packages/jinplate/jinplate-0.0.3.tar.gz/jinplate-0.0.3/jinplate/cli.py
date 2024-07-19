#!/usr/bin/env python3

import pathlib

import click
import jinja2

from jinplate.plugins.loader import DataLoader


@click.command("jinplate")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("datasource", type=str)
@click.option("--file-type", type=str, default=None)
def jinplate_cli(template_file, datasource, file_type):
    """
    A command line renderer for jinja templates

    TEMPLATE_FILE is the path to a jinja template file to render

    DATASOURCE is the URI of a datasource supported by jinplate that contains the
    template variables
    """
    template_path = pathlib.Path(template_file).resolve()
    jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path.parent))
    template = jenv.get_template(template_path.name)

    dataloader = DataLoader()
    data = dataloader.load(datasource, file_type=file_type)

    print(template.render(data))


# pylint: disable=no-value-for-parameter
if __name__ == '__main__':
    jinplate_cli()
