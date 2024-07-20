#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from collections.abc import Collection
from pathlib import Path

from importlab import environment, graph, output  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exception",
        action="append",
        dest="exceptions",
        help="Adds an exception for a module path or directory path",
    )
    parser.add_argument(
        "--no-ignore-siblings",
        default=False,
        action="store_false",
        help="Toggle to not ignore tangled files within the same parent directory",
    )
    parser.add_argument(
        "--no-ignore-venv",
        default=False,
        action="store_false",
        help="Toggle to not ignore tangled files found in .venv",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Base project path to find tangled files within (default: ./)",
    )
    parser.add_argument("input", type=str, nargs=1, help="Input file")
    default_python_version = "%d.%d" % sys.version_info[:2]
    parser.add_argument(
        "-V",
        "--python_version",
        type=str,
        action="store",
        dest="python_version",
        default=default_python_version,
        help='Python version of target code, e.g. "2.7"',
    )
    parser.add_argument(
        "-P",
        "--pythonpath",
        type=str,
        action="store",
        dest="pythonpath",
        default="",
        help=(
            "Directories for reading dependencies - a list "
            'of paths separated by "%s".'
        )
        % os.pathsep,
    )
    return parser.parse_args()


def is_excepted(
    imported_path: Path, project_root: Path, exceptions: Collection[str]
) -> bool:
    relative_path = imported_path.relative_to(project_root)
    logger.debug("Checking imported_path for exceptions: %s", imported_path)
    logger.debug("Equivalent relative_path: %s", relative_path)

    # Handle exceptions that are marking files
    if str(relative_path) in exceptions:
        logger.debug("Ignoring %s as it's marked as an exception", imported_path)
        return True

    # Handle exceptions that are marking a directory
    # In case an exception path is a directory, check if relative_path
    # is a subdir of said exception path
    for exception in exceptions:
        exception_path = project_root / exception
        logger.debug("Checking %s", exception_path)

        if not exception_path.is_dir():
            logger.debug("Exception path is not a directory")
            continue

        logger.debug("Exception path is a directory")
        if exception_path not in relative_path.resolve().parents:
            logger.debug("Exception path is not a parent of %s", relative_path)
            continue

        logger.debug("Exception path is a parent of %s", relative_path)
        return True

    return False


def get_tangled_modules(
    import_graph: graph.ImportGraph,
    input_file: str,
    project_root: Path,
    ignore_venv: bool,
    ignore_siblings: bool,
    exceptions: Collection[str],
) -> Collection[Path]:
    tangled_modules = []
    keys = set(x[0] for x in import_graph.graph.edges)
    for key in sorted(keys):
        for _, value in sorted(import_graph.graph.edges([key])):
            project_root = project_root.resolve()
            venv_path = project_root / ".venv"
            importer_path = Path(input_file).resolve()
            imported_path = Path(value)

            # Ignore external imports
            if project_root not in imported_path.parents:
                logger.debug("Ignoring %s as it's not in project root", imported_path)
                continue
            # Ignore imports from venv (typically indicator of an external import)
            if ignore_venv and venv_path in imported_path.parents:
                logger.debug("Ignoring %s as it's part of .venv", imported_path)
                continue
            # Ignore imports within same parent directory
            if ignore_siblings and importer_path.parent in imported_path.parents:
                logger.debug(
                    "Ignoring %s as it's a sibling/niece/nephew", imported_path
                )
                continue
            # Ignore exceptions
            if is_excepted(imported_path, project_root, exceptions):
                logger.debug(
                    "Ignoring %s as it's marked as an exception", imported_path
                )
                continue

            # Mark import as a tangled import
            tangled_modules.append(imported_path)
    return tangled_modules


def main() -> None:
    args = parse_args()

    logger.info(
        "Checking tangleation of %s against other modules in %s",
        args.input,
        args.project_root.resolve(),
    )
    env = environment.create_from_args(args)
    import_graph = graph.ImportGraph.create(env, args.input, True)

    if args.no_ignore_venv:
        logger.warning("Considering imports from .venv")

    if args.no_ignore_siblings:
        logger.warning("Considering imports from siblings and nephews/nieces")

    if args.exceptions:
        logger.warning(
            "Ignoring the following exceptions:\n%s", "\n".join(args.exceptions)
        )

    logger.info("Source tree:")
    output.print_tree(import_graph)

    tangled_modules = get_tangled_modules(
        import_graph,
        args.input[0],
        args.project_root,
        not args.no_ignore_venv,
        not args.no_ignore_siblings,
        args.exceptions or [],
    )

    if len(tangled_modules) > 0:
        logger.info("%d tangled module/s found:", len(tangled_modules))
        for tangled_module in tangled_modules:
            logger.info("%s", tangled_module.relative_to(args.project_root.resolve()))
        sys.exit(1)
    else:
        logger.info("0 tangled modules found!")


if __name__ == "__main__":
    main()
