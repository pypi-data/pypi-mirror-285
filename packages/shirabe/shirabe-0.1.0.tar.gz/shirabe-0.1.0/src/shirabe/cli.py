import argparse
from pathlib import Path

from shirabe.deps import DependenciesCompiler
from shirabe.venv import ShirabeEnvBuilder


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    alpha_parser = subparsers.add_parser("alpha")
    alpha_parser.add_argument(
        "dir",
        metavar="ENV_DIR",
        help="A directory to create the environment in.",
    )
    alpha_parser.add_argument(
        "--with-pip",
        action="store_true",
        help=(
            "Skips installing in the virtual environment "
            "(pip is not bootstrapped by default)"
        ),
    )
    options = parser.parse_args()

    working_dir = Path.cwd()
    DependenciesCompiler(working_dir).run()

    builder = ShirabeEnvBuilder(with_pip=options.with_pip)
    builder.create(options.dir)
