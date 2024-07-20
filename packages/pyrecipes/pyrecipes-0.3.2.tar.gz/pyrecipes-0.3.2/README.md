# Pyrecipes

![ci workflow](https://github.com/ChrisA87/pyrecipes/actions/workflows/ci.yml/badge.svg)
![Publish Pyrecipes to PyPI](https://github.com/ChrisA87/pyrecipes/actions/workflows/publish.yml/badge.svg)
![coverage-badge](https://raw.githubusercontent.com/ChrisA87/pyrecipes/aa37d4757dd7ecbc0b1f2ec93eeb55165be12307/coverage.svg)

---

Recipes from [Python Cookbook, Third Edition](https://www.oreilly.com/library/view/python-cookbook-3rd/9781449357337/), by David Beazley and Brian K. Jones. Copyright © 2013 David Beazley and Brian Jones. Published by O'Reilly Media, Inc. Used with permission.

This project implements a simple CLI tool to list, run and view these recipes.

Special thanks to O'Reilly Media, Inc and the Authors for permission to use their recipes.

Check out Author David Beazley's website: https://www.dabeaz.com/

Add this amazing book to your bookshelf [here](https://www.amazon.co.uk/Python-Cookbook-David-Beazley/dp/1449340377/ref=sr_1_1?crid=1OU8UMUB7WGMI&keywords=python+cookbook&qid=1699549493&s=books&sprefix=python+cookbook%2Cstripbooks%2C279&sr=1-1)

[![Python Cookbook](https://raw.githubusercontent.com/ChrisA87/pyrecipes/main/imgs/python-cookbook-cover.jpeg)](https://www.amazon.co.uk/Python-Cookbook-David-Beazley/dp/1449340377/ref=sr_1_1?crid=1OU8UMUB7WGMI&keywords=python+cookbook&qid=1699549493&s=books&sprefix=python+cookbook%2Cstripbooks%2C279&sr=1-1)

---

## Installation

```
pip install pyrecipes
```

---

## Example Usage

### Show recipes help and subcommands
```
recipes
```

### List all chapters
```
recipes chapters
```

### List all recipes
```
recipes ls
```

### List all recipes in a specific chapter
```
recipes ls 1
```

### List all recipes in a specific chapter with a short description
```
recipes ls 1 -d
```

### Show recipe code
```
recipes show 1 3
```

### Run the recipe as a script
```
recipes run 1 3
```

### Search for recipes containing a pattern
RegEx is supported.
```
recipes search 'itertools'
recipes search 'itertools' --color green
recipes search 'event' --ignore-case
recipes search 'functools' -c
recipes search '[a-z]\d[^\s]'
```
