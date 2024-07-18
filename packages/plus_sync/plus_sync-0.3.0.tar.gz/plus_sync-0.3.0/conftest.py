import shutil
from functools import partial
from pathlib import Path

import pytest
from typer.testing import CliRunner

import plus_sync.cmd as ps_command

runner = CliRunner()


@pytest.fixture(autouse=True)
def to_temp_folder(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture(autouse=True)
def configure_rclone(monkeypatch):
    monkeypatch.setenv('RCLONE_CONFIG', 'rclone.conf')
    yield


@pytest.fixture(scope='session')
def plus_sync_cmd():
    return partial(runner.invoke, ps_command.app)


@pytest.fixture(scope='function')
def initialized(plus_sync_cmd):
    # remove config file if it exists
    Path('plus_sync.toml').unlink(missing_ok=True)
    # remove data folder recursively if it exists
    if Path('data_synced').exists():
        shutil.rmtree('data_synced')
    result = plus_sync_cmd(['init'], input='test\n')
    assert result.exit_code == 0
    assert 'Done' in result.stdout


@pytest.fixture
def sftp_fixture(sftpserver):
    # https://github.com/ulope/pytest-sftpserver/issues/30
    # Tests hanging forever
    sftpserver.daemon_threads = True
    sftpserver.block_on_close = False
    yield sftpserver
