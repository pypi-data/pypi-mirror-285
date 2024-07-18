import subprocess
import tempfile
from pathlib import Path

import pytest

from tests.factories.subject_file import SubjectFileFactory


@pytest.fixture(scope='function')
def subjects_in_folder():
    with tempfile.TemporaryDirectory() as tmpdir:

        def _subjects_in_folder(n_subjects, path):
            tmpdir_path = Path(tmpdir)
            subjects = SubjectFileFactory.create_batch(n_subjects, path=path)
            for subject in subjects:
                subject.save_to_disk(tmpdir_path)

            return subjects, tmpdir_path

        yield _subjects_in_folder


@pytest.fixture(scope='function')
def rclone_config():
    rclone('config', 'create', 'test', 'local')
    yield
    Path('rclone.conf').unlink(missing_ok=True)


def rclone(*args):
    return subprocess.run(['rclone', '--config', 'rclone.conf', *args], capture_output=True, check=False)
