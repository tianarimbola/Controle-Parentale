import os
import sys
import platform
import ctypes
from tkinter import messagebox
import customtkinter as ctk
from app.ui.app_monitor import AppMonitor

if __name__ == "__main__":
    # Vérification des privilèges admin pour Windows
    if platform.system() == "Windows":
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("Demande d'élévation des privilèges administrateur...")
                # Afficher un message avant de demander l'élévation
                messagebox.showinfo(
                    "Privilèges administrateur", 
                    "L'application nécessite des privilèges administrateur pour fonctionner correctement.\n"
                    "Une fenêtre de confirmation va s'afficher."
                )
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit(0)
            else:
                print("Exécution avec privilèges administrateur.")
        except Exception as e:
            print(f"Erreur lors de la vérification des privilèges admin: {e}")
            messagebox.showwarning(
                "Avertissement", 
                "L'application fonctionne sans privilèges administrateur.\n"
                "Certaines fonctionnalités comme le blocage de sites peuvent ne pas fonctionner."
            )

    # Ajout d'un gestionnaire d'exceptions global
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Gestionnaire d'exceptions global pour capturer les erreurs non gérées"""
        error_msg = f"Une erreur non gérée s'est produite:\n{exc_type.__name__}: {exc_value}"
        print(error_msg)
        try:
            messagebox.showerror("Erreur critique", error_msg)
        except:
            pass  # Si la messagebox échoue aussi
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)

    # Installer le gestionnaire d'exceptions
    sys.excepthook = exception_handler

    # Configuration de l'interface
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # Démarrer l'application
    app = AppMonitor()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
