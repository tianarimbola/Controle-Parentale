import customtkinter as ctk
from tkinter import messagebox

def setup_settings_tab(app):
    """Configuration de l'onglet Paramètres"""
    settings_frame = ctk.CTkFrame(app.tab_settings)
    settings_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Titre
    ctk.CTkLabel(
        settings_frame,
        text="⚙️ Paramètres de l'application",
        font=("Arial", 16),
        text_color=app.theme_manager.get_color("card_text")
    ).pack(pady=10)

    # Mode d'apparence
    appearance_frame = ctk.CTkFrame(settings_frame)
    appearance_frame.pack(fill="x", pady=10, padx=10)

    ctk.CTkLabel(
        appearance_frame,
        text="Mode d'apparence:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=10, pady=10)

    appearance_var = ctk.StringVar(value=ctk.get_appearance_mode())
    ctk.CTkComboBox(
        appearance_frame,
        values=["System", "Light", "Dark"],
        variable=appearance_var,
        command=lambda value: ctk.set_appearance_mode(value)
    ).pack(side="left", padx=10, pady=10)

    # Personnalisation des couleurs
    colors_frame = ctk.CTkFrame(settings_frame)
    colors_frame.pack(fill="both", expand=True, pady=10, padx=10)

    ctk.CTkLabel(
        colors_frame,
        text="Personnalisation des couleurs",
        font=("Arial", 14),
        text_color=app.theme_manager.get_color("card_text")
    ).pack(pady=10)

    # Conteneur scrollable pour les couleurs
    colors_scroll = ctk.CTkScrollableFrame(colors_frame)
    colors_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    # Création des sélecteurs de couleur
    color_items = [
        ("Couleur principale", "primary_button"),
        ("Couleur de succès", "success_button"),
        ("Couleur d'alerte", "danger_button"),
        ("Couleur neutre", "neutral_button"),
        ("Couleur de texte principal", "card_text"),
        ("Couleur de texte secondaire", "card_subtext"),
        ("Couleur positive", "positive_change"),
        ("Couleur négative", "negative_change"),
        ("Couleur graphique primaire", "chart_primary"),
        ("Couleur graphique secondaire", "chart_secondary")
    ]

    for i, (label, key) in enumerate(color_items):
        color_item = ctk.CTkFrame(colors_scroll)
        color_item.pack(fill="x", pady=5)

        ctk.CTkLabel(
            color_item,
            text=label,
            text_color=app.theme_manager.get_color("card_text"),
            width=200
        ).pack(side="left", padx=10, pady=10)

        # Affichage de la couleur actuelle
        color_preview = ctk.CTkFrame(
            color_item,
            fg_color=app.theme_manager.get_color(key),
            width=30,
            height=30,
            corner_radius=5
        )
        color_preview.pack(side="left", padx=10, pady=10)

        # Bouton pour changer la couleur
        ctk.CTkButton(
            color_item,
            text="Changer",
            command=lambda k=key, p=color_preview: app.change_color(k, p),
            fg_color=app.theme_manager.get_color("primary_button"),
            hover_color=app.theme_manager.get_color("primary_button_hover"),
            width=100
        ).pack(side="right", padx=10, pady=10)

    # Boutons de réinitialisation et sauvegarde
    buttons_frame = ctk.CTkFrame(settings_frame)
    buttons_frame.pack(fill="x", pady=10, padx=10)

    ctk.CTkButton(
        buttons_frame,
        text="Réinitialiser aux couleurs par défaut",
        command=app.reset_colors,
        fg_color=app.theme_manager.get_color("danger_button"),
        hover_color=app.theme_manager.get_color("danger_button_hover"),
        width=200
    ).pack(side="left", padx=10, pady=10)

    ctk.CTkButton(
        buttons_frame,
        text="Appliquer les changements",
        command=app.apply_theme_changes,
        fg_color=app.theme_manager.get_color("success_button"),
        hover_color=app.theme_manager.get_color("success_button_hover"),
        width=200
    ).pack(side="right", padx=10, pady=10)
