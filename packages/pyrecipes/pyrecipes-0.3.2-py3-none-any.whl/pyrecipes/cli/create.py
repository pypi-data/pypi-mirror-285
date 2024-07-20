import click
from pyrecipes import COOKBOOK_DIR, TEMPLATE_DIR


def create_recipe_dir_name(number, name):
    return (f"{number:0>2} {name}").lower().replace(" ", "_")


@click.command(hidden=True)
@click.argument("chapter", type=int)
@click.argument("number", type=int)
@click.argument("name", type=str)
def create(chapter, number, name):
    """Create a new recipe"""
    chapter_dir = next(COOKBOOK_DIR.glob(f"{chapter:0>2}_*"))
    recipe_dir = chapter_dir / create_recipe_dir_name(number, name)

    click.echo(f"creating {recipe_dir}")
    recipe_dir.mkdir()
    template = (TEMPLATE_DIR / "recipe.py").read_text()
    (recipe_dir / "example.py").write_text(template)
