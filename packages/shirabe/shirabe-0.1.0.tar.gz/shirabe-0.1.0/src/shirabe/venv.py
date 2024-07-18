import os
import os.path
import subprocess
import sys
import tempfile
from venv import EnvBuilder


class ShirabeEnvBuilder(EnvBuilder):
    def post_setup(self, context):
        env_dir = context.env_dir
        requirements_file = os.path.join(
            os.path.dirname(env_dir), "requirements.txt"
        )
        if os.path.exists(requirements_file):
            self._install_requirements(context, requirements_file)

    def _install_requirements(self, context, requirements_file: str):
        commands = [
            context,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "-r",
            requirements_file,
        ]
        if self.with_pip:
            self._call_new_python(*commands)
            return

        # ref: https://github.com/astral-sh/rye/blob/0.34.0/rye/src/sync.rs#L270-L274  # NOQA: E501
        shirabe_running_python = sys.executable
        shirabe_running_python_root = os.path.dirname(
            os.path.dirname(shirabe_running_python)
        )
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        shirabe_site_packages = os.path.join(
            shirabe_running_python_root,
            f"lib/python{python_version}/site-packages",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            os.symlink(
                os.path.join(shirabe_site_packages, "pip"),
                os.path.join(tmpdir, "pip"),
            )
            os.environ["PYTHONPATH"] = tmpdir
            self._call_new_python_keep_pythonpath(*commands)

    def _call_new_python(self, context, *py_args, **kwargs):
        # Avoid for mypy to raise [attr-defined] error
        # >error: "ShirabeEnvBuilder" has no attribute "_call_new_python"
        return super()._call_new_python(context, *py_args, **kwargs)

    def _call_new_python_keep_pythonpath(self, context, *py_args, **kwargs):
        # Tweak https://github.com/python/cpython/blob/v3.12.4/Lib/venv/__init__.py#L369-L382  # NOQA: E501
        args = [context.env_exec_cmd, *py_args]
        kwargs["env"] = env = os.environ.copy()
        env["VIRTUAL_ENV"] = context.env_dir
        env.pop("PYTHONHOME", None)
        # env.pop("PYTHONPATH", None)  # Keep PYTHONPATH
        kwargs["cwd"] = context.env_dir
        kwargs["executable"] = context.env_exec_cmd
        subprocess.check_output(args, **kwargs)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dir",
        metavar="ENV_DIR",
        help="A directory to create the environment in.",
    )
    options = parser.parse_args()

    builder = ShirabeEnvBuilder(with_pip=True)
    builder.create(options.dir)
