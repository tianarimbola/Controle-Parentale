import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta

def setup_schedule_tab(app):
    """Configuration de l'onglet Planification"""
    main_frame = ctk.CTkFrame(app.tab_schedule)
    main_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Sélection d'application
    app_select_frame = ctk.CTkFrame(main_frame)
    app_select_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(
        app_select_frame,
        text="Application:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    app.app_combobox = ctk.CTkComboBox(app_select_frame, values=get_app_names(app))
    app.app_combobox.pack(side="left", padx=5, fill="x", expand=True)

    # Sélection d'action
    action_frame = ctk.CTkFrame(main_frame)
    action_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(
        action_frame,
        text="Action:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    app.action_var = ctk.StringVar(value="block")

    ctk.CTkRadioButton(
        action_frame,
        text="Bloquer",
        variable=app.action_var,
        value="block",
        fg_color=app.theme_manager.get_color("primary_button"),
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    ctk.CTkRadioButton(
        action_frame,
        text="Débloquer",
        variable=app.action_var,
        value="unblock",
        fg_color=app.theme_manager.get_color("primary_button"),
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    # Type de planification
    schedule_type_frame = ctk.CTkFrame(main_frame)
    schedule_type_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(
        schedule_type_frame,
        text="Type:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    app.schedule_type_var = ctk.StringVar(value="duration")

    ctk.CTkRadioButton(
        schedule_type_frame,
        text="Durée",
        variable=app.schedule_type_var,
        value="duration",
        command=lambda: toggle_schedule_ui(app),
        fg_color=app.theme_manager.get_color("primary_button"),
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    ctk.CTkRadioButton(
        schedule_type_frame,
        text="Date/Heure",
        variable=app.schedule_type_var,
        value="datetime",
        command=lambda: toggle_schedule_ui(app),
        fg_color=app.theme_manager.get_color("primary_button"),
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    # Interface durée
    app.duration_frame = ctk.CTkFrame(main_frame)
    app.duration_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(
        app.duration_frame,
        text="Heures:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    app.hours_entry = ctk.CTkEntry(app.duration_frame, width=50)
    app.hours_entry.pack(side="left", padx=5)
    app.hours_entry.insert(0, "0")

    ctk.CTkLabel(
        app.duration_frame,
        text="Minutes:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    app.minutes_entry = ctk.CTkEntry(app.duration_frame, width=50)
    app.minutes_entry.pack(side="left", padx=5)
    app.minutes_entry.insert(0, "30")

    # Interface date/heure
    app.datetime_frame = ctk.CTkFrame(main_frame)

    ctk.CTkLabel(
        app.datetime_frame,
        text="Date:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    app.date_entry = ctk.CTkEntry(app.datetime_frame, placeholder_text="JJ/MM/AAAA")
    app.date_entry.pack(side="left", padx=5)

    ctk.CTkLabel(
        app.datetime_frame,
        text="Heure:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(side="left", padx=5)

    app.time_entry = ctk.CTkEntry(app.datetime_frame, placeholder_text="HH:MM")
    app.time_entry.pack(side="left", padx=5)

    # Bouton de soumission
    submit_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    submit_frame.pack(fill="x", pady=10)

    ctk.CTkButton(
        submit_frame,
        text="Planifier",
        command=lambda: schedule_action(app),
        fg_color=app.theme_manager.get_color("primary_button"),
        hover_color=app.theme_manager.get_color("primary_button_hover")
    ).pack(pady=5)

    # Liste des tâches
    ctk.CTkLabel(
        main_frame,
        text="Tâches planifiées:",
        text_color=app.theme_manager.get_color("card_text")
    ).pack(anchor="w", pady=5)

    app.scheduled_tasks_frame = ctk.CTkScrollableFrame(main_frame, height=200)
    app.scheduled_tasks_frame.pack(fill="x", pady=5)
    load_scheduled_tasks(app)

def toggle_schedule_ui(app):
    """Bascule entre les interfaces durée et date/heure"""
    if app.schedule_type_var.get() == "duration":
        app.datetime_frame.pack_forget()
        app.duration_frame.pack(fill="x", pady=5)
    else:
        app.duration_frame.pack_forget()
        app.datetime_frame.pack(fill="x", pady=5)

def get_app_names(app):
    """Récupération des noms d'applications"""
    cursor = app.db.execute_query("SELECT name FROM applications")
    if cursor:
        app_names = [row[0] for row in cursor.fetchall()]
        return app_names if app_names else ["Aucune application"]
    return ["Aucune application"]

def get_app_id_by_name(app, name):
    """Récupération de l'ID par nom avec gestion robuste des erreurs"""
    cursor = app.db.execute_query("SELECT id FROM applications WHERE name = ?", (name,))
    if cursor:
        result = cursor.fetchone()
        return result[0] if result else None
    return None

def schedule_action(app):
    """Planification d'une action avec vérification améliorée des entrées"""
    app_name = app.app_combobox.get()
    if not app_name or app_name == "Aucune application":
        messagebox.showerror("Erreur", "Sélectionnez une application")
        return

    app_id = get_app_id_by_name(app, app_name)
    if app_id is None:
        messagebox.showerror("Erreur", "Application introuvable")
        return

    action_type = app.action_var.get()
    schedule_type = app.schedule_type_var.get()

    if schedule_type == "duration":
        try:
            hours = int(app.hours_entry.get() or 0)
            minutes = int(app.minutes_entry.get() or 0)

            if hours == 0 and minutes == 0:
                messagebox.showerror("Erreur", "Durée invalide")
                return

            scheduled_time = (datetime.now() + timedelta(hours=hours, minutes=minutes)).isoformat()

            app.db.execute_query(
                """INSERT INTO scheduled_tasks 
                (app_id, action_type, schedule_type, duration_hours, duration_minutes, scheduled_time)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (app_id, action_type, schedule_type, hours, minutes, scheduled_time)
            )

            messagebox.showinfo("Succès", f"Action dans {hours}h{minutes}m")
            load_scheduled_tasks(app)

        except ValueError:
            messagebox.showerror("Erreur", "Valeurs numériques requises")

    else:  # datetime
        date_str = app.date_entry.get()
        time_str = app.time_entry.get()

        try:
            day, month, year = map(int, date_str.split('/'))
            hour, minute = map(int, time_str.split(':'))
            scheduled_time = datetime(year, month, day, hour, minute).isoformat()

            if scheduled_time <= datetime.now().isoformat():
                messagebox.showerror("Erreur", "Date/heure future requise")
                return

            app.db.execute_query(
                """INSERT INTO scheduled_tasks 
                (app_id, action_type, schedule_type, scheduled_time)
                VALUES (?, ?, ?, ?)""",
                (app_id, action_type, schedule_type, scheduled_time)
            )

            messagebox.showinfo("Succès", f"Action le {date_str} à {time_str}")
            load_scheduled_tasks(app)

        except Exception as e:
            messagebox.showerror("Erreur", f"Format invalide : JJ/MM/AAAA et HH:MM\n{str(e)}")

def load_scheduled_tasks(app):
    """Chargement des tâches planifiées avec style moderne"""
    for widget in app.scheduled_tasks_frame.winfo_children():
        widget.destroy()

    cursor = app.db.execute_query("""
        SELECT t.id, a.name, t.action_type, t.schedule_type, 
               t.duration_hours, t.duration_minutes, t.scheduled_time
        FROM scheduled_tasks t
        JOIN applications a ON t.app_id = a.id
        WHERE t.is_completed = 0
        ORDER BY t.scheduled_time
    """)

    if cursor:
        tasks = cursor.fetchall()
        if not tasks:
            ctk.CTkLabel(
                app.scheduled_tasks_frame,
                text="Aucune tâche planifiée",
                font=ctk.CTkFont(size=14),
                text_color=app.theme_manager.get_color("card_subtext")
            ).pack(pady=20)
            return

        for task_id, app_name, action_type, schedule_type, hours, minutes, scheduled_time in tasks:
            task_frame = ctk.CTkFrame(app.scheduled_tasks_frame)
            task_frame.pack(fill="x", pady=2)

            if schedule_type == "duration":
                info_text = f"{app_name} - {action_type} dans {hours}h{minutes}m"
            else:
                dt = datetime.fromisoformat(scheduled_time)
                info_text = f"{app_name} - {action_type} le {dt.strftime('%d/%m/%Y à %H:%M')}"

            ctk.CTkLabel(
                task_frame,
                text=info_text,
                width=400,
                text_color=app.theme_manager.get_color("card_text")
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                task_frame,
                text="Annuler",
                fg_color=app.theme_manager.get_color("danger_button"),
                hover_color=app.theme_manager.get_color("danger_button_hover"),
                width=80,
                command=lambda id=task_id: cancel_scheduled_task(app, id)
            ).pack(side="right", padx=5)
    else:
        ctk.CTkLabel(
            app.scheduled_tasks_frame,
            text="Aucune tâche planifiée",
            font=ctk.CTkFont(size=14),
            text_color=app.theme_manager.get_color("card_subtext")
        ).pack(pady=20)

def cancel_scheduled_task(app, task_id):
    """Annulation d'une tâche planifiée"""
    if messagebox.askyesno("Confirmer", "Annuler cette tâche?"):
        app.db.execute_query(
            "DELETE FROM scheduled_tasks WHERE id = ?",
            (task_id,)
        )
        load_scheduled_tasks(app)
