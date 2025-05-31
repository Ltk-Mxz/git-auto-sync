# Git Auto Sync

Ce projet permet de synchroniser automatiquement plusieurs dossiers locaux avec différents dépôts GitHub, en surveillant les changements en temps réel. Il propose une interface graphique (GUI) pour configurer facilement les cibles de synchronisation, ainsi qu'une interface en ligne de commande (CLI).

## Fonctionnalités

- Synchronisation automatique de plusieurs dossiers locaux vers différents dépôts GitHub.
- Surveillance en temps réel des changements de fichiers (création, modification, suppression, déplacement).
- Gestion de la dominance locale ou distante (`local_dominance`).
- Interface graphique pour éditer la configuration et lancer la synchronisation.
- Export facile en exécutable avec PyInstaller.

## Prérequis

- **Python 3.8+**
- **Git** installé sur votre machine (et accessible dans le PATH)
- Un token GitHub avec accès en écriture aux dépôts concernés.

## Installation des dépendances

```bash
pip install -r requirements.txt
```

## Configuration

La configuration se fait dans le fichier :  
`config/sync_config.yml`

Pour synchroniser plusieurs dossiers/repos, utilisez la clé `sync_targets` :

```yaml
sync_targets:
  - github_token: "ghp_xxx"
    github_repo: "utilisateur1/repo1"
    local_path: "C:/Utilisateurs/xxx/Documents/Projet1"
    watch_paths:
      - "C:/Utilisateurs/xxx/Documents/Projet1"
    sync_delay: 60
    force_sync: true
    create_new_branch: false
    target_branch: "main"
    local_dominance: true

  - github_token: "ghp_yyy"
    github_repo: "utilisateur2/repo2"
    local_path: "D:/Travail/Projet2"
    watch_paths:
      - "D:/Travail/Projet2"
    sync_delay: 300
    force_sync: false
    create_new_branch: false
    target_branch: "main"
    local_dominance: false
```

Chaque bloc représente une cible indépendante.

## Utilisation

### Mode graphique (GUI)

Pour éditer la configuration et lancer la synchronisation :

```bash
python main.py --gui
```

- Ajoutez/supprimez des cibles de synchronisation.
- Enregistrez la configuration.
- Lancez la synchronisation directement depuis la GUI (bouton "Lancer la synchronisation").

### Mode automatique (CLI)

Pour lancer la synchronisation automatique (toutes les cibles du YAML) :

```bash
python main.py
```

## Exporter en exécutable

Depuis la GUI, cliquez sur "Export as EXE (PyInstaller)"  
Ou en ligne de commande :

```bash
pyinstaller --onefile --noconsole main.py
```

## Dépendances principales

- [PyYAML](https://pyyaml.org/)
- [watchdog](https://github.com/gorakhargosh/watchdog)
- [GitPython](https://gitpython.readthedocs.io/)
- [PyGithub](https://pygithub.readthedocs.io/)
- [tkinter](https://docs.python.org/3/library/tkinter.html) (pour la GUI)

## Notes

- Le programme crée un fichier `sync.log` pour le suivi des opérations.
- Chaque cible de synchronisation fonctionne indépendamment.
- Pour chaque dossier, le programme initialise un dépôt git si besoin, ou clone si le dossier est vide.
- La configuration multi-cible est gérée via la clé `sync_targets` dans le YAML.

---

## Contribution

Si vous souhaitez contribuer, n'hésitez pas à ouvrir des issues ou des pull requests. Toute contribution est la bienvenue !

## Auteurs et licence

**Auteur :** Ltk-Mxz  
**Licence :** MIT
