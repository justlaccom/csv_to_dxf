#!/usr/bin/env python3
"""
Application Terminal DXF Generator
Interface terminal stylisée pour la génération de fichiers DXF à partir de CSV
"""

import sys
import os
import threading
import time
from colorama import Fore, Style

# Ajouter le dossier utils au chemin
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.terminal_ui import TerminalUI
from utils.csv_analyzer import CSVAnalyzer
from utils.dxf_generator import DXFGenerator


class TerminalDXFApp:
    """Application principale avec interface terminal"""
    
    def __init__(self):
        self.ui = TerminalUI()
        self.analyzer = CSVAnalyzer()
        self.generator = DXFGenerator()
        
        # État de l'application
        self.current_file = ""
        self.analysis_result = None
        self.pieces_data = []
    
    def run(self):
        """Point d'entrée principal de l'application"""
        try:
            self.ui.clear_screen()
            self.ui.print_banner("DXF Generator", font="slant")
            self.ui.print_box("Générateur de fichiers DXF à partir de fichiers CSV", color='info')
            print()
            
            # Lancer directement l'analyse CSV
            self.analyze_csv_file()
            
        except KeyboardInterrupt:
            self.ui.print_warning("\nApplication interrompue par l'utilisateur")
            sys.exit(0)
        except Exception as e:
            self.ui.print_error(f"Erreur critique: {e}")
            sys.exit(1)
    
    def main_menu(self):
        """Menu principal"""
        while True:
            options = [
                "Analyser un fichier CSV",
                "Générer les fichiers DXF",
                "Voir les données extraites",
                "Quitter"
            ]
            
            choice = self.ui.print_menu("Menu Principal", options, 'primary')
            
            if choice == 0:
                self.analyze_csv_file()
            elif choice == 1:
                self.generate_dxf_files()
            elif choice == 2:
                self.show_extracted_data()
            elif choice == 3:
                self.ui.print_success("Au revoir!")
                break
    
    def analyze_csv_file(self):
        """Analyse un fichier CSV"""
        self.ui.clear_screen()
        self.ui.print_banner("Analyse CSV", font="small")
        
        # Sélection du fichier
        file_path = self.ui.select_file("Sélectionnez un fichier CSV à analyser")
        
        if not file_path:
            return
        
        self.current_file = file_path
        self.ui.print_info(f"Analyse du fichier: {os.path.basename(file_path)}")
        print()
        
        def analyze_thread():
            self.analysis_result = self.analyzer.analyze_file(file_path)
        
        # Lancer l'analyse dans un thread
        thread = threading.Thread(target=analyze_thread)
        thread.start()
        
        # Barre de progression animée pendant l'analyse
        progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0
        while thread.is_alive():
            char = progress_chars[i % len(progress_chars)]
            print(f"\r{Fore.CYAN}[{char}] Analyse en cours...{Style.RESET_ALL}", end='', flush=True)
            i += 1
            time.sleep(0.1)
        
        print("\r" + " " * 50 + "\r", end='', flush=True)  # Nettoyer la ligne
        thread.join()
        
        # Vérifier les résultats
        if self.analysis_result and self.analysis_result.get('success'):
            self.ui.print_success("Analyse terminée!")
            print()
            
            # Afficher les colonnes détectées
            detected_columns = self.analysis_result['detected_columns']
            self.ui.print_box("Colonnes détectées:", color='info')
            
            for key, value in detected_columns.items():
                if value:
                    self.ui.print_success(f"  {key}: {value}")
                else:
                    self.ui.print_warning(f"  {key}: Non détectée")
            
            print()
            
            # Extraire les données finales
            self.pieces_data = self.analyzer.get_pieces_data()
            self.ui.print_success(f"{len(self.pieces_data)} pièces extraites")
            print()
            
            # Demander si l'utilisateur veut modifier les colonnes
            if self.ui.confirm("Modifier les colonnes?", default=False):
                self.modify_column_selection()
                print()
            
            # Générer automatiquement les fichiers DXF
            if self.pieces_data:
                self.ui.print_info("Génération des fichiers DXF...")
                self.generate_dxf_files_auto()
            else:
                self.ui.print_warning("Aucune donnée valide à traiter.")
            
        else:
            error = self.analysis_result.get('error', 'Erreur inconnue') if self.analysis_result else 'Erreur inconnue'
            self.ui.print_error(f"Erreur: {error}")
        
        self.ui.wait_for_key()
    
    def generate_dxf_files_auto(self):
        """Génère automatiquement les fichiers DXF sans confirmation"""
        if not self.pieces_data:
            self.ui.print_warning("Aucune donnée à traiter.")
            return
        
        # Génération avec barre de progression
        def generate_thread():
            self.created_files, self.errors = self.generator.create_dxf_files(self.pieces_data)
        
        thread = threading.Thread(target=generate_thread)
        thread.start()
        
        # Barre de progression animée pendant la génération
        progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0
        while thread.is_alive():
            char = progress_chars[i % len(progress_chars)]
            print(f"\r{Fore.GREEN}[{char}] Génération DXF...{Style.RESET_ALL}", end='', flush=True)
            i += 1
            time.sleep(0.1)
        
        print("\r" + " " * 50 + "\r", end='', flush=True)  # Nettoyer la ligne
        thread.join()
        print()
        
        # Afficher les résultats
        if hasattr(self, 'created_files'):
            self.ui.print_success(f"Génération terminée: {self.created_files} fichiers créés")
            
            if hasattr(self, 'errors') and self.errors:
                self.ui.print_warning(f"{len(self.errors)} erreurs:")
                for error in self.errors[:3]:  # Limiter l'affichage des erreurs
                    self.ui.print_error(f"  • {error}")
                if len(self.errors) > 3:
                    self.ui.print_warning(f"  ... et {len(self.errors) - 3} autres erreurs")
            
            output_dir = self.generator.get_output_directory()
            self.ui.print_info(f"Fichiers sauvegardés dans: {output_dir}")
        else:
            self.ui.print_error("Erreur lors de la génération des fichiers")
    
    def modify_column_selection(self):
        """Permet de modifier la sélection des colonnes"""
        available_columns = self.analysis_result['available_columns']
        detected_columns = self.analysis_result['detected_columns']
        
        new_mapping = self.ui.show_column_selection(available_columns, detected_columns)
        
        # Appliquer les nouveaux mappings seulement s'ils sont différents
        if new_mapping != detected_columns:
            for key, value in new_mapping.items():
                if value:
                    self.analyzer.update_column_mapping(key, value)
            
            # Mettre à jour les résultats
            self.pieces_data = self.analyzer.get_pieces_data()
            self.ui.print_success("Colonnes mises à jour")
    
    def generate_dxf_files(self):
        """Génère les fichiers DXF"""
        if not self.pieces_data:
            self.ui.print_warning("Aucune donnée à traiter. Veuillez d'abord analyser un fichier CSV.")
            self.ui.wait_for_key()
            return
        
        self.ui.clear_screen()
        self.ui.print_banner("Génération DXF", font="small")
        
        self.ui.print_info(f"Génération de {len(self.pieces_data)} fichiers DXF...")
        print()
        
        # Confirmer la génération
        if not self.ui.confirm(f"Confirmer la génération de {len(self.pieces_data)} fichiers DXF?", default=True):
            return
        
        # Génération avec barre de progression
        def generate_thread():
            self.created_files, self.errors = self.generator.create_dxf_files(self.pieces_data)
        
        thread = threading.Thread(target=generate_thread)
        thread.start()
        
        # Barre de progression animée
        while thread.is_alive():
            for i in range(1, 11):
                if not thread.is_alive():
                    break
                self.ui.print_progress_bar(i, 10, 40, 'success')
                time.sleep(0.1)
        
        thread.join()
        print()
        
        # Afficher les résultats
        if hasattr(self, 'created_files'):
            self.ui.print_success(f"Génération terminée: {self.created_files} fichiers créés")
            
            if hasattr(self, 'errors') and self.errors:
                self.ui.print_warning(f"{len(self.errors)} erreurs rencontrées:")
                for error in self.errors[:5]:  # Limiter l'affichage des erreurs
                    self.ui.print_error(f"  • {error}")
                if len(self.errors) > 5:
                    self.ui.print_warning(f"  ... et {len(self.errors) - 5} autres erreurs")
            
            output_dir = self.generator.get_output_directory()
            self.ui.print_info(f"Fichiers sauvegardés dans: {output_dir}")
        else:
            self.ui.print_error("Erreur lors de la génération des fichiers")
        
        self.ui.wait_for_key()
    
    def show_extracted_data(self):
        """Affiche les données extraites"""
        if not self.pieces_data:
            self.ui.print_warning("Aucune donnée à afficher. Veuillez d'abord analyser un fichier CSV.")
            self.ui.wait_for_key()
            return
        
        self.ui.clear_screen()
        self.ui.print_banner("Données Extraites", font="small")
        
        # Préparer les données pour le tableau
        headers = ["Nom", "Longueur", "Largeur", "Code SAP", "Réf. Pièce", "Paquet", "Repère"]
        rows = []
        
        for piece_data in self.pieces_data:
            if len(piece_data) == 4:
                name, length, width, extra_data = piece_data
            else:
                name, length, width = piece_data
                extra_data = {}
            
            row = [
                name[:20] + "..." if len(name) > 20 else name,
                str(length),
                str(width),
                extra_data.get('code_sap', ''),
                extra_data.get('reference_piece', ''),
                extra_data.get('paquet', ''),
                extra_data.get('repere', '')
            ]
            rows.append(row)
        
        # Afficher le tableau
        self.ui.print_table(headers, rows, 'info')
        print()
        
        self.ui.print_info(f"Total: {len(self.pieces_data)} pièces")
        
        if self.current_file:
            self.ui.print_info(f"Fichier source: {os.path.basename(self.current_file)}")
        
        self.ui.wait_for_key()


def main():
    """Fonction principale"""
    try:
        app = TerminalDXFApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrompue.")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur critique: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
