#!/usr/bin/env python3
"""
DXF Generator - Point d'entrée principal
Lance l'application terminal pour la génération de fichiers DXF à partir de CSV
"""

import sys
import os

# Ajouter le dossier utils au chemin
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.terminal_app import TerminalDXFApp


def main():
    """Point d'entrée principal"""
    print("Lancement de l'application DXF Generator...")
    
    try:
        app = TerminalDXFApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrompue par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur critique: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
