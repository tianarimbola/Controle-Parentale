import customtkinter as ctk

# Vérification des bibliothèques requises
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib non disponible. Les graphiques ne seront pas affichés.")

def setup_stats_tab(app):
    """Configuration de l'onglet Statistiques"""
    stats_frame = ctk.CTkFrame(app.tab_stats)
    stats_frame.pack(expand=True, fill="both", padx=10, pady=10)

    ctk.CTkLabel(
        stats_frame,
        text="📊 Statistiques d'utilisation",
        font=("Arial", 16),
        text_color=app.theme_manager.get_color("card_text")
    ).pack(pady=10)

    # Création des onglets pour différentes périodes
    tabs = ctk.CTkTabview(stats_frame)
    tabs.pack(fill="both", expand=True, padx=5, pady=5)

    # Ajout des onglets
    tabs.add("Aujourd'hui")
    tabs.add("Cette semaine")
    tabs.add("Ce mois")

    # Contenu de l'onglet "Aujourd'hui"
    today_frame = ctk.CTkFrame(tabs.tab("Aujourd'hui"))
    today_frame.pack(fill="both", expand=True, padx=5, pady=5)

    app.stats_text = ctk.CTkTextbox(
        today_frame,
        wrap="word",
        text_color=app.theme_manager.get_color("card_text")
    )
    app.stats_text.pack(expand=True, fill="both")
    update_stats(app)

    # Contenu des autres onglets
    if MATPLOTLIB_AVAILABLE:
        # Contenu de l'onglet "Cette semaine"
        week_frame = ctk.CTkFrame(tabs.tab("Cette semaine"))
        week_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Graphique hebdomadaire
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')

        # Données d'exemple
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        productive_hours = [4.5, 5.2, 3.8, 6.1, 5.5, 2.0, 1.5]

        ax.bar(days, productive_hours, color=app.theme_manager.get_color("chart_primary"))
        ax.set_ylabel('Heures productives')
        ax.set_title('Temps productif par jour')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        canvas = FigureCanvasTkAgg(fig, master=week_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Contenu de l'onglet "Ce mois"
        month_frame = ctk.CTkFrame(tabs.tab("Ce mois"))
        month_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Graphique mensuel
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        fig2.patch.set_facecolor('white')

        # Données d'exemple pour les semaines du mois
        weeks = ["Semaine 1", "Semaine 2", "Semaine 3", "Semaine 4"]
        productive_hours = [22.5, 25.2, 18.8, 20.1]
        distraction_hours = [10.2, 8.5, 12.3, 9.8]

        ax2.bar(weeks, productive_hours, label='Productif', color=app.theme_manager.get_color("chart_primary"))
        ax2.bar(weeks, distraction_hours, bottom=productive_hours, label='Distractions', color=app.theme_manager.get_color("chart_secondary"))

        ax2.set_ylabel('Heures')
        ax2.set_title('Répartition du temps par semaine')
        ax2.legend()
        ax2.grid(axis='y', linestyle='--', alpha=0.7)

        canvas2 = FigureCanvasTkAgg(fig2, master=month_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)
    else:
        # Placeholders si matplotlib n'est pas disponible
        for tab_name in ["Cette semaine", "Ce mois"]:
            tab_frame = ctk.CTkFrame(tabs.tab(tab_name))
            tab_frame.pack(fill="both", expand=True, padx=5, pady=5)

            ctk.CTkLabel(
                tab_frame,
                text="Graphiques non disponibles - Matplotlib requis",
                font=ctk.CTkFont(size=14),
                text_color=app.theme_manager.get_color("card_subtext")
            ).pack(pady=50)

def update_stats(app):
    """Mise à jour des statistiques"""
    cursor = app.db.execute_query("""
        SELECT a.name, SUM(u.duration), COUNT(u.id)
        FROM applications a
        LEFT JOIN app_usage u ON a.id = u.app_id
        GROUP BY a.name
        ORDER BY SUM(u.duration) DESC
    """)

    if cursor:
        app.stats_text.delete("1.0", "end")
        app.stats_text.insert("end", "Temps cumulé par application:\n\n")

        for name, duration, count in cursor.fetchall():
            if duration:
                hours = int(duration // 3600)
                mins = int((duration % 3600) // 60)
                app.stats_text.insert("end", f"• {name}: {hours}h{mins}m ({count} sessions)\n")
            else:
                app.stats_text.insert("end", f"• {name}: Aucune utilisation\n")
