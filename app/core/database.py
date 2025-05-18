import os
import sqlite3
from tkinter import messagebox

class DatabaseManager:
    """Gestion centralisée de la base de données"""
    def __init__(self, db_name="app_monitor.db"):
        self.db_path = os.path.join(os.path.expanduser("~"), "AppMonitorData", db_name)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        """Établit une connexion à la base de données"""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialisation des tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    executable TEXT NOT NULL UNIQUE,
                    is_blocked INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_id INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    duration INTEGER,
                    FOREIGN KEY(app_id) REFERENCES applications(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_id INTEGER,
                    action_type TEXT CHECK(action_type IN ('block', 'unblock')),
                    schedule_type TEXT CHECK(schedule_type IN ('duration', 'datetime')),
                    duration_hours INTEGER,
                    duration_minutes INTEGER,
                    scheduled_time TEXT,
                    is_completed INTEGER DEFAULT 0,
                    FOREIGN KEY(app_id) REFERENCES applications(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocked_sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    is_blocked INTEGER DEFAULT 1
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL,
                    is_productive INTEGER DEFAULT 1
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_category_mapping (
                    app_id INTEGER,
                    category_id INTEGER,
                    PRIMARY KEY (app_id, category_id),
                    FOREIGN KEY(app_id) REFERENCES applications(id),
                    FOREIGN KEY(category_id) REFERENCES app_categories(id)
                )
            ''')
            conn.commit()
            
            # Ajouter des catégories par défaut si elles n'existent pas
            default_categories = [
                ("Travail", "#4CAF50", 1),
                ("Études", "#2196F3", 1),
                ("Divertissement", "#FF9800", 0),
                ("Réseaux sociaux", "#F44336", 0),
                ("Productivité", "#9C27B0", 1)
            ]
            
            for name, color, is_productive in default_categories:
                cursor.execute(
                    "INSERT OR IGNORE INTO app_categories (name, color, is_productive) VALUES (?, ?, ?)",
                    (name, color, is_productive)
                )
            conn.commit()

    def execute_query(self, query, params=()):
        """Exécution sécurisée des requêtes SQL"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Erreur SQLite : {str(e)}")
            return None
