import sys
from pathlib import Path

from cmp180_evm.runtime import project_root


def test_source_root_contains_config():
    assert (project_root() / "configs/scpi_command_map.yaml").is_file()


def test_frozen_root_uses_executable_not_working_directory(monkeypatch, tmp_path):
    install = tmp_path / "可攜工作站"
    install.mkdir()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(install / "CMP180.exe"))
    monkeypatch.chdir(tmp_path)
    assert project_root() == install
    assert project_root() != Path.cwd()
