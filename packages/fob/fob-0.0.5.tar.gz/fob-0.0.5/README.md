[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Worfklow](https://github.com/andrewyates/fob/workflows/pytest/badge.svg)](https://github.com/andrewyates/fob/actions)
[![PyPI version fury.io](https://badge.fury.io/py/fob.svg)](https://pypi.python.org/pypi/fob/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 
# fob
*fob* is a library for building configurable, repeatable experiments. It comes with a `fob` command for running and inspecting experiment pipelines, which are built from configurable *ingredients*.

## Ingredient
An ingredient is the basic building block of a pipeline. Ingredients are configured using their `__init__`method, which allows unified Python and CLI APIs. They need to:

- Subclass the `Ingredient`class, which allows the ingredient to be recognized (and provides many convenience methods) 
- Decorate their `__init__` function with `@configurable`, which makes the arguments passed to `__init__` accessible from the `self.cfg` dict. This allows the arguments to be configured from the CLI and tracked for artifact provenance
- Decorate select methods with `@cacheable`, which saves the method's output based on (1) the method's arguments and (2) the configuration in `self.cfg`. When possible, decorated methods load output from disk rather than recomputing it. The `@cacheable` decorator takes an output type as an argument, such as `@cacheable(NumpyOutput)`. Other valid types include `PathOutput`, `PickleOutput`, `StringOutput`, etc.

## Command
The `fob` command can run arbitrary methods within a pipeline. It uses the syntax:
```
fob <class> [method] [method-args] [--output DIR] [--search-path DIR] [--config config-args]
```
where
- `method`can be a `method` of `class` or of an object in `class.cfg`
- `method-args` is a space-separated list of `key=val`arguments to pass to method 
- `--output`specifies a directory to store *@cacheable* output (and to find it in)
- `--search-path` specifies directories to look for `@cacheable` output in
- `config-args` is a space-separated list of `key=val`arguments to initialize `class`
