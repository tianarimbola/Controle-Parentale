def hex_to_rgb(hex_color):
    """Convertit une couleur hexadécimale en RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def format_duration(seconds):
    """Formate une durée en secondes en format heures/minutes"""
    if seconds is None:
        return "0h 0m"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"
