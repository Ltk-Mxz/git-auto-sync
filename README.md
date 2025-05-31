# Git Auto Sync

This project automatically synchronizes multiple local folders with different GitHub repositories, monitoring changes in real time. It provides a graphical user interface (GUI) for easy configuration of sync targets, as well as a command-line interface (CLI).

## Features

- Automatic synchronization of multiple local folders to different GitHub repositories.
- Real-time monitoring of file changes (creation, modification, deletion, move).
- Local or remote dominance management (`local_dominance`).
- Graphical interface to edit configuration and start synchronization.
- Easy export to executable with PyInstaller.

## Prerequisites

- **Python 3.8+**
- **Git** installed on your machine (and accessible in the PATH)
- A GitHub token with write access to the relevant repositories.

## Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Configuration is done in the file:  
`config/sync_config.yml`

To sync multiple folders/repos, use the `sync_targets` key:

```yaml
sync_targets:
  - github_token: "ghp_xxx"
    github_repo: "user1/repo1"
    local_path: "C:/Users/xxx/Documents/Project1"
    watch_paths:
      - "C:/Users/xxx/Documents/Project1"
    sync_delay: 60
    force_sync: true
    create_new_branch: false
    target_branch: "main"
    local_dominance: true

  - github_token: "ghp_yyy"
    github_repo: "user2/repo2"
    local_path: "D:/Work/Project2"
    watch_paths:
      - "D:/Work/Project2"
    sync_delay: 300
    force_sync: false
    create_new_branch: false
    target_branch: "main"
    local_dominance: false
```

Each block represents an independent sync target.

## Usage

### Graphical mode (GUI)

To edit the configuration and start synchronization:

```bash
python main.py --gui
```

- Add/remove sync targets.
- Save the configuration.
- Start synchronization directly from the GUI ("Start Sync" button).

### Automatic mode (CLI)

To start automatic synchronization (all targets from YAML):

```bash
python main.py
```

## Export as executable

From the GUI, click "Export as EXE (PyInstaller)"  
Or from the command line:

```bash
pyinstaller --onefile --noconsole main.py
```

## Main dependencies

- [PyYAML](https://pyyaml.org/)
- [watchdog](https://github.com/gorakhargosh/watchdog)
- [GitPython](https://gitpython.readthedocs.io/)
- [PyGithub](https://pygithub.readthedocs.io/)
- [tkinter](https://docs.python.org/3/library/tkinter.html) (for the GUI)

## Notes

- The program creates a `sync.log` file for operation tracking.
- Each sync target works independently.
- For each folder, the program initializes a git repo if needed, or clones if the folder is empty.
- Multi-target configuration is managed via the `sync_targets` key in the YAML.

---

## Contribution

If you want to contribute, feel free to open issues or pull requests. All contributions are welcome!

## Authors and License

**Author:** Ltk-Mxz  
**License:** MIT
