import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .git_sync import GitSyncManager

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, sync_manager):
        self.sync_manager = sync_manager

    def on_modified(self, event):
        if event.is_directory:
            return
        self.sync_manager.handle_change(event.src_path)
        
    def on_created(self, event):
        if event.is_directory:
            return
        self.sync_manager.handle_change(event.src_path)
        
    def on_deleted(self, event):
        if event.is_directory:
            return
        self.sync_manager.handle_change(event.src_path)
        
    def on_moved(self, event):
        if event.is_directory:
            return
        self.sync_manager.handle_change(event.dest_path)