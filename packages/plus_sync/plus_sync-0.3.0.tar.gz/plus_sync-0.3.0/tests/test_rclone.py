from pathlib import Path

from tests.helpers.sync import sync_tester


def test_rclone(plus_sync_cmd, initialized, rclone_config, subjects_in_folder):
    subjects, tmpdir_path = subjects_in_folder(3, 'testdata')

    result = plus_sync_cmd(
        ['add', 'rclone', 'test_rclone', 'test', str(Path(tmpdir_path, 'testdata')), '--globs', '*.txt']
    )
    assert result.exit_code == 0
    assert 'Done' in result.stdout

    sync_tester(plus_sync_cmd, subjects, 'test_rclone')


def test_partial_sync(plus_sync_cmd, initialized, rclone_config, subjects_in_folder):
    subjects, tmpdir_path = subjects_in_folder(3, 'testdata')
    result = plus_sync_cmd(
        ['add', 'rclone', 'test_rclone', 'test', str(Path(tmpdir_path, 'testdata')), '--globs', '*.txt']
    )
    assert result.exit_code == 0
    result = plus_sync_cmd(['sync', 'test_rclone'])
    assert result.exit_code == 0
    assert 'Found 3 files, 3 need syncing.' in result.stdout
    subject_path = Path('data_synced/test_rclone', subjects[0].hashed_filename)
    assert subject_path.exists()
    subject_path.unlink()
    assert not subject_path.exists()
    result = plus_sync_cmd(['sync', 'test_rclone'])
    assert result.exit_code == 0
    assert 'Found 3 files, 1 need syncing.' in result.stdout
    assert subject_path.exists()
    subject_path.write_text('new content')
    result = plus_sync_cmd(['sync', 'test_rclone'])
    assert result.exit_code == 0
    assert 'Found 3 files, 1 need syncing.' in result.stdout
