import os
import git
from github import Github
import time
import logging
import datetime
from dataclasses import dataclass

@dataclass
class SyncConfig:
    github_token: str
    github_repo: str
    local_path: str
    watch_paths: list
    sync_delay: int = 5
    force_sync: bool = False
    create_new_branch: bool = False
    target_branch: str = "main"
    local_dominance: bool = False

class GitSyncManager:
    def __init__(self, config):
        self.config = config
        self.github = Github(config.github_token)
        self.remote_repo = self.github.get_repo(config.github_repo)
        self.logger = logging.getLogger(__name__)

        git_dir = os.path.join(config.local_path, '.git')
        local_path_empty = (
            not os.path.exists(config.local_path) or
            (os.path.isdir(config.local_path) and not os.listdir(config.local_path))
        )

        if os.path.exists(git_dir):
            self.repo = git.Repo(config.local_path)
        else:
            if local_path_empty:
                self.logger.info("Cloning repository...")
                self.repo = git.Repo.clone_from(
                    f'https://github.com/{config.github_repo}.git',
                    config.local_path
                )
            else:
                self.logger.info(f"No .git found in '{config.local_path}', initializing new git repository.")
                self.repo = git.Repo.init(config.local_path)
                # Try to add remote if not present
                try:
                    if 'origin' not in [remote.name for remote in self.repo.remotes]:
                        self.repo.create_remote('origin', f'https://github.com/{config.github_repo}.git')
                except Exception as e:
                    self.logger.warning(f"Could not set remote: {e}")
                # Optionally, add all files and make initial commit if needed
                if self.repo.is_dirty(untracked_files=True):
                    self.repo.git.add(all=True)
                    self.repo.index.commit("Initial commit from existing directory")
                # Try to fetch remote if possible
                try:
                    self.repo.git.fetch('--all')
                except Exception as e:
                    self.logger.warning(f"Could not fetch remote: {e}")

        # Initial sync based on dominance
        self._sync_strategy()
        
        # Setup branch
        try:
            self.repo.git.checkout(config.target_branch)
        except git.GitCommandError:
            self.logger.info(f"Creating branch {config.target_branch}")
            self.repo.git.checkout('-b', config.target_branch)
        
        self.last_sync = time.time()
        self.sync_delay = config.sync_delay

    def _sync_strategy(self):
        """Apply sync strategy based on dominance setting"""
        try:
            if self.config.local_dominance:
                self.logger.info("Local dominance: pushing local changes to remote")
                # Force local changes to remote
                self.repo.git.add('.')
                if self.repo.is_dirty():
                    self.repo.index.commit("Initial sync: Local changes dominant")
                    self.repo.git.push('--force', 'origin', self.config.target_branch)
            else:
                self.logger.info("Remote dominance: pulling remote changes to local")
                # Force remote changes to local
                self.repo.git.fetch('--all')
                self.repo.git.reset('--hard', f'origin/{self.config.target_branch}')
                self.repo.git.clean('-fd')
        except Exception as e:
            self.logger.error(f"Error during sync strategy: {e}")

    def handle_change(self, file_path):
        if time.time() - self.last_sync < self.sync_delay:
            return

        try:
            if '.git' in file_path or file_path.endswith('.lock'):
                return

            if self.config.local_dominance:
                # Local changes take priority
                self.repo.git.add('.')
                if self.repo.is_dirty():
                    self.repo.index.commit(f"Auto-sync: Changes in {os.path.basename(file_path)}")
                    self.repo.git.push('--force', 'origin', self.config.target_branch)
            else:
                # Remote changes take priority
                self.repo.git.fetch('--all')
                self.repo.git.reset('--hard', f'origin/{self.config.target_branch}')
                self.repo.git.clean('-fd')
                
            self.last_sync = time.time()
            self.logger.info(f"Synced changes in {file_path}")
        except Exception as e:
            self.logger.error(f"Error syncing changes: {e}")
