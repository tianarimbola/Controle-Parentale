# import os
# import sqlite3
# import psutil
# import time
# import threading
# from datetime import datetime, timedelta, date
# import customtkinter as ctk
# from tkinter import messagebox, colorchooser
# import sys
# import platform
# import ctypes
# import json
# import subprocess
#
# # Vérification des bibliothèques requises
# try:
#     import matplotlib.pyplot as plt
#     from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#     MATPLOTLIB_AVAILABLE = True
# except ImportError:
#     MATPLOTLIB_AVAILABLE = False
#     print("Matplotlib non disponible. Les graphiques ne seront pas affichés.")
#
# try:
#     import winapps
#     WINAPPS_AVAILABLE = True
# except ImportError:
#     WINAPPS_AVAILABLE = False
#     print("Winapps non disponible. La détection automatique des applications sera limitée.")
#
# try:
#     import wmi
#     WMI_AVAILABLE = True
# except ImportError:
#     WMI_AVAILABLE = False
#     print("WMI non disponible. La détection automatique des applications sera limitée.")
#
# # Configuration de l'interface
# ctk.set_appearance_mode("System")
# ctk.set_default_color_theme("blue")
#
# # Classe pour gérer les thèmes et couleurs
# class ThemeManager:
#     """Gestion des thèmes et couleurs de l'application"""
#     DEFAULT_THEME = {
#         "primary_button": "#3A7EBF",
#         "primary_button_hover": "#2D5F8F",
#         "success_button": "#2A8C36",
#         "success_button_hover": "#20752D",
#         "danger_button": "#D22B2B",
#         "danger_button_hover": "#A52121",
#         "neutral_button": "#6C757D",
#         "neutral_button_hover": "#5A6268",
#         "tab_bg": "#F0F0F0",
#         "card_bg": "#FFFFFF",
#         "card_text": "#333333",
#         "card_subtext": "#666666",
#         "positive_change": "#2A8C36",
#         "negative_change": "#D22B2B",
#         "chart_primary": "#4527A0",  # Couleur bleue pour le temps productif
#         "chart_secondary": "#FF5252"  # Couleur rouge pour les distractions
#     }
#
#     def __init__(self, config_path=None):
#         """Initialise le gestionnaire de thèmes"""
#         self.config_path = config_path or os.path.join(
#             os.path.expanduser("~"),
#             "AppMonitorData",
#             "theme_config.json"
#         )
#         self.theme = self.load_theme()
#
#     def load_theme(self):
#         """Charge le thème depuis le fichier de configuration"""
#         try:
#             if os.path.exists(self.config_path):
#                 with open(self.config_path, 'r') as f:
#                     theme = json.load(f)
#                 # Vérifier que toutes les clés nécessaires sont présentes
#                 for key in self.DEFAULT_THEME:
#                     if key not in theme:
#                         theme[key] = self.DEFAULT_THEME[key]
#                 return theme
#         except Exception as e:
#             print(f"Erreur lors du chargement du thème: {e}")
#
#         # Si le chargement échoue, utiliser le thème par défaut
#         return self.DEFAULT_THEME.copy()
#
#     def save_theme(self):
#         """Sauvegarde le thème dans le fichier de configuration"""
#         try:
#             os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
#             with open(self.config_path, 'w') as f:
#                 json.dump(self.theme, f, indent=4)
#             return True
#         except Exception as e:
#             print(f"Erreur lors de la sauvegarde du thème: {e}")
#             return False
#
#     def get_color(self, key):
#         """Récupère une couleur du thème"""
#         return self.theme.get(key, self.DEFAULT_THEME.get(key))
#
#     def set_color(self, key, color):
#         """Définit une couleur dans le thème"""
#         if key in self.theme:
#             self.theme[key] = color
#             return True
#         return False
#
#     def reset_to_default(self):
#         """Réinitialise le thème aux valeurs par défaut"""
#         self.theme = self.DEFAULT_THEME.copy()
#         return self.save_theme()
#
# class DatabaseManager:
#     """Gestion centralisée de la base de données"""
#     def __init__(self, db_name="app_monitor.db"):
#         self.db_path = os.path.join(os.path.expanduser("~"), "AppMonitorData", db_name)
#         os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
#         self._init_db()
#
#     def _get_connection(self):
#         """Établit une connexion à la base de données"""
#         return sqlite3.connect(self.db_path)
#
#     def _init_db(self):
#         """Initialisation des tables"""
#         with self._get_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS applications (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     name TEXT NOT NULL,
#                     executable TEXT NOT NULL UNIQUE,
#                     is_blocked INTEGER DEFAULT 0
#                 )
#             ''')
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS app_usage (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     app_id INTEGER,
#                     start_time TEXT,
#                     end_time TEXT,
#                     duration INTEGER,
#                     FOREIGN KEY(app_id) REFERENCES applications(id)
#                 )
#             ''')
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS scheduled_tasks (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     app_id INTEGER,
#                     action_type TEXT CHECK(action_type IN ('block', 'unblock')),
#                     schedule_type TEXT CHECK(schedule_type IN ('duration', 'datetime')),
#                     duration_hours INTEGER,
#                     duration_minutes INTEGER,
#                     scheduled_time TEXT,
#                     is_completed INTEGER DEFAULT 0,
#                     FOREIGN KEY(app_id) REFERENCES applications(id)
#                 )
#             ''')
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS blocked_sites (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     url TEXT NOT NULL UNIQUE,
#                     is_blocked INTEGER DEFAULT 1
#                 )
#             ''')
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS app_categories (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     name TEXT NOT NULL UNIQUE,
#                     color TEXT NOT NULL,
#                     is_productive INTEGER DEFAULT 1
#                 )
#             ''')
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS app_category_mapping (
#                     app_id INTEGER,
#                     category_id INTEGER,
#                     PRIMARY KEY (app_id, category_id),
#                     FOREIGN KEY(app_id) REFERENCES applications(id),
#                     FOREIGN KEY(category_id) REFERENCES app_categories(id)
#                 )
#             ''')
#             conn.commit()
#
#             # Ajouter des catégories par défaut si elles n'existent pas
#             default_categories = [
#                 ("Travail", "#4CAF50", 1),
#                 ("Études", "#2196F3", 1),
#                 ("Divertissement", "#FF9800", 0),
#                 ("Réseaux sociaux", "#F44336", 0),
#                 ("Productivité", "#9C27B0", 1)
#             ]
#
#             for name, color, is_productive in default_categories:
#                 cursor.execute(
#                     "INSERT OR IGNORE INTO app_categories (name, color, is_productive) VALUES (?, ?, ?)",
#                     (name, color, is_productive)
#                 )
#             conn.commit()
#
#     def execute_query(self, query, params=()):
#         """Exécution sécurisée des requêtes SQL"""
#         try:
#             with self._get_connection() as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(query, params)
#                 conn.commit()
#                 return cursor
#         except sqlite3.Error as e:
#             messagebox.showerror("Database Error", f"Erreur SQLite : {str(e)}")
#             return None
#
# class SiteBlocker:
#     """Gestion du blocage des sites web"""
#     HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts" if platform.system() == "Windows" else "/etc/hosts"
#     TEMP_BACKUP = os.path.join(os.getenv('TEMP', '/tmp'), 'hosts_backup.txt')
#
#     @staticmethod
#     def _run_as_admin():
#         """Relance le programme avec les droits admin"""
#         try:
#             if platform.system() == "Windows":
#                 # Utilisation d'un processus détaché pour éviter la fermeture immédiate
#                 ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
#                 # Attendre un peu pour s'assurer que le nouveau processus démarre
#                 time.sleep(1)
#             else:
#                 os.system(f"sudo {sys.executable} {' '.join(sys.argv)}")
#             sys.exit(0)  # Sortie explicite avec code 0
#         except Exception as e:
#             messagebox.showerror("Erreur d'élévation", f"Impossible d'obtenir les privilèges administrateur: {str(e)}")
#             return False
#
#     @staticmethod
#     def _backup_hosts():
#         """Crée une sauvegarde du fichier hosts"""
#         try:
#             with open(SiteBlocker.HOSTS_PATH, 'r') as f:
#                 content = f.read()
#             with open(SiteBlocker.TEMP_BACKUP, 'w') as f:
#                 f.write(content)
#             return True
#         except Exception as e:
#             messagebox.showerror("Erreur Backup", f"Échec sauvegarde: {str(e)}")
#             return False
#
#     @staticmethod
#     def block_site(url):
#         """Bloque un site avec gestion des droits"""
#         try:
#             # Vérification des droits admin
#             if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
#                 messagebox.showinfo(
#                     "Privilèges requis",
#                     "Le blocage de sites nécessite des privilèges administrateur.\n"
#                     "Une fenêtre de confirmation va s'afficher."
#                 )
#                 if not SiteBlocker._run_as_admin():
#                     return False
#
#             # Validation URL
#             url = url.strip().lower()
#             if not url or ' ' in url:
#                 raise ValueError("URL invalide")
#
#             # Sauvegarde préventive
#             SiteBlocker._backup_hosts()
#
#             # Ajout des entrées
#             with open(SiteBlocker.HOSTS_PATH, 'a') as f:
#                 f.write(f"\n127.0.0.1 {url}\n127.0.0.1 www.{url}\n")
#
#             # Rafraîchissement DNS (Windows uniquement)
#             if platform.system() == "Windows":
#                 subprocess.run(['ipconfig', '/flushdns'], shell=True, check=True)
#
#             print(f"Site {url} bloqué avec succès")
#             return True
#
#         except Exception as e:
#             error_msg = f"Échec du blocage: {str(e)}"
#             print(error_msg)
#             messagebox.showerror("Erreur", error_msg)
#             return False
#
#     @staticmethod
#     def unblock_site(url):
#         """Débloque un site avec restauration si erreur"""
#         try:
#             # Vérification des droits admin
#             if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
#                 if not SiteBlocker._run_as_admin():
#                     return False
#
#             url = url.strip().lower()
#             SiteBlocker._backup_hosts()
#
#             # Filtrage des lignes
#             with open(SiteBlocker.HOSTS_PATH, 'r') as f:
#                 lines = [l for l in f if url not in l and f"www.{url}" not in l]
#
#             # Réécriture
#             with open(SiteBlocker.HOSTS_PATH, 'w') as f:
#                 f.writelines(lines)
#
#             # Rafraîchissement DNS (Windows uniquement)
#             if platform.system() == "Windows":
#                 subprocess.run(['ipconfig', '/flushdns'], shell=True, check=True)
#             return True
#
#         except Exception as e:
#             # Restauration de la sauvegarde
#             if os.path.exists(SiteBlocker.TEMP_BACKUP):
#                 os.replace(SiteBlocker.TEMP_BACKUP, SiteBlocker.HOSTS_PATH)
#             messagebox.showerror("Erreur", f"Échec déblocage: {str(e)}")
#             return False
#
# class AppMonitor(ctk.CTk):
#     """Application principale avec système de monitoring complet"""
#     def __init__(self):
#         super().__init__()
#         self.title("AppMonitor - Contrôle Applications/Sites")
#         self.geometry("1100x750")
#         self.db = DatabaseManager()
#         self.site_blocker = SiteBlocker()
#         self.theme_manager = ThemeManager()
#         self.monitoring_active = True
#         self.current_tab = None
#
#         # Configuration de l'interface
#         self._setup_ui()
#
#         # Démarrer les threads
#         self._start_monitoring_threads()
#
#     def _setup_ui(self):
#         """Configuration complète de l'interface"""
#         self.tab_view = ctk.CTkTabview(self)
#         self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)
#
#         # Onglet Tableau de bord
#         self.tab_dashboard = self.tab_view.add("Tableau de bord")
#         self._setup_dashboard_tab()
#
#         # Onglet Applications
#         self.tab_apps = self.tab_view.add("Applications")
#         self._setup_apps_tab()
#
#         # Onglet Sites Web
#         self.tab_sites = self.tab_view.add("Sites Web")
#         self._setup_sites_tab()
#
#         # Onglet Planification
#         self.tab_schedule = self.tab_view.add("Planification")
#         self._setup_schedule_tab()
#
#         # Onglet Statistiques
#         self.tab_stats = self.tab_view.add("Statistiques")
#         self._setup_stats_tab()
#
#         # Onglet Paramètres
#         self.tab_settings = self.tab_view.add("Paramètres")
#         self._setup_settings_tab()
#
#     def _setup_dashboard_tab(self):
#         """Configuration de l'onglet Tableau de bord"""
#         main_frame = ctk.CTkFrame(self.tab_dashboard)
#         main_frame.pack(expand=True, fill="both", padx=10, pady=10)
#
#         # Configuration du grid pour les cartes de statistiques
#         main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cards")
#         main_frame.grid_rowconfigure(0, weight=0)
#         main_frame.grid_rowconfigure(1, weight=1)
#         main_frame.grid_rowconfigure(2, weight=1)
#
#         # Cartes de statistiques
#         # 1. Temps productif
#         productive_time = self._get_productive_time()
#         if productive_time is not None:
#             hours = int(productive_time // 3600)
#             minutes = int((productive_time % 3600) // 60)
#             productive_display = f"{hours}h {minutes}m"
#         else:
#             productive_display = "0h 0m"
#
#         self._create_stat_card(
#             main_frame, 0, 0, "Temps productif",
#             productive_display,
#             "+12%", self.theme_manager.get_color("positive_change")
#         )
#
#         # 2. Sites bloqués
#         sites_count = self._get_blocked_sites_count()
#         self._create_stat_card(
#             main_frame, 0, 1, "Sites bloqués",
#             f"{sites_count}",
#             "+3", self.theme_manager.get_color("positive_change")
#         )
#
#         # 3. Applications bloquées
#         apps_count = self._get_blocked_apps_count()
#         self._create_stat_card(
#             main_frame, 0, 2, "Applications bloquées",
#             f"{apps_count}",
#             "-2", self.theme_manager.get_color("negative_change")
#         )
#
#         # 4. Concentration
#         concentration = self._calculate_concentration()
#         self._create_stat_card(
#             main_frame, 0, 3, "Concentration",
#             f"{concentration}%",
#             "+7%", self.theme_manager.get_color("positive_change")
#         )
#
#         # Graphique de productivité hebdomadaire
#         if MATPLOTLIB_AVAILABLE:
#             self._create_weekly_chart(main_frame)
#         else:
#             self._create_weekly_chart_placeholder(main_frame)
#
#         # Applications fréquentes
#         self._create_frequent_apps_section(main_frame)
#
#     def _create_stat_card(self, parent, row, col, title, value, change, change_color):
#         """Crée une carte de statistique"""
#         card = ctk.CTkFrame(
#             parent,
#             corner_radius=10,
#             fg_color=self.theme_manager.get_color("card_bg")
#         )
#         card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
#
#         # Titre
#         title_label = ctk.CTkLabel(
#             card,
#             text=title,
#             font=ctk.CTkFont(size=14),
#             text_color=self.theme_manager.get_color("card_subtext")
#         )
#         title_label.pack(anchor="w", padx=15, pady=(15, 5))
#
#         # Valeur
#         value_label = ctk.CTkLabel(
#             card,
#             text=value,
#             font=ctk.CTkFont(size=24, weight="bold"),
#             text_color=self.theme_manager.get_color("card_text")
#         )
#         value_label.pack(anchor="w", padx=15, pady=(0, 5))
#
#         # Changement
#         change_label = ctk.CTkLabel(
#             card,
#             text=change,
#             font=ctk.CTkFont(size=12),
#             text_color=change_color
#         )
#         change_label.pack(anchor="w", padx=15, pady=(0, 15))
#
#     def _create_weekly_chart(self, parent):
#         """Crée le graphique de productivité hebdomadaire"""
#         chart_frame = ctk.CTkFrame(
#             parent,
#             corner_radius=10,
#             fg_color=self.theme_manager.get_color("card_bg")
#         )
#         chart_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
#
#         # Titre
#         title_label = ctk.CTkLabel(
#             chart_frame,
#             text="Votre productivité cette semaine",
#             font=ctk.CTkFont(size=16, weight="bold"),
#             text_color=self.theme_manager.get_color("card_text")
#         )
#         title_label.pack(anchor="w", padx=15, pady=(15, 10))
#
#         # Données pour le graphique
#         days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
#         productive = [3, 4, 3, 5, 4, 2, 2.5]  # Heures productives
#         distractions = [2, 1.5, 2, 1, 1.5, 3, 2.5]  # Heures de distraction
#
#         # Création du graphique avec matplotlib
#         fig, ax = plt.subplots(figsize=(10, 4))
#         fig.patch.set_facecolor('white')
#
#         # Barres empilées
#         ax.bar(days, productive, label='Productif', color=self.theme_manager.get_color("chart_primary"))
#         ax.bar(days, distractions, bottom=productive, label='Distractions', color=self.theme_manager.get_color("chart_secondary"))
#
#         # Personnalisation
#         ax.set_ylabel('Heures')
#         ax.legend()
#         ax.grid(axis='y', linestyle='--', alpha=0.7)
#
#         # Intégration dans l'interface
#         canvas = FigureCanvasTkAgg(fig, master=chart_frame)
#         canvas.draw()
#         canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
#
#     def _create_weekly_chart_placeholder(self, parent):
#         """Crée un placeholder pour le graphique si matplotlib n'est pas disponible"""
#         chart_frame = ctk.CTkFrame(
#             parent,
#             corner_radius=10,
#             fg_color=self.theme_manager.get_color("card_bg")
#         )
#         chart_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
#
#         # Titre
#         title_label = ctk.CTkLabel(
#             chart_frame,
#             text="Votre productivité cette semaine",
#             font=ctk.CTkFont(size=16, weight="bold"),
#             text_color=self.theme_manager.get_color("card_text")
#         )
#         title_label.pack(anchor="w", padx=15, pady=(15, 10))
#
#         # Message d'erreur
#         error_label = ctk.CTkLabel(
#             chart_frame,
#             text="Graphique non disponible - Matplotlib requis",
#             font=ctk.CTkFont(size=14),
#             text_color=self.theme_manager.get_color("card_subtext")
#         )
#         error_label.pack(pady=50)
#
#     def _create_frequent_apps_section(self, parent):
#         """Crée la section des applications fréquentes"""
#         apps_frame = ctk.CTkFrame(
#             parent,
#             corner_radius=10,
#             fg_color=self.theme_manager.get_color("card_bg")
#         )
#         apps_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
#
#         # Titre
#         title_label = ctk.CTkLabel(
#             apps_frame,
#             text="Vos applications fréquentes",
#             font=ctk.CTkFont(size=16, weight="bold"),
#             text_color=self.theme_manager.get_color("card_text")
#         )
#         title_label.pack(anchor="w", padx=15, pady=(15, 10))
#
#         # Liste des applications
#         apps_list = self._get_frequent_apps()
#
#         # Conteneur pour les applications
#         apps_container = ctk.CTkFrame(apps_frame, fg_color="transparent")
#         apps_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
#
#         # Affichage des applications
#         for i, (name, duration) in enumerate(apps_list):
#             app_item = ctk.CTkFrame(
#                 apps_container,
#                 fg_color="#F5F5F5",
#                 corner_radius=5
#             )
#             app_item.pack(fill="x", pady=5)
#
#             # Nom de l'application
#             app_name = ctk.CTkLabel(
#                 app_item,
#                 text=name,
#                 font=ctk.CTkFont(size=14),
#                 text_color=self.theme_manager.get_color("card_text")
#             )
#             app_name.pack(side="left", padx=10, pady=10)
#
#             # Durée d'utilisation
#             if duration is not None:
#                 hours = int(duration // 3600)
#                 minutes = int((duration % 3600) // 60)
#                 duration_text = f"{hours}h {minutes}m"
#             else:
#                 duration_text = "0h 0m"
#
#             app_duration = ctk.CTkLabel(
#                 app_item,
#                 text=duration_text,
#                 font=ctk.CTkFont(size=14),
#                 text_color=self.theme_manager.get_color("card_subtext")
#             )
#             app_duration.pack(side="right", padx=10, pady=10)
#
#     def _get_productive_time(self):
#         """Calcule le temps productif total"""
#         cursor = self.db.execute_query("""
#             SELECT SUM(duration) FROM app_usage
#             JOIN applications ON app_usage.app_id = applications.id
#             JOIN app_category_mapping ON applications.id = app_category_mapping.app_id
#             JOIN app_categories ON app_category_mapping.category_id = app_categories.id
#             WHERE app_categories.is_productive = 1
#             AND start_time >= ?
#         """, (datetime.now().replace(hour=0, minute=0, second=0).isoformat(),))
#
#         if cursor:
#             result = cursor.fetchone()[0]
#             return result if result is not None else 0
#         return 0
#
#     def _get_blocked_sites_count(self):
#         """Compte le nombre de sites bloqués"""
#         cursor = self.db.execute_query(
#             "SELECT COUNT(*) FROM blocked_sites WHERE is_blocked = 1"
#         )
#
#         if cursor:
#             return cursor.fetchone()[0]
#         return 0
#
#     def _get_blocked_apps_count(self):
#         """Compte le nombre d'applications bloquées"""
#         cursor = self.db.execute_query(
#             "SELECT COUNT(*) FROM applications WHERE is_blocked = 1"
#         )
#
#         if cursor:
#             return cursor.fetchone()[0]
#         return 0
#
#     def _calculate_concentration(self):
#         """Calcule le pourcentage de concentration (temps productif / temps total)"""
#         cursor = self.db.execute_query("""
#             SELECT
#                 SUM(CASE WHEN c.is_productive = 1 THEN u.duration ELSE 0 END) as productive,
#                 SUM(u.duration) as total
#             FROM app_usage u
#             JOIN applications a ON u.app_id = a.id
#             LEFT JOIN app_category_mapping m ON a.id = m.app_id
#             LEFT JOIN app_categories c ON m.category_id = c.id
#             WHERE start_time >= ?
#         """, (datetime.now().replace(hour=0, minute=0, second=0).isoformat(),))
#
#         if cursor:
#             result = cursor.fetchone()
#             productive, total = result
#
#             # Vérification que productive et total ne sont pas None
#             if productive is None:
#                 productive = 0
#             if total is None or total == 0:
#                 return 82  # Valeur par défaut si pas de données
#
#             return int((productive / total) * 100)
#
#         return 82  # Valeur par défaut pour la démo
#
#     def _get_frequent_apps(self):
#         """Récupère les applications les plus utilisées"""
#         cursor = self.db.execute_query("""
#             SELECT a.name, SUM(u.duration) as total_duration
#             FROM applications a
#             JOIN app_usage u ON a.id = u.app_id
#             GROUP BY a.name
#             ORDER BY total_duration DESC
#             LIMIT 5
#         """)
#
#         if cursor:
#             return cursor.fetchall()
#
#         # Données d'exemple si aucune donnée n'est disponible
#         return [
#             ("Google Chrome", 7200),
#             ("Visual Studio Code", 5400),
#             ("Microsoft Word", 3600),
#             ("Spotify", 1800),
#             ("Slack", 1200)
#         ]
#
#     def _setup_apps_tab(self):
#         """Configuration de l'onglet Applications"""
#         main_frame = ctk.CTkFrame(self.tab_apps)
#         main_frame.pack(expand=True, fill="both", padx=10, pady=10)
#
#         # Bouton de détection
#         ctk.CTkButton(
#             main_frame,
#             text="🔄 Détecter les applications",
#             command=self._detect_installed_apps,
#             fg_color=self.theme_manager.get_color("success_button"),
#             hover_color=self.theme_manager.get_color("success_button_hover")
#         ).pack(pady=10)
#
#         # En-tête de liste
#         header_frame = ctk.CTkFrame(main_frame)
#         header_frame.pack(fill="x")
#
#         ctk.CTkLabel(
#             header_frame,
#             text="Statut",
#             width=50,
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         ctk.CTkLabel(
#             header_frame,
#             text="Nom",
#             width=200,
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         ctk.CTkLabel(
#             header_frame,
#             text="Catégorie",
#             width=100,
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         ctk.CTkLabel(
#             header_frame,
#             text="Actions",
#             width=150,
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="right", padx=5)
#
#         # Liste scrollable
#         self.apps_list_frame = ctk.CTkScrollableFrame(main_frame)
#         self.apps_list_frame.pack(expand=True, fill="both")
#         self._load_applications()
#
#     def _setup_sites_tab(self):
#         """Configuration de l'onglet Sites Web"""
#         main_frame = ctk.CTkFrame(self.tab_sites)
#         main_frame.pack(expand=True, fill="both", padx=10, pady=10)
#
#         # Frame d'ajout
#         add_frame = ctk.CTkFrame(main_frame)
#         add_frame.pack(fill="x", pady=(0, 10))
#
#         ctk.CTkLabel(
#             add_frame,
#             text="URL du site:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         self.site_url_entry = ctk.CTkEntry(add_frame, placeholder_text="exemple.com")
#         self.site_url_entry.pack(side="left", padx=5, fill="x", expand=True)
#
#         ctk.CTkButton(
#             add_frame,
#             text="Ajouter",
#             command=self._add_site,
#             fg_color=self.theme_manager.get_color("primary_button"),
#             hover_color=self.theme_manager.get_color("primary_button_hover"),
#             width=100
#         ).pack(side="right", padx=5)
#
#         # Liste des sites
#         ctk.CTkLabel(
#             main_frame,
#             text="Sites bloqués:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(anchor="w", pady=(10, 5))
#
#         self.sites_list_frame = ctk.CTkScrollableFrame(main_frame, height=300)
#         self.sites_list_frame.pack(fill="both", expand=True)
#         self._load_blocked_sites()
#
#     def _setup_schedule_tab(self):
#         """Configuration de l'onglet Planification"""
#         main_frame = ctk.CTkFrame(self.tab_schedule)
#         main_frame.pack(expand=True, fill="both", padx=10, pady=10)
#
#         # Sélection d'application
#         app_select_frame = ctk.CTkFrame(main_frame)
#         app_select_frame.pack(fill="x", pady=5)
#
#         ctk.CTkLabel(
#             app_select_frame,
#             text="Application:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         self.app_combobox = ctk.CTkComboBox(app_select_frame, values=self._get_app_names())
#         self.app_combobox.pack(side="left", padx=5, fill="x", expand=True)
#
#         # Sélection d'action
#         action_frame = ctk.CTkFrame(main_frame)
#         action_frame.pack(fill="x", pady=5)
#
#         ctk.CTkLabel(
#             action_frame,
#             text="Action:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         self.action_var = ctk.StringVar(value="block")
#
#         ctk.CTkRadioButton(
#             action_frame,
#             text="Bloquer",
#             variable=self.action_var,
#             value="block",
#             fg_color=self.theme_manager.get_color("primary_button"),
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         ctk.CTkRadioButton(
#             action_frame,
#             text="Débloquer",
#             variable=self.action_var,
#             value="unblock",
#             fg_color=self.theme_manager.get_color("primary_button"),
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         # Type de planification
#         schedule_type_frame = ctk.CTkFrame(main_frame)
#         schedule_type_frame.pack(fill="x", pady=5)
#
#         ctk.CTkLabel(
#             schedule_type_frame,
#             text="Type:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         self.schedule_type_var = ctk.StringVar(value="duration")
#
#         ctk.CTkRadioButton(
#             schedule_type_frame,
#             text="Durée",
#             variable=self.schedule_type_var,
#             value="duration",
#             command=self._toggle_schedule_ui,
#             fg_color=self.theme_manager.get_color("primary_button"),
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         ctk.CTkRadioButton(
#             schedule_type_frame,
#             text="Date/Heure",
#             variable=self.schedule_type_var,
#             value="datetime",
#             command=self._toggle_schedule_ui,
#             fg_color=self.theme_manager.get_color("primary_button"),
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         # Interface durée
#         self.duration_frame = ctk.CTkFrame(main_frame)
#         self.duration_frame.pack(fill="x", pady=5)
#
#         ctk.CTkLabel(
#             self.duration_frame,
#             text="Heures:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         self.hours_entry = ctk.CTkEntry(self.duration_frame, width=50)
#         self.hours_entry.pack(side="left", padx=5)
#         self.hours_entry.insert(0, "0")
#
#         ctk.CTkLabel(
#             self.duration_frame,
#             text="Minutes:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         self.minutes_entry = ctk.CTkEntry(self.duration_frame, width=50)
#         self.minutes_entry.pack(side="left", padx=5)
#         self.minutes_entry.insert(0, "30")
#
#         # Interface date/heure
#         self.datetime_frame = ctk.CTkFrame(main_frame)
#
#         ctk.CTkLabel(
#             self.datetime_frame,
#             text="Date:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         self.date_entry = ctk.CTkEntry(self.datetime_frame, placeholder_text="JJ/MM/AAAA")
#         self.date_entry.pack(side="left", padx=5)
#
#         ctk.CTkLabel(
#             self.datetime_frame,
#             text="Heure:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         self.time_entry = ctk.CTkEntry(self.datetime_frame, placeholder_text="HH:MM")
#         self.time_entry.pack(side="left", padx=5)
#
#         # Bouton de soumission
#         submit_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
#         submit_frame.pack(fill="x", pady=10)
#
#         ctk.CTkButton(
#             submit_frame,
#             text="Planifier",
#             command=self._schedule_action,
#             fg_color=self.theme_manager.get_color("primary_button"),
#             hover_color=self.theme_manager.get_color("primary_button_hover")
#         ).pack(pady=5)
#
#         # Liste des tâches
#         ctk.CTkLabel(
#             main_frame,
#             text="Tâches planifiées:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(anchor="w", pady=5)
#
#         self.scheduled_tasks_frame = ctk.CTkScrollableFrame(main_frame, height=200)
#         self.scheduled_tasks_frame.pack(fill="x", pady=5)
#         self._load_scheduled_tasks()
#
#     def _setup_stats_tab(self):
#         """Configuration de l'onglet Statistiques"""
#         stats_frame = ctk.CTkFrame(self.tab_stats)
#         stats_frame.pack(expand=True, fill="both", padx=10, pady=10)
#
#         ctk.CTkLabel(
#             stats_frame,
#             text="📊 Statistiques d'utilisation",
#             font=("Arial", 16),
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(pady=10)
#
#         # Création des onglets pour différentes périodes
#         tabs = ctk.CTkTabview(stats_frame)
#         tabs.pack(fill="both", expand=True, padx=5, pady=5)
#
#         # Ajout des onglets
#         tabs.add("Aujourd'hui")
#         tabs.add("Cette semaine")
#         tabs.add("Ce mois")
#
#         # Contenu de l'onglet "Aujourd'hui"
#         today_frame = ctk.CTkFrame(tabs.tab("Aujourd'hui"))
#         today_frame.pack(fill="both", expand=True, padx=5, pady=5)
#
#         self.stats_text = ctk.CTkTextbox(
#             today_frame,
#             wrap="word",
#             text_color=self.theme_manager.get_color("card_text")
#         )
#         self.stats_text.pack(expand=True, fill="both")
#         self._update_stats()
#
#         # Contenu des autres onglets
#         if MATPLOTLIB_AVAILABLE:
#             # Contenu de l'onglet "Cette semaine"
#             week_frame = ctk.CTkFrame(tabs.tab("Cette semaine"))
#             week_frame.pack(fill="both", expand=True, padx=5, pady=5)
#
#             # Graphique hebdomadaire
#             fig, ax = plt.subplots(figsize=(10, 6))
#             fig.patch.set_facecolor('white')
#
#             # Données d'exemple
#             days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
#             productive_hours = [4.5, 5.2, 3.8, 6.1, 5.5, 2.0, 1.5]
#
#             ax.bar(days, productive_hours, color=self.theme_manager.get_color("chart_primary"))
#             ax.set_ylabel('Heures productives')
#             ax.set_title('Temps productif par jour')
#             ax.grid(axis='y', linestyle='--', alpha=0.7)
#
#             canvas = FigureCanvasTkAgg(fig, master=week_frame)
#             canvas.draw()
#             canvas.get_tk_widget().pack(fill="both", expand=True)
#
#             # Contenu de l'onglet "Ce mois"
#             month_frame = ctk.CTkFrame(tabs.tab("Ce mois"))
#             month_frame.pack(fill="both", expand=True, padx=5, pady=5)
#
#             # Graphique mensuel
#             fig2, ax2 = plt.subplots(figsize=(10, 6))
#             fig2.patch.set_facecolor('white')
#
#             # Données d'exemple pour les semaines du mois
#             weeks = ["Semaine 1", "Semaine 2", "Semaine 3", "Semaine 4"]
#             productive_hours = [22.5, 25.2, 18.8, 20.1]
#             distraction_hours = [10.2, 8.5, 12.3, 9.8]
#
#             ax2.bar(weeks, productive_hours, label='Productif', color=self.theme_manager.get_color("chart_primary"))
#             ax2.bar(weeks, distraction_hours, bottom=productive_hours, label='Distractions', color=self.theme_manager.get_color("chart_secondary"))
#
#             ax2.set_ylabel('Heures')
#             ax2.set_title('Répartition du temps par semaine')
#             ax2.legend()
#             ax2.grid(axis='y', linestyle='--', alpha=0.7)
#
#             canvas2 = FigureCanvasTkAgg(fig2, master=month_frame)
#             canvas2.draw()
#             canvas2.get_tk_widget().pack(fill="both", expand=True)
#         else:
#             # Placeholders si matplotlib n'est pas disponible
#             for tab_name in ["Cette semaine", "Ce mois"]:
#                 tab_frame = ctk.CTkFrame(tabs.tab(tab_name))
#                 tab_frame.pack(fill="both", expand=True, padx=5, pady=5)
#
#                 ctk.CTkLabel(
#                     tab_frame,
#                     text="Graphiques non disponibles - Matplotlib requis",
#                     font=ctk.CTkFont(size=14),
#                     text_color=self.theme_manager.get_color("card_subtext")
#                 ).pack(pady=50)
#
#     def _setup_settings_tab(self):
#         """Configuration de l'onglet Paramètres"""
#         settings_frame = ctk.CTkFrame(self.tab_settings)
#         settings_frame.pack(expand=True, fill="both", padx=10, pady=10)
#
#         # Titre
#         ctk.CTkLabel(
#             settings_frame,
#             text="⚙️ Paramètres de l'application",
#             font=("Arial", 16),
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(pady=10)
#
#         # Mode d'apparence
#         appearance_frame = ctk.CTkFrame(settings_frame)
#         appearance_frame.pack(fill="x", pady=10, padx=10)
#
#         ctk.CTkLabel(
#             appearance_frame,
#             text="Mode d'apparence:",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=10, pady=10)
#
#         appearance_var = ctk.StringVar(value=ctk.get_appearance_mode())
#         ctk.CTkComboBox(
#             appearance_frame,
#             values=["System", "Light", "Dark"],
#             variable=appearance_var,
#             command=lambda value: ctk.set_appearance_mode(value)
#         ).pack(side="left", padx=10, pady=10)
#
#         # Personnalisation des couleurs
#         colors_frame = ctk.CTkFrame(settings_frame)
#         colors_frame.pack(fill="both", expand=True, pady=10, padx=10)
#
#         ctk.CTkLabel(
#             colors_frame,
#             text="Personnalisation des couleurs",
#             font=("Arial", 14),
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(pady=10)
#
#         # Conteneur scrollable pour les couleurs
#         colors_scroll = ctk.CTkScrollableFrame(colors_frame)
#         colors_scroll.pack(fill="both", expand=True, padx=10, pady=10)
#
#         # Création des sélecteurs de couleur
#         color_items = [
#             ("Couleur principale", "primary_button"),
#             ("Couleur de succès", "success_button"),
#             ("Couleur d'alerte", "danger_button"),
#             ("Couleur neutre", "neutral_button"),
#             ("Couleur de texte principal", "card_text"),
#             ("Couleur de texte secondaire", "card_subtext"),
#             ("Couleur positive", "positive_change"),
#             ("Couleur négative", "negative_change"),
#             ("Couleur graphique primaire", "chart_primary"),
#             ("Couleur graphique secondaire", "chart_secondary")
#         ]
#
#         for i, (label, key) in enumerate(color_items):
#             color_item = ctk.CTkFrame(colors_scroll)
#             color_item.pack(fill="x", pady=5)
#
#             ctk.CTkLabel(
#                 color_item,
#                 text=label,
#                 text_color=self.theme_manager.get_color("card_text"),
#                 width=200
#             ).pack(side="left", padx=10, pady=10)
#
#             # Affichage de la couleur actuelle
#             color_preview = ctk.CTkFrame(
#                 color_item,
#                 fg_color=self.theme_manager.get_color(key),
#                 width=30,
#                 height=30,
#                 corner_radius=5
#             )
#             color_preview.pack(side="left", padx=10, pady=10)
#
#             # Bouton pour changer la couleur
#             ctk.CTkButton(
#                 color_item,
#                 text="Changer",
#                 command=lambda k=key, p=color_preview: self._change_color(k, p),
#                 fg_color=self.theme_manager.get_color("primary_button"),
#                 hover_color=self.theme_manager.get_color("primary_button_hover"),
#                 width=100
#             ).pack(side="right", padx=10, pady=10)
#
#         # Boutons de réinitialisation et sauvegarde
#         buttons_frame = ctk.CTkFrame(settings_frame)
#         buttons_frame.pack(fill="x", pady=10, padx=10)
#
#         ctk.CTkButton(
#             buttons_frame,
#             text="Réinitialiser aux couleurs par défaut",
#             command=self._reset_colors,
#             fg_color=self.theme_manager.get_color("danger_button"),
#             hover_color=self.theme_manager.get_color("danger_button_hover"),
#             width=200
#         ).pack(side="left", padx=10, pady=10)
#
#         ctk.CTkButton(
#             buttons_frame,
#             text="Appliquer les changements",
#             command=self._apply_theme_changes,
#             fg_color=self.theme_manager.get_color("success_button"),
#             hover_color=self.theme_manager.get_color("success_button_hover"),
#             width=200
#         ).pack(side="right", padx=10, pady=10)
#
#     def _change_color(self, key, preview_frame):
#         """Ouvre un sélecteur de couleur et met à jour la couleur"""
#         current_color = self.theme_manager.get_color(key)
#
#         # Convertir la couleur hex en RGB pour le sélecteur
#         r, g, b = self._hex_to_rgb(current_color)
#
#         # Ouvrir le sélecteur de couleur
#         color = colorchooser.askcolor(
#             initialcolor=(r, g, b),
#             title=f"Choisir une couleur pour {key}"
#         )
#
#         if color[1]:  # Si une couleur a été sélectionnée
#             self.theme_manager.set_color(key, color[1])
#             preview_frame.configure(fg_color=color[1])
#
#     def _hex_to_rgb(self, hex_color):
#         """Convertit une couleur hexadécimale en RGB"""
#         hex_color = hex_color.lstrip('#')
#         return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
#
#     def _reset_colors(self):
#         """Réinitialise les couleurs aux valeurs par défaut"""
#         if messagebox.askyesno("Confirmer", "Réinitialiser toutes les couleurs aux valeurs par défaut?"):
#             self.theme_manager.reset_to_default()
#             messagebox.showinfo("Succès", "Les couleurs ont été réinitialisées aux valeurs par défaut")
#             self._setup_settings_tab()  # Rafraîchir la page des paramètres
#
#     def _apply_theme_changes(self):
#         """Applique les changements de thème et redémarre l'interface"""
#         if self.theme_manager.save_theme():
#             messagebox.showinfo("Succès", "Les changements ont été enregistrés")
#             if messagebox.askyesno("Redémarrage", "Voulez-vous redémarrer l'application pour appliquer tous les changements?"):
#                 self.restart_application()
#             else:
#                 # Appliquer certains changements sans redémarrer
#                 self._update_ui_colors()
#         else:
#             messagebox.showerror("Erreur", "Impossible d'enregistrer les changements")
#
#     def _update_ui_colors(self):
#         """Met à jour les couleurs de l'interface sans redémarrer"""
#         # Recréer les onglets pour appliquer les nouvelles couleurs
#         current_tab = self.tab_view.get()
#
#         # Recréer l'interface
#         for widget in self.winfo_children():
#             widget.destroy()
#
#         self._setup_ui()
#
#         # Revenir à l'onglet actif
#         self.tab_view.set(current_tab)
#
#     def restart_application(self):
#         """Redémarre l'application pour appliquer les changements"""
#         self.on_closing(restart=True)
#
#     def _add_site(self):
#         """Ajoute un site à bloquer"""
#         url = self.site_url_entry.get().strip()
#         if not url:
#             messagebox.showerror("Erreur", "Veuillez entrer une URL")
#             return
#
#         try:
#             # Ajout à la base de données
#             self.db.execute_query(
#                 "INSERT OR IGNORE INTO blocked_sites (url) VALUES (?)",
#                 (url,)
#             )
#
#             # Blocage effectif
#             if self.site_blocker.block_site(url):
#                 messagebox.showinfo("Succès", f"Site {url} bloqué avec succès!")
#                 self._load_blocked_sites()
#                 self.site_url_entry.delete(0, "end")
#             else:
#                 # Si le blocage a échoué, supprimer de la base
#                 self.db.execute_query(
#                     "DELETE FROM blocked_sites WHERE url = ?",
#                     (url,)
#                 )
#
#         except Exception as e:
#             messagebox.showerror("Erreur", f"Échec d'ajout : {str(e)}")
#
#     def _load_blocked_sites(self):
#         """Charge la liste des sites bloqués"""
#         for widget in self.sites_list_frame.winfo_children():
#             widget.destroy()
#
#         cursor = self.db.execute_query(
#             "SELECT id, url FROM blocked_sites WHERE is_blocked = 1"
#         )
#
#         if cursor:
#             sites = cursor.fetchall()
#             if not sites:
#                 ctk.CTkLabel(
#                     self.sites_list_frame,
#                     text="Aucun site bloqué",
#                     font=ctk.CTkFont(size=14),
#                     text_color=self.theme_manager.get_color("card_subtext")
#                 ).pack(pady=20)
#                 return
#
#             for site_id, url in sites:
#                 self._add_site_to_list(site_id, url)
#         else:
#             ctk.CTkLabel(
#                 self.sites_list_frame,
#                 text="Aucun site bloqué",
#                 font=ctk.CTkFont(size=14),
#                 text_color=self.theme_manager.get_color("card_subtext")
#             ).pack(pady=20)
#
#     def _add_site_to_list(self, site_id, url):
#         """Ajoute un site à la liste avec style moderne"""
#         site_frame = ctk.CTkFrame(self.sites_list_frame)
#         site_frame.pack(fill="x", pady=2)
#
#         # URL
#         ctk.CTkLabel(
#             site_frame,
#             text=url,
#             width=400,
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         # Boutons d'action
#         action_frame = ctk.CTkFrame(site_frame, fg_color="transparent")
#         action_frame.pack(side="right")
#
#         ctk.CTkButton(
#             action_frame,
#             text="Débloquer",
#             fg_color=self.theme_manager.get_color("success_button"),
#             hover_color=self.theme_manager.get_color("success_button_hover"),
#             width=80,
#             command=lambda: self._toggle_site_block(site_id, url)
#         ).pack(side="left", padx=2)
#
#         ctk.CTkButton(
#             action_frame,
#             text="🗑️",
#             width=40,
#             fg_color=self.theme_manager.get_color("neutral_button"),
#             hover_color=self.theme_manager.get_color("neutral_button_hover"),
#             command=lambda: self._delete_site(site_id, url)
#         ).pack(side="left", padx=2)
#
#     def _toggle_site_block(self, site_id, url):
#         """Bascule le statut de blocage d'un site"""
#         if messagebox.askyesno("Confirmer", f"Débloquer le site {url}?"):
#             if self.site_blocker.unblock_site(url):
#                 self.db.execute_query(
#                     "UPDATE blocked_sites SET is_blocked = 0 WHERE id = ?",
#                     (site_id,)
#                 )
#                 self._load_blocked_sites()
#                 messagebox.showinfo("Succès", f"Site {url} débloqué!")
#             else:
#                 messagebox.showerror("Erreur", "Échec du déblocage")
#
#     def _delete_site(self, site_id, url):
#         """Supprime un site de la liste"""
#         if messagebox.askyesno("Confirmer", f"Supprimer le site {url}?"):
#             # Débloquer d'abord si nécessaire
#             cursor = self.db.execute_query(
#                 "SELECT is_blocked FROM blocked_sites WHERE id = ?",
#                 (site_id,)
#             )
#             if cursor and cursor.fetchone()[0] == 1:
#                 self.site_blocker.unblock_site(url)
#
#             # Supprimer de la base
#             self.db.execute_query(
#                 "DELETE FROM blocked_sites WHERE id = ?",
#                 (site_id,)
#             )
#             self._load_blocked_sites()
#
#     def _detect_installed_apps(self):
#         """Détection automatique des applications installées"""
#         try:
#             detected = False
#
#             # Méthode 1: Logiciels installés via winapps
#             if WINAPPS_AVAILABLE:
#                 for app in winapps.list_installed():
#                     try:
#                         if app.install_location:
#                             exe_name = app.name + ".exe"
#                             exe_path = os.path.join(app.install_location, exe_name)
#                             if os.path.exists(exe_path):
#                                 self.db.execute_query(
#                                     "INSERT OR IGNORE INTO applications (name, executable) VALUES (?, ?)",
#                                     (app.name, exe_path)
#                                 )
#                                 detected = True
#                     except Exception:
#                         continue
#
#             # Méthode 2: Processus en cours via WMI
#             if WMI_AVAILABLE:
#                 c = wmi.WMI()
#                 for process in c.Win32_Process():
#                     try:
#                         if process.ExecutablePath and not any(
#                                 x in process.ExecutablePath.lower()
#                                 for x in ["\\windows\\", "\\microsoft\\"]
#                         ):
#                             self.db.execute_query(
#                                 "INSERT OR IGNORE INTO applications (name, executable) VALUES (?, ?)",
#                                 (process.Name, process.ExecutablePath)
#                             )
#                             detected = True
#                     except Exception:
#                         continue
#
#             # Méthode 3: Processus en cours via psutil (plus portable)
#             for proc in psutil.process_iter(['pid', 'name', 'exe']):
#                 try:
#                     process_info = proc.info
#                     if process_info['exe'] and not any(
#                             x in process_info['exe'].lower()
#                             for x in ["\\windows\\", "\\microsoft\\", "/usr/bin/", "/bin/"]
#                     ):
#                         self.db.execute_query(
#                             "INSERT OR IGNORE INTO applications (name, executable) VALUES (?, ?)",
#                             (process_info['name'], process_info['exe'])
#                         )
#                         detected = True
#                 except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#                     continue
#
#             self._load_applications()
#
#             if detected:
#                 messagebox.showinfo("Succès", "Détection terminée!")
#             else:
#                 messagebox.showinfo("Information", "Aucune nouvelle application détectée.")
#
#         except Exception as e:
#             messagebox.showerror("Erreur", f"Échec de détection : {str(e)}")
#
#     def _load_applications(self):
#         """Chargement des applications dans l'interface"""
#         for widget in self.apps_list_frame.winfo_children():
#             widget.destroy()
#
#         cursor = self.db.execute_query("""
#             SELECT a.id, a.name, a.is_blocked, c.name as category_name, c.color
#             FROM applications a
#             LEFT JOIN app_category_mapping m ON a.id = m.app_id
#             LEFT JOIN app_categories c ON m.category_id = c.id
#         """)
#
#         if cursor:
#             apps = cursor.fetchall()
#             if not apps:
#                 ctk.CTkLabel(
#                     self.apps_list_frame,
#                     text="Aucune application détectée",
#                     font=ctk.CTkFont(size=14),
#                     text_color=self.theme_manager.get_color("card_subtext")
#                 ).pack(pady=20)
#                 return
#
#             for app_data in apps:
#                 app_id, name, is_blocked = app_data[0], app_data[1], app_data[2]
#                 category_name = app_data[3] if app_data[3] else "Non catégorisé"
#                 category_color = app_data[4] if app_data[4] else "#CCCCCC"
#                 self._add_app_to_list(app_id, name, is_blocked, category_name, category_color)
#         else:
#             ctk.CTkLabel(
#                 self.apps_list_frame,
#                 text="Aucune application détectée",
#                 font=ctk.CTkFont(size=14),
#                 text_color=self.theme_manager.get_color("card_subtext")
#             ).pack(
#                 text_color=self.theme_manager.get_color("card_subtext")
#             ).pack(pady=20)
#
#     def _add_app_to_list(self, app_id, name, is_blocked, category_name, category_color):
#         """Ajout d'une application à la liste avec style moderne"""
#         app_frame = ctk.CTkFrame(self.apps_list_frame)
#         app_frame.pack(fill="x", pady=2)
#
#         # Statut + Nom
#         status_icon = "⛔" if is_blocked else "✅"
#         ctk.CTkLabel(
#             app_frame,
#             text=status_icon,
#             width=50,
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         ctk.CTkLabel(
#             app_frame,
#             text=name,
#             width=200,
#             anchor="w",
#             text_color=self.theme_manager.get_color("card_text")
#         ).pack(side="left", padx=5)
#
#         # Catégorie avec couleur
#         category_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
#         category_frame.pack(side="left", padx=5)
#
#         category_indicator = ctk.CTkFrame(
#             category_frame,
#             fg_color=category_color,
#             width=15,
#             height=15,
#             corner_radius=7
#         )
#         category_indicator.pack(side="left", padx=5)
#
#         ctk.CTkLabel(
#             category_frame,
#             text=category_name,
#             font=ctk.CTkFont(size=12),
#             text_color=self.theme_manager.get_color("card_subtext")
#         ).pack(side="left")
#
#         # Boutons d'action
#         action_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
#         action_frame.pack(side="right")
#
#         ctk.CTkButton(
#             action_frame,
#             text="Débloquer" if is_blocked else "Bloquer",
#             fg_color=self.theme_manager.get_color("success_button") if is_blocked else self.theme_manager.get_color("danger_button"),
#             hover_color=self.theme_manager.get_color("success_button_hover") if is_blocked else self.theme_manager.get_color("danger_button_hover"),
#             width=80,
#             command=lambda: self._toggle_app_block(app_id)
#         ).pack(side="left", padx=2)
#
#         # Bouton de catégorie
#         ctk.CTkButton(
#             action_frame,
#             text="Catégorie",
#             fg_color=self.theme_manager.get_color("primary_button"),
#             hover_color=self.theme_manager.get_color("primary_button_hover"),
#             width=80,
#             command=lambda: self._set_app_category(app_id, name)
#         ).pack(side="left", padx=2)
#
#         ctk.CTkButton(
#             action_frame,
#             text="🗑️",
#             width=40,
#             fg_color=self.theme_manager.get_color("neutral_button"),
#             hover_color=self.theme_manager.get_color("neutral_button_hover"),
#             command=lambda: self._delete_application(app_id)
#         ).pack(side="left", padx=2)
#
#     def _set_app_category(self, app_id, app_name):
#         """Ouvre une fenêtre pour définir la catégorie de l'application"""
#         category_window = ctk.CTkToplevel(self)
#         category_window.title(f"Catégorie pour {app_name}")
#         category_window.geometry("400x300")
#         category_window.transient(self)
#         category_window.grab_set()
#
#         # Récupérer les catégories
#         cursor = self.db.execute_query("SELECT id, name, color FROM app_categories")
#         categories = cursor.fetchall() if cursor else []
#
#         # Récupérer la catégorie actuelle
#         cursor = self.db.execute_query("""
#             SELECT category_id FROM app_category_mapping
#             WHERE app_id = ?
#         """, (app_id,))
#         current_category = cursor.fetchone()[0] if cursor and cursor.fetchone() else None
#
#         # Variable pour stocker la sélection
#         selected_category = ctk.IntVar(value=current_category if current_category else 0)
#
#         # Frame pour les catégories
#         categories_frame = ctk.CTkScrollableFrame(category_window)
#         categories_frame.pack(fill="both", expand=True, padx=20, pady=20)
#
#         # Option "Aucune catégorie"
#         none_frame = ctk.CTkFrame(categories_frame, fg_color="transparent")
#         none_frame.pack(fill="x", pady=5)
#
#         ctk.CTkRadioButton(
#             none_frame,
#             text="Aucune catégorie",
#             variable=selected_category,
#             value=0,
#             fg_color=self.theme_manager.get_color("primary_button")
#         ).pack(side="left", padx=10)
#
#         # Liste des catégories
#         for cat_id, cat_name, cat_color in categories:
#             cat_frame = ctk.CTkFrame(categories_frame, fg_color="transparent")
#             cat_frame.pack(fill="x", pady=5)
#
#             ctk.CTkRadioButton(
#                 cat_frame,
#                 text=cat_name,
#                 variable=selected_category,
#                 value=cat_id,
#                 fg_color=self.theme_manager.get_color("primary_button")
#             ).pack(side="left", padx=10)
#
#             color_indicator = ctk.CTkFrame(
#                 cat_frame,
#                 fg_color=cat_color,
#                 width=15,
#                 height=15,
#                 corner_radius=7
#             )
#             color_indicator.pack(side="left", padx=5)
#
#         # Boutons d'action
#         buttons_frame = ctk.CTkFrame(category_window, fg_color="transparent")
#         buttons_frame.pack(fill="x", padx=20, pady=10)
#
#         ctk.CTkButton(
#             buttons_frame,
#             text="Annuler",
#             command=category_window.destroy,
#             fg_color=self.theme_manager.get_color("neutral_button"),
#             hover_color=self.theme_manager.get_color("neutral_button_hover"),
#             width=100
#         ).pack(side="left", padx=10)
#
#         ctk.CTkButton(
#             buttons_frame,
#             text="Appliquer",
#             command=lambda: self._apply_category(app_id, selected_category.get(), category_window),
#             fg_color=self.theme_manager.get_color("primary_button"),
#             hover_color=self.theme_manager.get_color("primary_button_hover"),
#             width=100
#         ).pack(side="right", padx=10)
#
#     def _apply_category(self, app_id, category_id, window):
#         """Applique la catégorie sélectionnée à l'application"""
#         try:
#             # Supprimer les mappings existants
#             self.db.execute_query(
#                 "DELETE FROM app_category_mapping WHERE app_id = ?",
#                 (app_id,)
#             )
#
#             # Ajouter le nouveau mapping si une catégorie est sélectionnée
#             if category_id > 0:
#                 self.db.execute_query(
#                     "INSERT INTO app_category_mapping (app_id, category_id) VALUES (?, ?)",
#                     (app_id, category_id)
#                 )
#
#             window.destroy()
#             self._load_applications()
#
#         except Exception as e:
#             messagebox.showerror("Erreur", f"Échec de l'application de la catégorie: {str(e)}")
#
#     def _toggle_app_block(self, app_id):
#         """Basculement du statut de blocage"""
#         cursor = self.db.execute_query(
#             "SELECT is_blocked FROM applications WHERE id = ?",
#             (app_id,)
#         )
#
#         if cursor:
#             current_status = cursor.fetchone()[0]
#             new_status = 0 if current_status else 1
#
#             self.db.execute_query(
#                 "UPDATE applications SET is_blocked = ? WHERE id = ?",
#                 (new_status, app_id)
#             )
#             self._load_applications()
#
#     def _delete_application(self, app_id):
#         """Suppression d'une application"""
#         if messagebox.askyesno("Confirmer", "Supprimer cette application?"):
#             # Supprimer les mappings de catégorie
#             self.db.execute_query(
#                 "DELETE FROM app_category_mapping WHERE app_id = ?",
#                 (app_id,)
#             )
#
#             # Supprimer l'application
#             self.db.execute_query(
#                 "DELETE FROM applications WHERE id = ?",
#                 (app_id,)
#             )
#             self._load_applications()
#
#     def _toggle_schedule_ui(self):
#         """Bascule entre les interfaces durée et date/heure"""
#         if self.schedule_type_var.get() == "duration":
#             self.datetime_frame.pack_forget()
#             self.duration_frame.pack(fill="x", pady=5)
#         else:
#             self.duration_frame.pack_forget()
#             self.datetime_frame.pack(fill="x", pady=5)
#
#     def _get_app_names(self):
#         """Récupération des noms d'applications"""
#         cursor = self.db.execute_query("SELECT name FROM applications")
#         if cursor:
#             app_names = [row[0] for row in cursor.fetchall()]
#             return app_names if app_names else ["Aucune application"]
#         return ["Aucune application"]
#
#     def _get_app_id_by_name(self, name):
#         """Récupération de l'ID par nom avec gestion robuste des erreurs"""
#         cursor = self.db.execute_query("SELECT id FROM applications WHERE name = ?", (name,))
#         if cursor:
#             result = cursor.fetchone()
#             return result[0] if result else None
#         return None
#
#     def _schedule_action(self):
#         """Planification d'une action avec vérification améliorée des entrées"""
#         app_name = self.app_combobox.get()
#         if not app_name or app_name == "Aucune application":
#             messagebox.showerror("Erreur", "Sélectionnez une application")
#             return
#
#         app_id = self._get_app_id_by_name(app_name)
#         if app_id is None:
#             messagebox.showerror("Erreur", "Application introuvable")
#             return
#
#         action_type = self.action_var.get()
#         schedule_type = self.schedule_type_var.get()
#
#         if schedule_type == "duration":
#             try:
#                 hours = int(self.hours_entry.get() or 0)
#                 minutes = int(self.minutes_entry.get() or 0)
#
#                 if hours == 0 and minutes == 0:
#                     messagebox.showerror("Erreur", "Durée invalide")
#                     return
#
#                 scheduled_time = (datetime.now() + timedelta(hours=hours, minutes=minutes)).isoformat()
#
#                 self.db.execute_query(
#                     """INSERT INTO scheduled_tasks
#                     (app_id, action_type, schedule_type, duration_hours, duration_minutes, scheduled_time)
#                     VALUES (?, ?, ?, ?, ?, ?)""",
#                     (app_id, action_type, schedule_type, hours, minutes, scheduled_time)
#                 )
#
#                 messagebox.showinfo("Succès", f"Action dans {hours}h{minutes}m")
#                 self._load_scheduled_tasks()
#
#             except ValueError:
#                 messagebox.showerror("Erreur", "Valeurs numériques requises")
#
#         else:  # datetime
#             date_str = self.date_entry.get()
#             time_str = self.time_entry.get()
#
#             try:
#                 day, month, year = map(int, date_str.split('/'))
#                 hour, minute = map(int, time_str.split(':'))
#                 scheduled_time = datetime(year, month, day, hour, minute).isoformat()
#
#                 if scheduled_time <= datetime.now().isoformat():
#                     messagebox.showerror("Erreur", "Date/heure future requise")
#                     return
#
#                 self.db.execute_query(
#                     """INSERT INTO scheduled_tasks
#                     (app_id, action_type, schedule_type, scheduled_time)
#                     VALUES (?, ?, ?, ?)""",
#                     (app_id, action_type, schedule_type, scheduled_time)
#                 )
#
#                 messagebox.showinfo("Succès", f"Action le {date_str} à {time_str}")
#                 self._load_scheduled_tasks()
#
#             except Exception as e:
#                 messagebox.showerror("Erreur", f"Format invalide : JJ/MM/AAAA et HH:MM\n{str(e)}")
#
#     def _load_scheduled_tasks(self):
#         """Chargement des tâches planifiées avec style moderne"""
#         for widget in self.scheduled_tasks_frame.winfo_children():
#             widget.destroy()
#
#         cursor = self.db.execute_query("""
#             SELECT t.id, a.name, t.action_type, t.schedule_type,
#                    t.duration_hours, t.duration_minutes, t.scheduled_time
#             FROM scheduled_tasks t
#             JOIN applications a ON t.app_id = a.id
#             WHERE t.is_completed = 0
#             ORDER BY t.scheduled_time
#         """)
#
#         if cursor:
#             tasks = cursor.fetchall()
#             if not tasks:
#                 ctk.CTkLabel(
#                     self.scheduled_tasks_frame,
#                     text="Aucune tâche planifiée",
#                     font=ctk.CTkFont(size=14),
#                     text_color=self.theme_manager.get_color("card_subtext")
#                 ).pack(pady=20)
#                 return
#
#             for task_id, app_name, action_type, schedule_type, hours, minutes, scheduled_time in tasks:
#                 task_frame = ctk.CTkFrame(self.scheduled_tasks_frame)
#                 task_frame.pack(fill="x", pady=2)
#
#                 if schedule_type == "duration":
#                     info_text = f"{app_name} - {action_type} dans {hours}h{minutes}m"
#                 else:
#                     dt = datetime.fromisoformat(scheduled_time)
#                     info_text = f"{app_name} - {action_type} le {dt.strftime('%d/%m/%Y à %H:%M')}"
#
#                 ctk.CTkLabel(
#                     task_frame,
#                     text=info_text,
#                     width=400,
#                     text_color=self.theme_manager.get_color("card_text")
#                 ).pack(side="left", padx=5)
#
#                 ctk.CTkButton(
#                     task_frame,
#                     text="Annuler",
#                     fg_color=self.theme_manager.get_color("danger_button"),
#                     hover_color=self.theme_manager.get_color("danger_button_hover"),
#                     width=80,
#                     command=lambda id=task_id: self._cancel_scheduled_task(id)
#                 ).pack(side="right", padx=5)
#         else:
#             ctk.CTkLabel(
#                 self.scheduled_tasks_frame,
#                 text="Aucune tâche planifiée",
#                 font=ctk.CTkFont(size=14),
#                 text_color=self.theme_manager.get_color("card_subtext")
#             ).pack(pady=20)
#
#     def _cancel_scheduled_task(self, task_id):
#         """Annulation d'une tâche planifiée"""
#         if messagebox.askyesno("Confirmer", "Annuler cette tâche?"):
#             self.db.execute_query(
#                 "DELETE FROM scheduled_tasks WHERE id = ?",
#                 (task_id,)
#             )
#             self._load_scheduled_tasks()
#
#     def _check_scheduled_tasks(self):
#         """Vérification des tâches à exécuter"""
#         while self.monitoring_active:
#             try:
#                 cursor = self.db.execute_query("""
#                     SELECT id, app_id, action_type
#                     FROM scheduled_tasks
#                     WHERE scheduled_time <= ? AND is_completed = 0
#                 """, (datetime.now().isoformat(),))
#
#                 if cursor:
#                     for task_id, app_id, action_type in cursor.fetchall():
#                         # Exécution de l'action
#                         self.db.execute_query(
#                             "UPDATE applications SET is_blocked = ? WHERE id = ?",
#                             (1 if action_type == "block" else 0, app_id)
#                         )
#
#                         # Marquage comme complété
#                         self.db.execute_query(
#                             "UPDATE scheduled_tasks SET is_completed = 1 WHERE id = ?",
#                             (task_id,)
#                         )
#
#                         # Mise à jour de l'interface
#                         self.after(0, self._load_applications)
#                         self.after(0, self._load_scheduled_tasks)
#
#             except Exception as e:
#                 print(f"Erreur vérification tâches : {str(e)}")
#
#             time.sleep(10)
#
#     def _update_stats(self):
#         """Mise à jour des statistiques"""
#         cursor = self.db.execute_query("""
#             SELECT a.name, SUM(u.duration), COUNT(u.id)
#             FROM applications a
#             LEFT JOIN app_usage u ON a.id = u.app_id
#             GROUP BY a.name
#             ORDER BY SUM(u.duration) DESC
#         """)
#
#         if cursor:
#             self.stats_text.delete("1.0", "end")
#             self.stats_text.insert("end", "Temps cumulé par application:\n\n")
#
#             for name, duration, count in cursor.fetchall():
#                 if duration:
#                     hours = int(duration // 3600)
#                     mins = int((duration % 3600) // 60)
#                     self.stats_text.insert("end", f"• {name}: {hours}h{mins}m ({count} sessions)\n")
#                 else:
#                     self.stats_text.insert("end", f"• {name}: Aucune utilisation\n")
#
#     def _monitor_apps(self):
#         """Surveillance des applications en temps réel"""
#         tracked_processes = {}
#
#         while self.monitoring_active:
#             try:
#                 self._check_blocked_apps()
#                 self._track_app_usage(tracked_processes)
#
#                 if int(time.time()) % 30 == 0:
#                     self._update_stats()
#
#             except Exception as e:
#                 print(f"Erreur monitoring : {str(e)}")
#             time.sleep(5)
#
#     def _check_blocked_apps(self):
#         """Vérification et fermeture des applications bloquées"""
#         cursor = self.db.execute_query(
#             "SELECT executable FROM applications WHERE is_blocked = 1"
#         )
#
#         if cursor:
#             for exe_path in [x[0] for x in cursor.fetchall()]:
#                 for process in psutil.process_iter(['pid', 'exe']):
#                     try:
#                         if process.info['exe'] and exe_path.lower() in process.info['exe'].lower():
#                             psutil.Process(process.info['pid']).kill()
#                     except:
#                         continue
#
#     def _track_app_usage(self, tracked_processes):
#         """Suivi de l'utilisation des applications"""
#         current_time = datetime.now().isoformat()
#
#         cursor = self.db.execute_query(
#             "SELECT id, executable FROM applications WHERE is_blocked = 0"
#         )
#
#         if cursor:
#             apps = {exe: id for id, exe in cursor.fetchall()}
#
#             # Détection des processus en cours
#             running = {}
#             for p in psutil.process_iter(['pid', 'exe']):
#                 if p.info['exe'] and p.info['exe'] in apps:
#                     running[p.info['exe']] = p.info['pid']
#
#             # Nouveaux processus
#             for exe, pid in running.items():
#                 if exe not in tracked_processes:
#                     self.db.execute_query(
#                         "INSERT INTO app_usage (app_id, start_time) VALUES (?, ?)",
#                         (apps[exe], current_time)
#                     )
#                     tracked_processes[exe] = (pid, current_time)
#
#             # Processus terminés
#             for exe in list(tracked_processes.keys()):
#                 if exe not in running:
#                     pid, start = tracked_processes[exe]
#                     duration = (datetime.now() - datetime.fromisoformat(start)).total_seconds()
#
#                     self.db.execute_query(
#                         """UPDATE app_usage SET end_time = ?, duration = ?
#                         WHERE app_id = ? AND end_time IS NULL""",
#                         (current_time, duration, apps[exe])
#                     )
#                     del tracked_processes[exe]
#
#     def _start_monitoring_threads(self):
#         """Lancement des threads de surveillance"""
#         self.monitor_thread = threading.Thread(
#             target=self._monitor_apps,
#             daemon=True,
#             name="AppMonitorThread"
#         )
#         self.monitor_thread.start()
#
#         self.task_checker_thread = threading.Thread(
#             target=self._check_scheduled_tasks,
#             daemon=True,
#             name="TaskCheckerThread"
#         )
#         self.task_checker_thread.start()
#
#     def on_closing(self, restart=False):
#         """Nettoyage avant fermeture"""
#         self.monitoring_active = False
#         if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
#             self.monitor_thread.join(timeout=1)
#         if hasattr(self, 'task_checker_thread') and self.task_checker_thread.is_alive():
#             self.task_checker_thread.join(timeout=1)
#
#         self.destroy()
#
#         if restart:
#             os.execl(sys.executable, sys.executable, *sys.argv)
#
# if __name__ == "__main__":
#     # Vérification des privilèges admin pour Windows
#     if platform.system() == "Windows":
#         try:
#             is_admin = ctypes.windll.shell32.IsUserAnAdmin()
#             if not is_admin:
#                 print("Demande d'élévation des privilèges administrateur...")
#                 # Afficher un message avant de demander l'élévation
#                 messagebox.showinfo(
#                     "Privilèges administrateur",
#                     "L'application nécessite des privilèges administrateur pour fonctionner correctement.\n"
#                     "Une fenêtre de confirmation va s'afficher."
#                 )
#                 ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
#                 sys.exit(0)
#             else:
#                 print("Exécution avec privilèges administrateur.")
#         except Exception as e:
#             print(f"Erreur lors de la vérification des privilèges admin: {e}")
#             messagebox.showwarning(
#                 "Avertissement",
#                 "L'application fonctionne sans privilèges administrateur.\n"
#                 "Certaines fonctionnalités comme le blocage de sites peuvent ne pas fonctionner."
#             )
#
#     # Ajout d'un gestionnaire d'exceptions global
#     def exception_handler(exc_type, exc_value, exc_traceback):
#         """Gestionnaire d'exceptions global pour capturer les erreurs non gérées"""
#         error_msg = f"Une erreur non gérée s'est produite:\n{exc_type.__name__}: {exc_value}"
#         print(error_msg)
#         try:
#             messagebox.showerror("Erreur critique", error_msg)
#         except:
#             pass  # Si la messagebox échoue aussi
#         return sys.__excepthook__(exc_type, exc_value, exc_traceback)
#
#     # Installer le gestionnaire d'exceptions
#     sys.excepthook = exception_handler
#
#     # Démarrer l'application
#     app = AppMonitor()
#     app.protocol("WM_DELETE_WINDOW", app.on_closing)
#     app.mainloop()
