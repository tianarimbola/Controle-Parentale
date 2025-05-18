import os
import time
import platform
import ctypes
import sys
import subprocess
from tkinter import messagebox

class SiteBlocker:
    """Gestion du blocage des sites web"""
    HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts" if platform.system() == "Windows" else "/etc/hosts"
    TEMP_BACKUP = os.path.join(os.getenv('TEMP', '/tmp'), 'hosts_backup.txt')

    @staticmethod
    def _run_as_admin():
        """Relance le programme avec les droits admin"""
        try:
            if platform.system() == "Windows":
                # Utilisation d'un processus détaché pour éviter la fermeture immédiate
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                # Attendre un peu pour s'assurer que le nouveau processus démarre
                time.sleep(1)
            else:
                os.system(f"sudo {sys.executable} {' '.join(sys.argv)}")
            sys.exit(0)  # Sortie explicite avec code 0
        except Exception as e:
            messagebox.showerror("Erreur d'élévation", f"Impossible d'obtenir les privilèges administrateur: {str(e)}")
            return False

    @staticmethod
    def _backup_hosts():
        """Crée une sauvegarde du fichier hosts"""
        try:
            with open(SiteBlocker.HOSTS_PATH, 'r') as f:
                content = f.read()
            with open(SiteBlocker.TEMP_BACKUP, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            messagebox.showerror("Erreur Backup", f"Échec sauvegarde: {str(e)}")
            return False

    @staticmethod
    def block_site(url):
        """Bloque un site avec gestion des droits"""
        try:
            # Vérification des droits admin
            if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showinfo(
                    "Privilèges requis", 
                    "Le blocage de sites nécessite des privilèges administrateur.\n"
                    "Une fenêtre de confirmation va s'afficher."
                )
                if not SiteBlocker._run_as_admin():
                    return False

            # Validation URL
            url = url.strip().lower()
            if not url or ' ' in url:
                raise ValueError("URL invalide")

            # Sauvegarde préventive
            SiteBlocker._backup_hosts()

            # Ajout des entrées
            with open(SiteBlocker.HOSTS_PATH, 'a') as f:
                f.write(f"\n127.0.0.1 {url}\n127.0.0.1 www.{url}\n")

            # Rafraîchissement DNS (Windows uniquement)
            if platform.system() == "Windows":
                subprocess.run(['ipconfig', '/flushdns'], shell=True, check=True)
            
            print(f"Site {url} bloqué avec succès")
            return True

        except Exception as e:
            error_msg = f"Échec du blocage: {str(e)}"
            print(error_msg)
            messagebox.showerror("Erreur", error_msg)
            return False

    @staticmethod
    def unblock_site(url):
        """Débloque un site avec restauration si erreur"""
        try:
            # Vérification des droits admin
            if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
                if not SiteBlocker._run_as_admin():
                    return False

            url = url.strip().lower()
            SiteBlocker._backup_hosts()

            # Filtrage des lignes
            with open(SiteBlocker.HOSTS_PATH, 'r') as f:
                lines = [l for l in f if url not in l and f"www.{url}" not in l]

            # Réécriture
            with open(SiteBlocker.HOSTS_PATH, 'w') as f:
                f.writelines(lines)

            # Rafraîchissement DNS (Windows uniquement)
            if platform.system() == "Windows":
                subprocess.run(['ipconfig', '/flushdns'], shell=True, check=True)
            return True

        except Exception as e:
            # Restauration de la sauvegarde
            if os.path.exists(SiteBlocker.TEMP_BACKUP):
                os.replace(SiteBlocker.TEMP_BACKUP, SiteBlocker.HOSTS_PATH)
            messagebox.showerror("Erreur", f"Échec déblocage: {str(e)}")
            return False
