from pathlib import Path

import click
from piptools.scripts import compile


class DependenciesCompiler:
    def __init__(self, work_dir: Path) -> None:
        self.work_dir = work_dir

    def run(self):
        if not (self.work_dir / "requirements.txt").exists():
            click.Context(compile.cli).invoke(compile.cli)
