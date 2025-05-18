import customtkinter as ctk
from tkinter import messagebox
import psutil

# Vérification des bibliothèques requises
try:
    import winapps
    WINAPPS_AVAILABLE = True
except ImportError:
    WINAPPS_AVAILABLE = False
    print("Winapps non disponible. La détection automatique des applications sera limitée.")

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    print("WMI non disponible. La détection automatique des applications sera limitée.")

def setup_apps_tab(app):
    """Configuration de l'onglet Applications"""
    main_frame = ctk.CTkFrame(app.tab_apps)
    main_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Bouton de détection
    ctk.CTkButton(
        main_frame,
        text="🔄 Détecter les applications",
        command=lambda: detect_installed_apps(app),
        fg_color=app.theme_manager.get_color("success_button"),
        hover_color=app.theme_manager.get_color("success_button_hover")
    ).pack(pady=10)

    # En-tête de liste
    header_frame = ctk.CTkFrame(main_frame)
    header_frame.pack(fill="x")
    
    ctk.CTkLabel(
        header_frame, 
        text="Statut", 
        width=50,
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)
    
    ctk.CTkLabel(
        header_frame, 
        text="Nom", 
        width=200,
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)
    
    ctk.CTkLabel(
        header_frame, 
        text="Catégorie", 
        width=100,
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)
    
    ctk.CTkLabel(
        header_frame, 
        text="Actions", 
        width=150,
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="right", padx=5)

    # Liste scrollable
    app.apps_list_frame = ctk.CTkScrollableFrame(main_frame)
    app.apps_list_frame.pack(expand=True, fill="both")
    load_applications(app)

def load_applications(app):
    """Chargement des applications dans l'interface"""
    for widget in app.apps_list_frame.winfo_children():
        widget.destroy()

    cursor = app.db.execute_query("""
        SELECT a.id, a.name, a.is_blocked, c.name as category_name, c.color
        FROM applications a
        LEFT JOIN app_category_mapping m ON a.id = m.app_id
        LEFT JOIN app_categories c ON m.category_id = c.id
    """)
    
    if cursor:
        apps = cursor.fetchall()
        if not apps:
            ctk.CTkLabel(
                app.apps_list_frame, 
                text="Aucune application détectée", 
                font=ctk.CTkFont(size=14), 
                text_color=app.theme_manager.get_color("card_subtext")
            ).pack(pady=20)
            return
            
        for app_data in apps:
            app_id, name, is_blocked = app_data[0], app_data[1], app_data[2]
            category_name = app_data[3] if app_data[3] else "Non catégorisé"
            category_color = app_data[4] if app_data[4] else "#CCCCCC"
            add_app_to_list(app, app_id, name, is_blocked, category_name, category_color)
    else:
        ctk.CTkLabel(
            app.apps_list_frame, 
            text="Aucune application détectée", 
            font=ctk.CTkFont(size=14), 
            text_color=app.theme_manager.get_color("card_subtext")
        ).pack(pady=20)

def add_app_to_list(app, app_id, name, is_blocked, category_name, category_color):
    """Ajout d'une application à la liste avec style moderne"""
    app_frame = ctk.CTkFrame(app.apps_list_frame)
    app_frame.pack(fill="x", pady=2)

    # Statut + Nom
    status_icon = "⛔" if is_blocked else "✅"
    ctk.CTkLabel(
        app_frame, 
        text=status_icon, 
        width=50,
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)
    
    ctk.CTkLabel(
        app_frame, 
        text=name, 
        width=200, 
        anchor="w",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)
    
    # Catégorie avec couleur
    category_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
    category_frame.pack(side="left", padx=5)
    
    category_indicator = ctk.CTkFrame(
        category_frame, 
        fg_color=category_color, 
        width=15, 
        height=15, 
        corner_radius=7
    )
    category_indicator.pack(side="left", padx=5)
    
    ctk.CTkLabel(
        category_frame, 
        text=category_name, 
        font=ctk.CTkFont(size=12), 
        text_color=app.theme_manager.get_color("card_subtext")
    ).pack(side="left")

    # Boutons d'action
    action_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
    action_frame.pack(side="right")

    ctk.CTkButton(
        action_frame,
        text="Débloquer" if is_blocked else "Bloquer",
        fg_color=app.theme_manager.get_color("success_button") if is_blocked else app.theme_manager.get_color("danger_button"),
        hover_color=app.theme_manager.get_color("success_button_hover") if is_blocked else app.theme_manager.get_color("danger_button_hover"),
        width=80,
        command=lambda: toggle_app_block(app, app_id)
    ).pack(side="left", padx=2)
    
    # Bouton de catégorie
    ctk.CTkButton(
        action_frame,
        text="Catégorie",
        fg_color=app.theme_manager.get_color("primary_button"),
        hover_color=app.theme_manager.get_color("primary_button_hover"),
        width=80,
        command=lambda: set_app_category(app, app_id, name)
    ).pack(side="left", padx=2)

    ctk.CTkButton(
        action_frame,
        text="🗑️",
        width=40,
        fg_color=app.theme_manager.get_color("neutral_button"),
        hover_color=app.theme_manager.get_color("neutral_button_hover"),
        command=lambda: delete_application(app, app_id)
    ).pack(side="left", padx=2)

