import os
import json

class ThemeManager:
    """Gestion des thèmes et couleurs de l'application"""
    DEFAULT_THEME = {
        "primary_button": "#3A7EBF",
        "primary_button_hover": "#2D5F8F",
        "success_button": "#2A8C36",
        "success_button_hover": "#20752D",
        "danger_button": "#D22B2B",
        "danger_button_hover": "#A52121",
        "neutral_button": "#6C757D",
        "neutral_button_hover": "#5A6268",
        "tab_bg": "#F0F0F0",
        "card_bg": "#FFFFFF",
        "card_text": "#333333",
        "card_subtext": "#666666",
        "positive_change": "#2A8C36",
        "negative_change": "#D22B2B",
        "chart_primary": "#4527A0",  # Couleur bleue pour le temps productif
        "chart_secondary": "#FF5252"  # Couleur rouge pour les distractions
    }
    
    def __init__(self, config_path=None):
        """Initialise le gestionnaire de thèmes"""
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), 
            "AppMonitorData", 
            "theme_config.json"
        )
        self.theme = self.load_theme()
    
    def load_theme(self):
        """Charge le thème depuis le fichier de configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    theme = json.load(f)
                # Vérifier que toutes les clés nécessaires sont présentes
                for key in self.DEFAULT_THEME:
                    if key not in theme:
                        theme[key] = self.DEFAULT_THEME[key]
                return theme
        except Exception as e:
            print(f"Erreur lors du chargement du thème: {e}")
        
        # Si le chargement échoue, utiliser le thème par défaut
        return self.DEFAULT_THEME.copy()
    
    def save_theme(self):
        """Sauvegarde le thème dans le fichier de configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.theme, f, indent=4)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du thème: {e}")
            return False
    
    def get_color(self, key):
        """Récupère une couleur du thème"""
        return self.theme.get(key, self.DEFAULT_THEME.get(key))
    
    def set_color(self, key, color):
        """Définit une couleur dans le thème"""
        if key in self.theme:
            self.theme[key] = color
            return True
        return False
    
    def reset_to_default(self):
        """Réinitialise le thème aux valeurs par défaut"""
        self.theme = self.DEFAULT_THEME.copy()
        return self.save_theme()
