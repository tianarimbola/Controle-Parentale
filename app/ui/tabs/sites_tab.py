import customtkinter as ctk
from tkinter import messagebox

def setup_sites_tab(app):
    """Configuration de l'onglet Sites Web"""
    main_frame = ctk.CTkFrame(app.tab_sites)
    main_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Frame d'ajout
    add_frame = ctk.CTkFrame(main_frame)
    add_frame.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(
        add_frame,
        text="URL du site:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    app.site_url_entry = ctk.CTkEntry(add_frame, placeholder_text="exemple.com")
    app.site_url_entry.pack(side="left", padx=5, fill="x", expand=True)

    ctk.CTkButton(
        add_frame,
        text="Ajouter",
        command=lambda: add_site(app),
        fg_color=app.theme_manager.get_color("primary_button"),
        hover_color=app.theme_manager.get_color("primary_button_hover"),
        width=100
    ).pack(side="right", padx=5)

    # Liste des sites
    ctk.CTkLabel(
        main_frame,
        text="Sites bloqués:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(anchor="w", pady=(10, 5))

    app.sites_list_frame = ctk.CTkScrollableFrame(main_frame, height=300)
    app.sites_list_frame.pack(fill="both", expand=True)
    load_blocked_sites(app)

def load_blocked_sites(app):
    """Charge la liste des sites bloqués"""
    for widget in app.sites_list_frame.winfo_children():
        widget.destroy()

    cursor = app.db.execute_query(
        "SELECT id, url FROM blocked_sites WHERE is_blocked = 1"
    )

    if cursor:
        sites = cursor.fetchall()
        if not sites:
            ctk.CTkLabel(
                app.sites_list_frame,
                text="Aucun site bloqué",
                font=ctk.CTkFont(size=14),
                text_color=app.theme_manager.get_color("card_subtext")
            ).pack(pady=20)
            return

        for site_id, url in sites:
            add_site_to_list(app, site_id, url)
    else:
        ctk.CTkLabel(
            app.sites_list_frame,
            text="Aucun site bloqué",
            font=ctk.CTkFont(size=14),
            text_color=app.theme_manager.get_color("card_subtext")
        ).pack(pady=20)

def add_site_to_list(app, site_id, url):
    """Ajoute un site à la liste avec style moderne"""
    site_frame = ctk.CTkFrame(app.sites_list_frame)
    site_frame.pack(fill="x", pady=2)

    # URL
    ctk.CTkLabel(
        site_frame,
        text=url,
        width=400,
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    # Boutons d'action
    action_frame = ctk.CTkFrame(site_frame, fg_color="transparent")
    action_frame.pack(side="right")

    ctk.CTkButton(
        action_frame,
        text="Débloquer",
        fg_color=app.theme_manager.get_color("success_button"),
        hover_color=app.theme_manager.get_color("success_button_hover"),
        width=80,
        command=lambda: toggle_site_block(app, site_id, url)
    ).pack(side="left", padx=2)

    ctk.CTkButton(
        action_frame,
        text="🗑️",
        width=40,
        fg_color=app.theme_manager.get_color("neutral_button"),
        hover_color=app.theme_manager.get_color("neutral_button_hover"),
        command=lambda: delete_site(app, site_id, url)
    ).pack(side="left", padx=2)

def add_site(app):
    """Ajoute un site à bloquer"""
    url = app.site_url_entry.get().strip()
    if not url:
        messagebox.showerror("Erreur", "Veuillez entrer une URL")
        return

    try:
        # Ajout à la base de données
        app.db.execute_query(
            "INSERT OR IGNORE INTO blocked_sites (url) VALUES (?)",
            (url,)
        )

        # Blocage effectif
        if app.site_blocker.block_site(url):
            messagebox.showinfo("Succès", f"Site {url} bloqué avec succès!")
            load_blocked_sites(app)
            app.site_url_entry.delete(0, "end")
        else:
            # Si le blocage a échoué, supprimer de la base
            app.db.execute_query(
                "DELETE FROM blocked_sites WHERE url = ?",
                (url,)
            )

    except Exception as e:
        messagebox.showerror("Erreur", f"Échec d'ajout : {str(e)}")

def toggle_site_block(app, site_id, url):
    """Bascule le statut de blocage d'un site"""
    if messagebox.askyesno("Confirmer", f"Débloquer le site {url}?"):
        if app.site_blocker.unblock_site(url):
            app.db.execute_query(
                "UPDATE blocked_sites SET is_blocked = 0 WHERE id = ?",
                (site_id,)
            )
            load_blocked_sites(app)
            messagebox.showinfo("Succès", f"Site {url} débloqué!")
        else:
            messagebox.showerror("Erreur", "Échec du déblocage")

def delete_site(app, site_id, url):
    """Supprime un site de la liste"""
    if messagebox.askyesno("Confirmer", f"Supprimer le site {url}?"):
        # Débloquer d'abord si nécessaire
        cursor = app.db.execute_query(
            "SELECT is_blocked FROM blocked_sites WHERE id = ?",
            (site_id,)
        )
        if cursor and cursor.fetchone()[0] == 1:
            app.site_blocker.unblock_site(url)

        # Supprimer de la base
        app.db.execute_query(
            "DELETE FROM blocked_sites WHERE id = ?",
            (site_id,)
        )
        load_blocked_sites(app)
