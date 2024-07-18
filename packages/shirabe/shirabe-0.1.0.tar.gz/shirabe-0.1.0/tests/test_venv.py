import sys
from unittest.mock import patch

from shirabe.venv import main


def run_shirabe(venv_path):
    with patch.object(sys, "argv", ["shirabe", venv_path]):
        main()


@patch("shirabe.venv.ShirabeEnvBuilder._install_requirements")
def test_python_m_shirabe_no_requirements(
    _install_requirements, tmp_path, monkeypatch
):
    with monkeypatch.context() as m:
        m.chdir(tmp_path)
        run_shirabe(".venv")

    _install_requirements.assert_not_called()
