import os
import sys
import threading
import time
from datetime import datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox, colorchooser

from app.core.database import DatabaseManager
from app.core.theme import ThemeManager
from app.core.site_blocker import SiteBlocker
from app.utils.app_monitor import AppMonitoring
from app.utils.helpers import hex_to_rgb, format_duration

from app.ui.tabs.dashboard_tab import setup_dashboard_tab
from app.ui.tabs.apps_tab import setup_apps_tab, load_applications
from app.ui.tabs.sites_tab import setup_sites_tab, load_blocked_sites
from app.ui.tabs.schedule_tab import setup_schedule_tab, load_scheduled_tasks
from app.ui.tabs.stats_tab import setup_stats_tab, update_stats
from app.ui.tabs.settings_tab import setup_settings_tab

class AppMonitor(ctk.CTk):
    """Application principale avec système de monitoring complet"""
    def __init__(self):
        super().__init__()
        self.title("AppMonitor - Contrôle Applications/Sites")
        self.geometry("1100x750")
        self.db = DatabaseManager()
        self.site_blocker = SiteBlocker()
        self.theme_manager = ThemeManager()
        self.monitoring_active = True
        self.current_tab = None
        self.tracked_processes = {}

        # Configuration de l'interface
        self._setup_ui()

        # Démarrer les threads
        self._start_monitoring_threads()

    def _setup_ui(self):
        """Configuration complète de l'interface"""
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

        # Onglet Tableau de bord
        self.tab_dashboard = self.tab_view.add("Tableau de bord")
        setup_dashboard_tab(self)

        # Onglet Applications
        self.tab_apps = self.tab_view.add("Applications")
        setup_apps_tab(self)

        # Onglet Sites Web
        self.tab_sites = self.tab_view.add("Sites Web")
        setup_sites_tab(self)

        # Onglet Planification
        self.tab_schedule = self.tab_view.add("Planification")
        setup_schedule_tab(self)

        # Onglet Statistiques
        self.tab_stats = self.tab_view.add("Statistiques")
        setup_stats_tab(self)
        
        # Onglet Paramètres
        self.tab_settings = self.tab_view.add("Paramètres")
        setup_settings_tab(self)

    def _monitor_apps(self):
        """Surveillance des applications en temps réel"""
        while self.monitoring_active:
            try:
                AppMonitoring.check_blocked_apps(self.db)
                AppMonitoring.track_app_usage(self.db, self.tracked_processes)

                if int(time.time()) % 30 == 0:
                    self.after(0, lambda: update_stats(self))

            except Exception as e:
                print(f"Erreur monitoring : {str(e)}")
            time.sleep(5)

    def _check_scheduled_tasks(self):
        """Vérification des tâches à exécuter"""
        while self.monitoring_active:
            try:
                cursor = self.db.execute_query("""
                    SELECT id, app_id, action_type 
                    FROM scheduled_tasks 
                    WHERE scheduled_time <= ? AND is_completed = 0
                """, (datetime.now().isoformat(),))

                if cursor:
                    for task_id, app_id, action_type in cursor.fetchall():
                        # Exécution de l'action
                        self.db.execute_query(
                            "UPDATE applications SET is_blocked = ? WHERE id = ?",
                            (1 if action_type == "block" else 0, app_id)
                        )

                        # Marquage comme complété
                        self.db.execute_query(
                            "UPDATE scheduled_tasks SET is_completed = 1 WHERE id = ?",
                            (task_id,)
                        )

                        # Mise à jour de l'interface
                        self.after(0, lambda: load_applications(self))
                        self.after(0, lambda: load_scheduled_tasks(self))

            except Exception as e:
                print(f"Erreur vérification tâches : {str(e)}")

            time.sleep(10)

    def _start_monitoring_threads(self):
        """Lancement des threads de surveillance"""
        self.monitor_thread = threading.Thread(
            target=self._monitor_apps,
            daemon=True,
            name="AppMonitorThread"
        )
        self.monitor_thread.start()

        self.task_checker_thread = threading.Thread(
            target=self._check_scheduled_tasks,
            daemon=True,
            name="TaskCheckerThread"
        )
        self.task_checker_thread.start()

    def change_color(self, key, preview_frame):
        """Ouvre un sélecteur de couleur et met à jour la couleur"""
        current_color = self.theme_manager.get_color(key)
        
        # Convertir la couleur hex en RGB pour le sélecteur
        r, g, b = hex_to_rgb(current_color)
        
        # Ouvrir le sélecteur de couleur
        color = colorchooser.askcolor(
            initialcolor=(r, g, b),
            title=f"Choisir une couleur pour {key}"
        )
        
        if color[1]:  # Si une couleur a été sélectionnée
            self.theme_manager.set_color(key, color[1])
            preview_frame.configure(fg_color=color[1])

    def reset_colors(self):
        """Réinitialise les couleurs aux valeurs par défaut"""
        if messagebox.askyesno("Confirmer", "Réinitialiser toutes les couleurs aux valeurs par défaut?"):
            self.theme_manager.reset_to_default()
            messagebox.showinfo("Succès", "Les couleurs ont été réinitialisées aux valeurs par défaut")
            setup_settings_tab(self)  # Rafraîchir la page des paramètres

    def apply_theme_changes(self):
        """Applique les changements de thème et redémarre l'interface"""
        if self.theme_manager.save_theme():
            messagebox.showinfo("Succès", "Les changements ont été enregistrés")
            if messagebox.askyesno("Redémarrage", "Voulez-vous redémarrer l'application pour appliquer tous les changements?"):
                self.restart_application()
            else:
                # Appliquer certains changements sans redémarrer
                self._update_ui_colors()
        else:
            messagebox.showerror("Erreur", "Impossible d'enregistrer les changements")

    def _update_ui_colors(self):
        """Met à jour les couleurs de l'interface sans redémarrer"""
        # Recréer les onglets pour appliquer les nouvelles couleurs
        current_tab = self.tab_view.get()
        
        # Recréer l'interface
        for widget in self.winfo_children():
            widget.destroy()
            
        self._setup_ui()
        
        # Revenir à l'onglet actif
        self.tab_view.set(current_tab)

    def restart_application(self):
        """Redémarre l'application pour appliquer les changements"""
        self.on_closing(restart=True)

    def on_closing(self, restart=False):
        """Nettoyage avant fermeture"""
        self.monitoring_active = False
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        if hasattr(self, 'task_checker_thread') and self.task_checker_thread.is_alive():
            self.task_checker_thread.join(timeout=1)
        
        self.destroy()
        
        if restart:
            os.execl(sys.executable, sys.executable, *sys.argv)
