import yaml
import os
from dataclasses import dataclass
from github import Github

@dataclass
class SyncConfig:
    github_token: str
    github_repo: str
    local_path: str
    watch_paths: list
    sync_delay: int = 1
    force_sync: bool = False
    create_new_branch: bool = False
    branch_prefix: str = "sync"
    target_branch: str = "main"
    local_dominance: bool = False

    def validate(self):
        # Validate GitHub token and repo
        gh = Github(self.github_token)
        try:
            gh.get_repo(self.github_repo)
        except Exception as e:
            raise ValueError(f"Invalid GitHub repository: {e}")

        # Validate paths
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)
        
        for path in self.watch_paths:
            if not os.path.exists(path):
                os.makedirs(path)

        # Validate sync delay
        if self.sync_delay < 1:
            raise ValueError("sync_delay must be at least 1 second")

        if not isinstance(self.force_sync, bool):
            raise ValueError("force_sync must be a boolean")

        # Validate branch settings
        if self.create_new_branch and not isinstance(self.branch_prefix, str):
            raise ValueError("branch_prefix must be a string")

        # Validate sync strategy
        if not isinstance(self.local_dominance, bool):
            raise ValueError("local_dominance must be a boolean")

    @classmethod
    def from_yaml(cls, path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            if "sync_targets" in data:
                configs = []
                for target in data["sync_targets"]:
                    config = cls(**target)
                    config.validate()
                    configs.append(config)
                return configs
            else:
                config = cls(**data)
                config.validate()
                return [config]
