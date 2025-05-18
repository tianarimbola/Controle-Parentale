import customtkinter as ctk
from datetime import datetime
from app.utils.helpers import format_duration

# Vérification des bibliothèques requises
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib non disponible. Les graphiques ne seront pas affichés.")

def setup_dashboard_tab(app):
    """Configuration de l'onglet Tableau de bord"""
    main_frame = ctk.CTkFrame(app.tab_dashboard)
    main_frame.pack(expand=True, fill="both", padx=10, pady=10)
    
    # Configuration du grid pour les cartes de statistiques
    main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cards")
    main_frame.grid_rowconfigure(0, weight=0)
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_rowconfigure(2, weight=1)
    
    # Cartes de statistiques
    # 1. Temps productif
    productive_time = get_productive_time(app)
    productive_display = format_duration(productive_time)
    
    create_stat_card(
        app, main_frame, 0, 0, "Temps productif", 
        productive_display, 
        "+12%", app.theme_manager.get_color("positive_change")
    )
    
    # 2. Sites bloqués
    sites_count = get_blocked_sites_count(app)
    create_stat_card(
        app, main_frame, 0, 1, "Sites bloqués", 
        f"{sites_count}", 
        "+3", app.theme_manager.get_color("positive_change")
    )
    
    # 3. Applications bloquées
    apps_count = get_blocked_apps_count(app)
    create_stat_card(
        app, main_frame, 0, 2, "Applications bloquées", 
        f"{apps_count}", 
        "-2", app.theme_manager.get_color("negative_change")
    )
    
    # 4. Concentration
    concentration = calculate_concentration(app)
    create_stat_card(
        app, main_frame, 0, 3, "Concentration", 
        f"{concentration}%", 
        "+7%", app.theme_manager.get_color("positive_change")
    )
    
    # Graphique de productivité hebdomadaire
    if MATPLOTLIB_AVAILABLE:
        create_weekly_chart(app, main_frame)
    else:
        create_weekly_chart_placeholder(app, main_frame)
    
    # Applications fréquentes
    create_frequent_apps_section(app, main_frame)

def create_stat_card(app, parent, row, col, title, value, change, change_color):
    """Crée une carte de statistique"""
    card = ctk.CTkFrame(
        parent, 
        corner_radius=10, 
        fg_color=app.theme_manager.get_color("card_bg")
    )
    card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    # Titre
    title_label = ctk.CTkLabel(
        card, 
        text=title, 
        font=ctk.CTkFont(size=14),
        text_color=app.theme_manager.get_color("card_subtext")
    )
    title_label.pack(anchor="w", padx=15, pady=(15, 5))
    
    # Valeur
    value_label = ctk.CTkLabel(
        card, 
        text=value, 
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=app.theme_manager.get_color("card_text")
    )
    value_label.pack(anchor="w", padx=15, pady=(0, 5))
    
    # Changement
    change_label = ctk.CTkLabel(
        card, 
        text=change, 
        font=ctk.CTkFont(size=12),
        text_color=change_color
    )
    change_label.pack(anchor="w", padx=15, pady=(0, 15))

def create_weekly_chart(app, parent):
    """Crée le graphique de productivité hebdomadaire"""
    chart_frame = ctk.CTkFrame(
        parent, 
        corner_radius=10, 
        fg_color=app.theme_manager.get_color("card_bg")
    )
    chart_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    # Titre
    title_label = ctk.CTkLabel(
        chart_frame, 
        text="Votre productivité cette semaine", 
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=app.theme_manager.get_color("card_text")
    )
    title_label.pack(anchor="w", padx=15, pady=(15, 10))
    
    # Données pour le graphique
    days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    productive = [3, 4, 3, 5, 4, 2, 2.5]  # Heures productives
    distractions = [2, 1.5, 2, 1, 1.5, 3, 2.5]  # Heures de distraction
    
    # Création du graphique avec matplotlib
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('white')
    
    # Barres empilées
    ax.bar(days, productive, label='Productif', color=app.theme_manager.get_color("chart_primary"))
    ax.bar(days, distractions, bottom=productive, label='Distractions', color=app.theme_manager.get_color("chart_secondary"))
    
    # Personnalisation
    ax.set_ylabel('Heures')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Intégration dans l'interface
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

def create_weekly_chart_placeholder(app, parent):
    """Crée un placeholder pour le graphique si matplotlib n'est pas disponible"""
    chart_frame = ctk.CTkFrame(
        parent, 
        corner_radius=10, 
        fg_color=app.theme_manager.get_color("card_bg")
    )
    chart_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    # Titre
    title_label = ctk.CTkLabel(
        chart_frame, 
        text="Votre productivité cette semaine", 
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=app.theme_manager.get_color("card_text")
    )
    title_label.pack(anchor="w", padx=15, pady=(15, 10))
    
    # Message d'erreur
    error_label = ctk.CTkLabel(
        chart_frame, 
        text="Graphique non disponible - Matplotlib requis", 
        font=ctk.CTkFont(size=14),
        text_color=app.theme_manager.get_color("card_subtext")
    )
    error_label.pack(pady=50)