def detect_installed_apps(app):
    """Détection automatique des applications installées"""
    try:
        detected = False
        
        # Méthode 1: Logiciels installés via winapps
        if WINAPPS_AVAILABLE:
            for app_item in winapps.list_installed():
                try:
                    if app_item.install_location:
                        exe_name = app_item.name + ".exe"
                        exe_path = os.path.join(app_item.install_location, exe_name)
                        if os.path.exists(exe_path):
                            app.db.execute_query(
                                "INSERT OR IGNORE INTO applications (name, executable) VALUES (?, ?)",
                                (app_item.name, exe_path)
                            )
                            detected = True
                except Exception:
                    continue

        # Méthode 2: Processus en cours via WMI
        if WMI_AVAILABLE:
            c = wmi.WMI()
            for process in c.Win32_Process():
                try:
                    if process.ExecutablePath and not any(
                            x in process.ExecutablePath.lower()
                            for x in ["\\windows\\", "\\microsoft\\"]
                    ):
                        app.db.execute_query(
                            "INSERT OR IGNORE INTO applications (name, executable) VALUES (?, ?)",
                            (process.Name, process.ExecutablePath)
                        )
                        detected = True
                except Exception:
                    continue
        
        # Méthode 3: Processus en cours via psutil (plus portable)
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_info = proc.info
                if process_info['exe'] and not any(
                        x in process_info['exe'].lower()
                        for x in ["\\windows\\", "\\microsoft\\", "/usr/bin/", "/bin/"]
                ):
                    app.db.execute_query(
                        "INSERT OR IGNORE INTO applications (name, executable) VALUES (?, ?)",
                        (process_info['name'], process_info['exe'])
                    )
                    detected = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        load_applications(app)
        
        if detected:
            messagebox.showinfo("Succès", "Détection terminée!")
        else:
            messagebox.showinfo("Information", "Aucune nouvelle application détectée.")
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de détection : {str(e)}")

def toggle_app_block(app, app_id):
    """Basculement du statut de blocage"""
    cursor = app.db.execute_query(
        "SELECT is_blocked FROM applications WHERE id = ?",
        (app_id,)
    )

    if cursor:
        current_status = cursor.fetchone()[0]
        new_status = 0 if current_status else 1

        app.db.execute_query(
            "UPDATE applications SET is_blocked = ? WHERE id = ?",
            (new_status, app_id)
        )
        load_applications(app)

def delete_application(app, app_id):
    """Suppression d'une application"""
    if messagebox.askyesno("Confirmer", "Supprimer cette application?"):
        # Supprimer les mappings de catégorie
        app.db.execute_query(
            "DELETE FROM app_category_mapping WHERE app_id = ?",
            (app_id,)
        )
        
        # Supprimer l'application
        app.db.execute_query(
            "DELETE FROM applications WHERE id = ?",
            (app_id,)
        )
        load_applications(app)

def set_app_category(app, app_id, app_name):
    """Ouvre une fenêtre pour définir la catégorie de l'application"""
    category_window = ctk.CTkToplevel(app)
    category_window.title(f"Catégorie pour {app_name}")
    category_window.geometry("400x300")
    category_window.transient(app)
    category_window.grab_set()
    
    # Récupérer les catégories
    cursor = app.db.execute_query("SELECT id, name, color FROM app_categories")
    categories = cursor.fetchall() if cursor else []
    
    # Récupérer la catégorie actuelle
    cursor = app.db.execute_query("""
        SELECT category_id FROM app_category_mapping 
        WHERE app_id = ?
    """, (app_id,))
    current_category = cursor.fetchone()[0] if cursor and cursor.fetchone() else None
    
    # Variable pour stocker la sélection
    selected_category = ctk.IntVar(value=current_category if current_category else 0)
    
    # Frame pour les catégories
    categories_frame = ctk.CTkScrollableFrame(category_window)
    categories_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Option "Aucune catégorie"
    none_frame = ctk.CTkFrame(categories_frame, fg_color="transparent")
    none_frame.pack(fill="x", pady=5)
    
    ctk.CTkRadioButton(
        none_frame,
        text="Aucune catégorie",
        variable=selected_category,
        value=0,
        fg_color=app.theme_manager.get_color("primary_button")
    ).pack(side="left", padx=10)
    
    # Liste des catégories
    for cat_id, cat_name, cat_color in categories:
        cat_frame = ctk.CTkFrame(categories_frame, fg_color="transparent")
        cat_frame.pack(fill="x", pady=5)
        
        ctk.CTkRadioButton(
            cat_frame,
            text=cat_name,
            variable=selected_category,
            value=cat_id,
            fg_color=app.theme_manager.get_color("primary_button")
        ).pack(side="left", padx=10)
        
        color_indicator = ctk.CTkFrame(
            cat_frame, 
            fg_color=cat_color, 
            width=15, 
            height=15, 
            corner_radius=7
        )
        color_indicator.pack(side="left", padx=5)
    
    # Boutons d'action
    buttons_frame = ctk.CTkFrame(category_window, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkButton(
        buttons_frame,
        text="Annuler",
        command=category_window.destroy,
        fg_color=app.theme_manager.get_color("neutral_button"),
        hover_color=app.theme_manager.get_color("neutral_button_hover"),
        width=100
    ).pack(side="left", padx=10)
    
    ctk.CTkButton(
        buttons_frame,
        text="Appliquer",
        command=lambda: apply_category(app, app_id, selected_category.get(), category_window),
        fg_color=app.theme_manager.get_color("primary_button"),
        hover_color=app.theme_manager.get_color("primary_button_hover"),
        width=100
    ).pack(side="right", padx=10)

def apply_category(app, app_id, category_id, window):
    """Applique la catégorie sélectionnée à l'application"""
    try:
        # Supprimer les mappings existants
        app.db.execute_query(
            "DELETE FROM app_category_mapping WHERE app_id = ?",
            (app_id,)
        )
        
        # Ajouter le nouveau mapping si une catégorie est sélectionnée
        if category_id > 0:
            app.db.execute_query(
                "INSERT INTO app_category_mapping (app_id, category_id) VALUES (?, ?)",
                (app_id, category_id)
            )
        
        window.destroy()
        load_applications(app)
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de l'application de la catégorie: {str(e)}")
