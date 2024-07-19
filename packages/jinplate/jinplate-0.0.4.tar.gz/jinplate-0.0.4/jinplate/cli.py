#!/usr/bin/env python3

import pathlib

import click
import jinja2

from jinplate.plugins.loader import DataLoader


@click.command("jinplate")
@click.option("--jinja-ext", type=str, default=None)
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("datasources", type=str, nargs=-1, required=True)
def jinplate_cli(template_file, datasources, jinja_ext):
    """
    A command line renderer for jinja templates

    TEMPLATE_FILE is the path to a jinja template file to render

    DATASOURCES is a list of URIs to data sources supported by jinplate which contain
    the template variables

    --jinja-ext allows specifying a comma-separated list of import paths containing
    jinja extensions. Example: --jinja-ext jinja2.ext.i18n
    """
    template_path = pathlib.Path(template_file).resolve()
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent),
        extensions=jinja_ext.split(",") if jinja_ext is not None else [],
    )
    template = jenv.get_template(template_path.name)

    dataloader = DataLoader()
    data = {}
    for source in datasources:
        data = {**data, **dataloader.load(source)}

    print(template.render(data))


# pylint: disable=no-value-for-parameter
if __name__ == '__main__':
    jinplate_cli()
