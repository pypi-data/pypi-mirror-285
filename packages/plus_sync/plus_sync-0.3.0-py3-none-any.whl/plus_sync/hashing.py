import hashlib
import re

import plus_sync.config


class SubjectIDHasher:
    def __init__(self, config: 'plus_sync.config.Config'):
        self.config = config
        self.subject_id_regex = re.compile(config.subject_id_regex)

    @classmethod
    def from_cmdargs(cls) -> 'SubjectIDHasher':
        config = plus_sync.config.Config.from_cmdargs()

        return cls(config)

    def hash_subject_id(self, subject_id: str) -> str:
        h = hashlib.sha256()
        h.update(subject_id.encode())
        h.update(self.config.project_name.encode())

        return h.hexdigest()[:12]

    def replace_subject_ids(self, text: str) -> str:
        return re.sub(self.subject_id_regex, lambda x: self.hash_subject_id(x.group()), text)