def create_frequent_apps_section(app, parent):
    """Crée la section des applications fréquentes"""
    apps_frame = ctk.CTkFrame(
        parent, 
        corner_radius=10, 
        fg_color=app.theme_manager.get_color("card_bg")
    )
    apps_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    # Titre
    title_label = ctk.CTkLabel(
        apps_frame, 
        text="Vos applications fréquentes", 
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=app.theme_manager.get_color("card_text")
    )
    title_label.pack(anchor="w", padx=15, pady=(15, 10))
    
    # Liste des applications
    apps_list = get_frequent_apps(app)
    
    # Conteneur pour les applications
    apps_container = ctk.CTkFrame(apps_frame, fg_color="transparent")
    apps_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    # Affichage des applications
    for i, (name, duration) in enumerate(apps_list):
        app_item = ctk.CTkFrame(
            apps_container, 
            fg_color="#F5F5F5", 
            corner_radius=5
        )
        app_item.pack(fill="x", pady=5)
    
        # Nom de l'application
        app_name = ctk.CTkLabel(
            app_item, 
            text=name, 
            font=ctk.CTkFont(size=14),
            text_color=app.theme_manager.get_color("card_text")
        )
        app_name.pack(side="left", padx=10, pady=10)
    
        # Durée d'utilisation
        duration_text = format_duration(duration)
    
        app_duration = ctk.CTkLabel(
            app_item, 
            text=duration_text, 
            font=ctk.CTkFont(size=14),
            text_color=app.theme_manager.get_color("card_subtext")
        )
        app_duration.pack(side="right", padx=10, pady=10)

def get_productive_time(app):
    """Calcule le temps productif total"""
    cursor = app.db.execute_query("""
        SELECT SUM(duration) FROM app_usage
        JOIN applications ON app_usage.app_id = applications.id
        JOIN app_category_mapping ON applications.id = app_category_mapping.app_id
        JOIN app_categories ON app_category_mapping.category_id = app_categories.id
        WHERE app_categories.is_productive = 1
        AND start_time >= ?
    """, (datetime.now().replace(hour=0, minute=0, second=0).isoformat(),))
    
    if cursor:
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    return 0

def get_blocked_sites_count(app):
    """Compte le nombre de sites bloqués"""
    cursor = app.db.execute_query(
        "SELECT COUNT(*) FROM blocked_sites WHERE is_blocked = 1"
    )
    
    if cursor:
        return cursor.fetchone()[0]
    return 0

def get_blocked_apps_count(app):
    """Compte le nombre d'applications bloquées"""
    cursor = app.db.execute_query(
        "SELECT COUNT(*) FROM applications WHERE is_blocked = 1"
    )
    
    if cursor:
        return cursor.fetchone()[0]
    return 0

def calculate_concentration(app):
    """Calcule le pourcentage de concentration (temps productif / temps total)"""
    cursor = app.db.execute_query("""
        SELECT 
            SUM(CASE WHEN c.is_productive = 1 THEN u.duration ELSE 0 END) as productive,
            SUM(u.duration) as total
        FROM app_usage u
        JOIN applications a ON u.app_id = a.id
        LEFT JOIN app_category_mapping m ON a.id = m.app_id
        LEFT JOIN app_categories c ON m.category_id = c.id
        WHERE start_time >= ?
    """, (datetime.now().replace(hour=0, minute=0, second=0).isoformat(),))
    
    if cursor:
        result = cursor.fetchone()
        productive, total = result
        
        # Vérification que productive et total ne sont pas None
        if productive is None:
            productive = 0
        if total is None or total == 0:
            return 82  # Valeur par défaut si pas de données
        
        return int((productive / total) * 100)
    
    return 82  # Valeur par défaut pour la démo

def get_frequent_apps(app):
    """Récupère les applications les plus utilisées"""
    cursor = app.db.execute_query("""
        SELECT a.name, SUM(u.duration) as total_duration
        FROM applications a
        JOIN app_usage u ON a.id = u.app_id
        GROUP BY a.name
        ORDER BY total_duration DESC
        LIMIT 5
    """)
    
    if cursor:
        return cursor.fetchall()
    
    # Données d'exemple si aucune donnée n'est disponible
    return [
        ("Google Chrome", 7200),
        ("Visual Studio Code", 5400),
        ("Microsoft Word", 3600),
        ("Spotify", 1800),
        ("Slack", 1200)
    ]
