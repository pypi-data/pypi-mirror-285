import datetime
from fnmatch import fnmatch
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import gitlab
import joblib
from gitlab.utils import EncodedId

from .base import BaseSync, FileInformation

if TYPE_CHECKING:
    import plus_sync.config


def _fetch_metadata(file_path: str, gl: gitlab.Gitlab, project_id: int, branch: str) -> dict:
    return gl.http_head(
        f'/projects/{project_id}/repository/files/{EncodedId(file_path)}', query_parameters={'ref': branch}
    )


class GitlabAccess(BaseSync):
    def __init__(self, gitlab_project: 'plus_sync.config.GitlabConfig'):
        self.gitlab_project = gitlab_project
        token = Path(gitlab_project.token_file).read_text().strip()
        self.gl = gitlab.Gitlab(self.gitlab_project.host, private_token=token)
        self.project = self.gl.projects.get(self.gitlab_project.slug)
        self.commits = self.project.commits.list(all=True)
        self.metadata_cache = {}

    def _get_files(self, with_metadata=True):
        all_files = self._get_files_local()
        if with_metadata:
            self._fetch_metadata(all_files)

            all_files = [
                FileInformation(
                    path=x['path'],
                    size=self._get_file_size(x),
                    last_modified=self._get_file_lastmod(x),
                    hashes={'sha256': self._get_file_sha256(x)},
                )
                for x in all_files
            ]
        else:
            all_files = [FileInformation(path=x['path']) for x in all_files]
        return all_files

    def _get_files_local(self):
        all_files = []

        for cur_path in self.gitlab_project.paths:
            files_generator = self.project.repository_tree(
                path=cur_path, recursive=True, iterator=True, ref=self.gitlab_project.branch
            )
            file_list = [
                x
                for x in files_generator
                if x['type'] == 'blob' and any(fnmatch(x['path'], glob) for glob in self.gitlab_project.globs)
            ]
            all_files.extend(file_list)

        return all_files

    def _get_commit(self, id):
        return [x for x in self.commits if x.id == id][0]

    def _fetch_metadata(self, file_paths: list[str]) -> None:
        def d_fetch(f):
            return _fetch_metadata(f['path'], self.gl, self.project.id, self.gitlab_project.branch)

        tmp = joblib.Parallel(n_jobs=30)(joblib.delayed(d_fetch)(f) for f in file_paths)
        self.metadata_cache = {x['x-gitlab-file-path']: x for x in tmp}

    @cache
    def _get_file_meta(self, file_path):
        return self.metadata_cache[file_path]

    def _get_file_sha256(self, file):
        return self._get_file_meta(file['path'])['x-gitlab-content-sha256']

    def _get_file_size(self, file):
        return self._get_file_meta(file['path'])['x-gitlab-size']

    def _get_file_last_commit(self, file):
        return self._get_file_meta(file['path'])['x-gitlab-last-commit-id']

    def _get_file_lastmod(self, file):
        commit_id = self._get_file_last_commit(file)
        return datetime.datetime.fromisoformat(self._get_commit(commit_id).committed_date)

    def get_content(self, file: FileInformation) -> bytes:
        return self.project.files.get(file.path, ref=self.gitlab_project.branch).decode()
