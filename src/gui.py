import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
import os

CONFIG_PATH = "config/sync_config.yml"

LANGS = {
    "fr": {
        "add_repo": "Ajouter un dépôt",
        "save_config": "Enregistrer la configuration",
        "run_sync": "Lancer la synchronisation",
        "quit": "Quitter",
        "config_tab": "Configuration",
        "console_tab": "Console",
        "console_label": "Console (output du programme)",
        "saved": "Configuration enregistrée dans",
        "sync_target": "Cible de synchronisation",
        "github_token": "Jeton GitHub",
        "github_repo": "Dépôt GitHub (utilisateur/dépôt)",
        "local_path": "Chemin local",
        "watch_paths": "Chemins à surveiller (séparés par des virgules)",
        "sync_delay": "Délai de synchronisation (secondes)",
        "force_sync": "Forcer la synchronisation (true/false)",
        "create_new_branch": "Créer une nouvelle branche (true/false)",
        "target_branch": "Branche cible",
        "local_dominance": "Dominance locale (true/false)",
        "remove": "X",
        "browse": "Parcourir",
        "monitoring_started": "Surveillance démarrée. Fermez la fenêtre pour arrêter.",
        "watching_dir": "Surveillance du dossier",
        "error_config": "Erreur de configuration",
        "error": "Erreur",
        "title": "Git Auto Sync",
        "lang_btn": "English",
    },
    "en": {
        "add_repo": "Add repository",
        "save_config": "Save configuration",
        "run_sync": "Start synchronization",
        "quit": "Quit",
        "config_tab": "Configuration",
        "console_tab": "Console",
        "console_label": "Console (program output)",
        "saved": "Configuration saved to",
        "sync_target": "Sync Target",
        "github_token": "GitHub Token",
        "github_repo": "GitHub Repo (user/repo)",
        "local_path": "Local Path",
        "watch_paths": "Watch Paths (comma separated)",
        "sync_delay": "Sync Delay (seconds)",
        "force_sync": "Force Sync (true/false)",
        "create_new_branch": "Create New Branch (true/false)",
        "target_branch": "Target Branch",
        "local_dominance": "Local Dominance (true/false)",
        "remove": "X",
        "browse": "Browse",
        "monitoring_started": "Monitoring started. Close the window to stop.",
        "watching_dir": "Watching directory",
        "error_config": "Configuration error",
        "error": "Error",
        "title": "Git Auto Sync",
        "lang_btn": "Français",
    }
}

class SyncTargetFrame(ttk.LabelFrame):
    def __init__(self, master, idx, remove_callback=None, lang="fr", **kwargs):
        self.lang = lang
        self.texts = LANGS[self.lang]
        super().__init__(master, text=f"{self.texts['sync_target']} {idx+1}", **kwargs)
        self.entries = {}
        self.remove_callback = remove_callback
        self._fields = [
            ("github_token", "github_token"),
            ("github_repo", "github_repo"),
            ("local_path", "local_path"),
            ("watch_paths", "watch_paths"),
            ("sync_delay", "sync_delay"),
            ("force_sync", "force_sync"),
            ("create_new_branch", "create_new_branch"),
            ("target_branch", "target_branch"),
            ("local_dominance", "local_dominance"),
        ]
        placeholders = {
            "github_token": "ghp_xxx...",
            "github_repo": "user/repo",
            "local_path": "C:/path/to/dir",
            "watch_paths": "C:/path1,C:/path2",
            "sync_delay": "60",
            "force_sync": "true/false",
            "create_new_branch": "true/false",
            "target_branch": "main",
            "local_dominance": "true/false",
        }
        for i, (label_key, key) in enumerate(self._fields):
            ttk.Label(self, text=self.texts[label_key]).grid(row=i, column=0, sticky="w")
            entry = ttk.Entry(self, width=40)
            entry.grid(row=i, column=1, sticky="ew")
            # Set placeholder
            entry.insert(0, placeholders.get(key, ""))
            self.entries[key] = entry

        # Add browse button for local_path
        def browse():
            path = filedialog.askdirectory()
            if path:
                self.entries["local_path"].delete(0, tk.END)
                self.entries["local_path"].insert(0, path)
        browse_btn = ttk.Button(self, text=self.texts["browse"], command=browse)
        browse_btn.grid(row=2, column=2, padx=2)

        # Add remove "X" button
        remove_btn = ttk.Button(self, text=self.texts["remove"], width=2, command=self._remove_self)
        remove_btn.grid(row=0, column=3, padx=2, sticky="e")

        self._browse_btn = browse_btn
        self._remove_btn = remove_btn
        self._labels = [child for child in self.winfo_children() if isinstance(child, ttk.Label)]

    def _remove_self(self):
        if self.remove_callback:
            self.remove_callback(self)

    def get_data(self):
        data = {}
        errors = []
        for key, entry in self.entries.items():
            val = entry.get().strip()
            # Validation
            if key in ("github_token", "github_repo", "local_path", "target_branch") and not val:
                errors.append(f"{key} is required")
            if key == "github_repo" and val and "/" not in val:
                errors.append("github_repo doit être du format user/repo")
            if key == "sync_delay":
                if not val:
                    data[key] = 5  # valeur par défaut
                else:
                    try:
                        data[key] = int(val)
                        if data[key] < 1:
                            errors.append("sync_delay doit être >= 1")
                    except Exception:
                        data[key] = 5  # valeur par défaut si non numérique
            elif key == "watch_paths":
                data[key] = [p.strip() for p in val.split(",") if p.strip()]
                if not data[key]:
                    errors.append("watch_paths ne doit pas être vide")
            elif key in ("force_sync", "create_new_branch", "local_dominance"):
                data[key] = val.lower() == "true"
            else:
                if key not in data:
                    data[key] = val
        if errors:
            raise ValueError("; ".join(errors))
        return data

    def set_data(self, data):
        # Remplit les champs à partir d'un dict
        for key, entry in self.entries.items():
            val = data.get(key, "")
            if isinstance(val, list):
                val = ",".join(val)
            elif isinstance(val, bool):
                val = "true" if val else "false"
            entry.delete(0, tk.END)
            entry.insert(0, str(val))

    def set_language(self, lang, idx):
        self.lang = lang
        self.texts = LANGS[self.lang]
        self.config(text=f"{self.texts['sync_target']} {idx+1}")
        for i, (label_key, key) in enumerate(self._fields):
            self._labels[i].config(text=self.texts[label_key])
        self._browse_btn.config(text=self.texts["browse"])
        self._remove_btn.config(text=self.texts["remove"])

class SyncConfigGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "fr"
        self.texts = LANGS[self.lang]
        self.title(self.texts["title"])
        self.geometry("750x700")
        self.frames = []

        # --- Notebook (tabs) setup ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # --- Tab 1: Configuration ---
        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text=self.texts["config_tab"])

        # --- Tab 2: Console ---
        self.tab_console = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_console, text=self.texts["console_tab"])

        # --- Configuration tab content ---
        container = ttk.Frame(self.tab_config)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.frame_container = ttk.Frame(canvas)

        self.frame_container.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.frame_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # --- Buttons (in config tab) ---
        btn_frame = ttk.Frame(self.tab_config)
        btn_frame.pack(pady=5)
        self.add_target_btn = ttk.Button(btn_frame, text=self.texts["add_repo"], command=self.add_target)
        self.add_target_btn.pack(side="left", padx=5)
        self.load_btn = ttk.Button(btn_frame, text="Charger la configuration", command=self.load_config)
        self.load_btn.pack(side="left", padx=5)
        self.save_btn = ttk.Button(btn_frame, text=self.texts["save_config"], command=self.save_config)
        self.save_btn.pack(side="left", padx=5)
        self.run_btn = ttk.Button(btn_frame, text=self.texts["run_sync"], command=self.run_sync_from_gui)
        self.run_btn.pack(side="left", padx=5)
        self.quit_btn = ttk.Button(btn_frame, text=self.texts["quit"], command=self.close_gui)
        self.quit_btn.pack(side="left", padx=5)
        self.lang_btn = ttk.Button(btn_frame, text=self.texts["lang_btn"], command=self.toggle_language)
        self.lang_btn.pack(side="left", padx=5)

        # --- Console (in console tab) ---
        self.console_frame = ttk.LabelFrame(self.tab_console, text=self.texts["console_label"])
        self.console_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.console_text = tk.Text(self.console_frame, height=12, state="disabled", bg="#222", fg="#0f0")
        self.console_text.pack(fill="both", expand=True)

        self.add_target()  # Add first target by default

    def add_target(self):
        idx = len(self.frames)
        frame = SyncTargetFrame(self.frame_container, idx, remove_callback=self.remove_target, lang=self.lang)
        frame.pack(fill="x", pady=10, padx=10)
        self.frames.append(frame)
        self._refresh_labels()

    def remove_target(self, frame):
        frame.destroy()
        self.frames.remove(frame)
        self._refresh_labels()

    def _refresh_labels(self):
        # Met à jour les titres des frames après suppression/ajout
        for i, frame in enumerate(self.frames):
            frame.set_language(self.lang, i)

    def save_config(self):
        try:
            sync_targets = []
            for idx, frame in enumerate(self.frames):
                try:
                    data = frame.get_data()
                    # Vérification des champs obligatoires
                    missing = []
                    for field in ["github_token", "github_repo", "local_path", "watch_paths", "target_branch"]:
                        val = data.get(field)
                        if not val or (isinstance(val, list) and not any(val)):
                            missing.append(field)
                    if missing:
                        msg = f"❌ Cible #{idx+1} : Les champs suivants sont obligatoires et vides : {', '.join(missing)}"
                        self.show_error(msg)
                        return
                    sync_targets.append(data)
                except Exception as e:
                    self.show_error(str(e))
                    return
            if not sync_targets:
                self.show_error("Aucune cible de synchronisation valide à sauvegarder.")
                return
            config = {"sync_targets": sync_targets}
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True)
            messagebox.showinfo(self.texts["saved"], f"{self.texts['saved']} {CONFIG_PATH}")
        except Exception as e:
            self.show_error(str(e))

    def load_config(self):
        # Charge la config YAML et remplit les frames
        try:
            if not os.path.exists(CONFIG_PATH):
                self.show_error(f"Fichier de configuration introuvable : {CONFIG_PATH}")
                return
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            sync_targets = data.get("sync_targets", [])
            # Supprime les frames existantes
            for frame in self.frames:
                frame.destroy()
            self.frames.clear()
            # Ajoute une frame par cible
            for idx, target in enumerate(sync_targets):
                frame = SyncTargetFrame(self.frame_container, idx, remove_callback=self.remove_target, lang=self.lang)
                frame.set_data(target)
                frame.pack(fill="x", pady=10, padx=10)
                self.frames.append(frame)
            self._refresh_labels()
            self.append_console(f"✅ Configuration chargée depuis {CONFIG_PATH}")
        except Exception as e:
            self.show_error(f"Erreur lors du chargement : {e}")

    def close_gui(self):
        self.destroy()
        # La console Python reste ouverte pour les logs

    # Optionnel : méthode pour afficher un message dans la zone console
    def append_console(self, text):
        self.console_text.config(state="normal")
        self.console_text.insert(tk.END, text + "\n")
        self.console_text.see(tk.END)
        self.console_text.config(state="disabled")

    def show_error(self, msg):
        self.append_console(msg)
        messagebox.showerror(self.texts["error"], msg)

    def run_sync_from_gui(self):
        from src.config import SyncConfig
        from src.git_sync import GitSyncManager
        from src.watcher import FileChangeHandler
        import logging
        import threading
        from watchdog.observers import Observer
        import time

        sync_targets = []
        for idx, frame in enumerate(self.frames):
            try:
                data = frame.get_data()
                # Vérification des champs obligatoires
                missing = []
                for field in ["github_token", "github_repo", "local_path", "watch_paths", "target_branch"]:
                    val = data.get(field)
                    if not val or (isinstance(val, list) and not any(val)):
                        missing.append(field)
                if missing:
                    msg = f"❌ Cible #{idx+1} : Les champs suivants sont obligatoires et vides : {', '.join(missing)}"
                    self.show_error(msg)
                    return
                sync_targets.append(data)
            except Exception as e:
                self.show_error(f"❌ Cible #{idx+1} : {e}")
                return

        configs = []
        errors = []
        for idx, target in enumerate(sync_targets):
            try:
                config = SyncConfig(**target)
                config.validate()
                configs.append(config)
            except Exception as e:
                msg = f"{self.texts['error_config']} (#{idx+1}): {e}"
                self.show_error(msg)
                errors.append(msg)

        if errors or not configs:
            return

        def sync_thread():
            logger = logging.getLogger(__name__)
            observer = Observer()
            sync_managers = []
            try:
                for config in configs:
                    try:
                        sync_manager = GitSyncManager(config)
                        sync_managers.append(sync_manager)
                        event_handler = FileChangeHandler(sync_manager)
                        for path in config.watch_paths:
                            observer.schedule(event_handler, path, recursive=True)
                            self.append_console(f"{self.texts['watching_dir']}: {path} (repo: {config.github_repo})")
                        self.append_console(f"✅ {config.local_path} prêt pour la synchronisation.")
                    except Exception as e:
                        err_msg = f"❌ {config.local_path} : {e}"
                        self.show_error(err_msg)
                if not sync_managers:
                    self.append_console("Aucune cible valide pour la synchronisation.")
                    return
                observer.start()
                self.append_console(self.texts["monitoring_started"])
                while True:
                    time.sleep(1)
            except Exception as e:
                err_msg = f"{self.texts['error']}: {e}"
                self.show_error(err_msg)
            finally:
                observer.stop()
                if observer.is_alive():
                    observer.join()

        import threading
        threading.Thread(target=sync_thread, daemon=True).start()

    def toggle_language(self):
        self.lang = "en" if self.lang == "fr" else "fr"
        self.texts = LANGS[self.lang]
        self.title(self.texts["title"])
        # Tabs
        self.notebook.tab(0, text=self.texts["config_tab"])
        self.notebook.tab(1, text=self.texts["console_tab"])
        # Buttons
        self.add_target_btn.config(text=self.texts["add_repo"])
        self.save_btn.config(text=self.texts["save_config"])
        self.run_btn.config(text=self.texts["run_sync"])
        self.quit_btn.config(text=self.texts["quit"])
        self.lang_btn.config(text=self.texts["lang_btn"])
        self.load_btn.config(text="Load configuration" if self.lang == "en" else "Charger la configuration")
        # Console label
        self.console_frame.config(text=self.texts["console_label"])
        # Frames
        self._refresh_labels()

if __name__ == "__main__":
    app = SyncConfigGUI()
    app.mainloop()
