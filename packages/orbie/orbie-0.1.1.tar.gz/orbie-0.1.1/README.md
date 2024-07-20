# Orbie

A checker to guide the web of Python code in strictly architected projects and
restrict tangling up of code.

Orbie is named after the orb-weaver spider which can make complex web patterns.

## Example Use Case

Imagine you have a single Python project with several subprojects being shipped
as part of it but you want to have some level of isolation between the modules.
(Yes, you could split it into several projects to enforce that but maybe you
cannot for some reason). Or you want to strictly control the import mapping
between the different parts of your project.

Why might you not want this? Having a tangled web of interdependencies may be
undesireable as it increases the complexity of the project. By trimming and
restricting these interdependencies, the complexity can be reduced and options
open up such as optimising the ci-cd to test only the changed subprojects
without fear of missing re-testing unrelated but affected components.

Take this Python project structure below as an example.

```
src/
└── example
    ├── example_a
    │   ├── example_a.py
    │   ├── __init__.py
    │   ├── nephews
    │   │   └── nephew.py
    │   └── sibling.py
    ├── example_b
    │   ├── example_b.py
    │   └── __init__.py
    ├── example_c
    │   ├── example_c.py
    │   └── __init__.py
    ├── example_shared
    │   ├── __init__.py
    │   └── shared.py
    └── __init__.py
```

We may not want `example_a.py` referencing anything from `example_b.py` or
`example_c.py`.

This can be enforced with some simple code review but that may fail if the
reviewer does not have enough coffee. We need a more complicated solution for
the sake of being programmers building tools for programmers.

Orbie is a tool that exists to enforce isolation (so it can be enforced via
automation). It detects imports that reference other modules within the same
project space but that are cousins or ancestors.

## How It Works

Orbie uses [importlab](https://github.com/google/importlab) to statically
parse the imports dependency tree and filters external dependencies and nested
dependencies to find dependencies that pull from parent paths within the same
Python package/project. If the number of these exceed zero, the script will exit
with error code `1`.

## Installation

TODO.

## Usage

```
$ pdm run orbie --help
usage: orbie [-h]
               [--exception EXCEPTIONS]
               [--no-ignore-siblings] 
               [--no-ignore-venv]
               [--project-root PROJECT_ROOT]
               [-V PYTHON_VERSION]
               [-P PYTHONPATH]
               input

positional arguments:
  input                 Input file

options:
  -h, --help            show this help message and exit
  --exception EXCEPTIONS
                        Adds an exception for a module path or directory path
  --no-ignore-siblings  Toggle to not ignore tangled files within the same
                        parent directory
  --no-ignore-venv      Toggle to not ignore tangled files found in .venv
  --project-root PROJECT_ROOT
                        Base project path to find tangled files within (default:
                        ./)
  -V PYTHON_VERSION, --python_version PYTHON_VERSION
                        Python version of target code, e.g. "2.7"
  -P PYTHONPATH, --pythonpath PYTHONPATH
                        Directories for reading dependencies - a list of paths
                        separated by ":".
```

Example:

```
cd example
pdm install
orbie src/example/example_one.py
```

### Usage: Exceptions

Of course, restricting interdependencies to 0 typically makes no sense. The more
realistic use case of Orbie is to only allow select interdependencies that
meet the architecture of the project. One example might be only allowing modules
in a specific shared space from being imported (thus creating a clear structure
around the interdependencies).

These exceptional import paths can be specified with `--exceptions`.
