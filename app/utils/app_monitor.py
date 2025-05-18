import psutil
import time
from datetime import datetime

class AppMonitoring:
    """Classe pour la surveillance des applications"""
    
    @staticmethod
    def check_blocked_apps(db):
        """Vérification et fermeture des applications bloquées"""
        cursor = db.execute_query(
            "SELECT executable FROM applications WHERE is_blocked = 1"
        )

        if cursor:
            for exe_path in [x[0] for x in cursor.fetchall()]:
                for process in psutil.process_iter(['pid', 'exe']):
                    try:
                        if process.info['exe'] and exe_path.lower() in process.info['exe'].lower():
                            psutil.Process(process.info['pid']).kill()
                    except:
                        continue

    @staticmethod
    def track_app_usage(db, tracked_processes):
        """Suivi de l'utilisation des applications"""
        current_time = datetime.now().isoformat()

        cursor = db.execute_query(
            "SELECT id, executable FROM applications WHERE is_blocked = 0"
        )

        if cursor:
            apps = {exe: id for id, exe in cursor.fetchall()}

            # Détection des processus en cours
            running = {}
            for p in psutil.process_iter(['pid', 'exe']):
                if p.info['exe'] and p.info['exe'] in apps:
                    running[p.info['exe']] = p.info['pid']

            # Nouveaux processus
            for exe, pid in running.items():
                if exe not in tracked_processes:
                    db.execute_query(
                        "INSERT INTO app_usage (app_id, start_time) VALUES (?, ?)",
                        (apps[exe], current_time)
                    )
                    tracked_processes[exe] = (pid, current_time)

            # Processus terminés
            for exe in list(tracked_processes.keys()):
                if exe not in running:
                    pid, start = tracked_processes[exe]
                    duration = (datetime.now() - datetime.fromisoformat(start)).total_seconds()

                    db.execute_query(
                        """UPDATE app_usage SET end_time = ?, duration = ?
                        WHERE app_id = ? AND end_time IS NULL""",
                        (current_time, duration, apps[exe])
                    )
                    del tracked_processes[exe]
