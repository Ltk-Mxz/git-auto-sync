import yaml
import time
import os
import logging
import sys
from watchdog.observers import Observer
from src.watcher import FileChangeHandler
from src.git_sync import GitSyncManager
from src.config import SyncConfig

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('sync.log')
        ]
    )

def run_sync(configs):
    logger = logging.getLogger(__name__)
    observer = Observer()
    sync_managers = []
    for config in configs:
        sync_manager = GitSyncManager(config)
        sync_managers.append(sync_manager)
        event_handler = FileChangeHandler(sync_manager)
        for path in config.watch_paths:
            observer.schedule(event_handler, path, recursive=True)
            logger.info(f"Watching directory: {path} (repo: {config.github_repo})")
    observer.start()
    logger.info("Monitoring started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping monitoring...")
    finally:
        observer.stop()
        if observer.is_alive():
            observer.join()

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    # Mode GUI ou exécutable PyInstaller
    if "--gui" in sys.argv or getattr(sys, 'frozen', False):
        from src.gui import SyncConfigGUI
        app = SyncConfigGUI()
        app.mainloop()
        return

    # Mode console : YAML
    try:
        # Utilise le dossier du script/exe pour trouver config/sync_config.yml
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
        config_path = os.path.join(base_dir, 'config', 'sync_config.yml')
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            print(f"\nERREUR: Le fichier de configuration '{config_path}' est introuvable.\n"
                  "Créez-le via la GUI (python main.py --gui) ou copiez un exemple dans config/sync_config.yml\n")
            return

        configs = SyncConfig.from_yaml(config_path)
        run_sync(configs)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
