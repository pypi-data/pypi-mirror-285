import sys
import click
from pyrecipes import TEMPLATE_DIR

templates = {
    "gitignore": TEMPLATE_DIR / ".gitignore",
    "pyproject": TEMPLATE_DIR / "pyproject.toml",
}


@click.command()
@click.argument(
    "name", required=True, default=None, type=click.Choice(templates.keys())
)
@click.option("-o", "--output", type=click.File(mode="w+"), default=sys.stdout)
def template(name, output):
    """Generates commonly used template files for Python projects."""
    output.write(templates.get(name).read_text())
