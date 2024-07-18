import sys
from unittest.mock import ANY, patch

from piptools.scripts import compile

from shirabe.cli import main


def run_shirabe(venv_path):
    with patch.object(sys, "argv", ["shirabe", "alpha", venv_path]):
        main()


@patch("shirabe.venv.ShirabeEnvBuilder._install_requirements")
@patch("shirabe.deps.click.Context.invoke")
def test_shirabe_with_resolved_dependencies(
    click_invoke, _install_requirements, tmp_path, monkeypatch
):
    requirements_file_path = tmp_path / "requirements.txt"
    requirements_file_path.write_text("kojo-fan-art==0.1.1")

    with monkeypatch.context() as m:
        m.chdir(tmp_path)
        run_shirabe(".venv")

    click_invoke.assert_not_called()
    _install_requirements.assert_called_once_with(
        ANY, str(requirements_file_path)
    )


@patch("shirabe.venv.ShirabeEnvBuilder._install_requirements")
@patch("shirabe.deps.click.Context.invoke")
def test_shirabe_with_direct_dependencies(
    click_invoke, _install_requirements, tmp_path, monkeypatch
):
    requirements_file_path = tmp_path / "requirements.txt"

    def dummy_generate_resolved_dependencies(click_command):
        requirements_file_path.write_text("kojo-fan-art==0.1.1")

    click_invoke.side_effect = dummy_generate_resolved_dependencies

    direct_dependencies_file_path = tmp_path / "requirements.in"
    direct_dependencies_file_path.write_text("kojo-fan-art")

    with monkeypatch.context() as m:
        m.chdir(tmp_path)
        run_shirabe(".venv")

    click_invoke.assert_called_once_with(compile.cli)
    _install_requirements.assert_called_once_with(
        ANY, str(requirements_file_path)
    )
