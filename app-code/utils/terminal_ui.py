import os
import sys
import subprocess
from typing import List, Dict, Optional, Tuple
try:
    import pyfiglet as figlet
    import colorama
    from colorama import Fore, Back, Style
    import keyboard
    import time
except ImportError as e:
    print(f"Modules manquants: {e}")
    print("Installez les dépendances avec: pip install pyfiglet colorama keyboard")
    sys.exit(1)

# Import du sélecteur de colonnes tkinter
try:
    from .column_selector import select_columns_with_tkinter
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class TerminalUI:
    """Interface terminal stylisée avec figlet et colorama"""
    
    def __init__(self):
        # Initialiser colorama
        colorama.init(autoreset=True)
        
        # Définir les couleurs
        self.colors = {
            'primary': Fore.CYAN,
            'secondary': Fore.MAGENTA,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'info': Fore.BLUE,
            'reset': Style.RESET_ALL
        }
        
        # Styles de texte
        self.styles = {
            'bold': Style.BRIGHT,
            'dim': Style.DIM,
            'normal': Style.NORMAL
        }
        
        # Caractères de décoration
        self.chars = {
            'horizontal': '═',
            'vertical': '║',
            'corner_tl': '╔',
            'corner_tr': '╗',
            'corner_bl': '╚',
            'corner_br': '╝',
            'cross': '╬',
            't_down': '╦',
            't_up': '╩',
            't_right': '╠',
            't_left': '╣'
        }
    
    def clear_screen(self):
        """Efface l'écran du terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self, text: str, font: str = "slant"):
        """
        Affiche une bannière avec figlet
        
        Args:
            text: Texte à afficher
            font: Police figlet à utiliser
        """
        try:
            banner = figlet.figlet_format(text, font=font)
            print(f"{self.colors['primary']}{banner}{self.colors['reset']}")
        except:
            # Fallback si figlet échoue
            print(f"{self.colors['primary']}{self.styles['bold']}{text.center(50)}{self.colors['reset']}")
    
    def print_box(self, text: str, width: int = 60, color: str = 'primary'):
        """
        Affiche du texte dans une boîte stylisée
        
        Args:
            text: Texte à afficher
            width: Largeur de la boîte
            color: Couleur à utiliser
        """
        lines = text.split('\n')
        color_code = self.colors.get(color, self.colors['primary'])
        
        # Ligne supérieure
        print(f"{color_code}{self.chars['corner_tl']}{self.chars['horizontal'] * (width - 2)}{self.chars['corner_tr']}{self.colors['reset']}")
        
        # Contenu
        for line in lines:
            # Gérer les lignes longues
            if len(line) > width - 4:
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line + word) <= width - 4:
                        current_line += word + " "
                    else:
                        print(f"{color_code}{self.chars['vertical']} {current_line.ljust(width - 4)} {self.chars['vertical']}{self.colors['reset']}")
                        current_line = word + " "
                if current_line:
                    print(f"{color_code}{self.chars['vertical']} {current_line.ljust(width - 4)} {self.chars['vertical']}{self.colors['reset']}")
            else:
                print(f"{color_code}{self.chars['vertical']} {line.ljust(width - 4)} {self.chars['vertical']}{self.colors['reset']}")
        
        # Ligne inférieure
        print(f"{color_code}{self.chars['corner_bl']}{self.chars['horizontal'] * (width - 2)}{self.chars['corner_br']}{self.colors['reset']}")
    
    def print_menu(self, title: str, options: List[str], color: str = 'primary'):
        """
        Affiche un menu stylisé
        
        Args:
            title: Titre du menu
            options: Liste des options
            color: Couleur à utiliser
        
        Returns:
            int: Index de l'option choisie
        """
        self.print_box(title, color=color)
        print()
        
        color_code = self.colors.get(color, self.colors['primary'])
        
        for i, option in enumerate(options, 1):
            print(f"{color_code}[{i}]{self.colors['reset']} {self.styles['bold']}{option}{self.colors['reset']}")
        
        print()
        choice = self.get_input(f"{color_code}Choisissez une option (1-{len(options)}):{self.colors['reset']}")
        
        try:
            choice_int = int(choice)
            if 1 <= choice_int <= len(options):
                return choice_int - 1
            else:
                self.print_error("Choix invalide")
                return self.print_menu(title, options, color)
        except ValueError:
            self.print_error("Veuillez entrer un nombre")
            return self.print_menu(title, options, color)
    
    def get_input(self, prompt: str, color: str = 'info') -> str:
        """
        Demande une entrée utilisateur avec style
        
        Args:
            prompt: Message à afficher
            color: Couleur du prompt
        
        Returns:
            str: Entrée utilisateur
        """
        color_code = self.colors.get(color, self.colors['info'])
        return input(f"{color_code}{prompt}{self.colors['reset']}")
    
    def print_success(self, message: str):
        """Affiche un message de succès"""
        print(f"{self.colors['success']}{self.styles['bold']}✓ {message}{self.colors['reset']}")
    
    def print_error(self, message: str):
        """Affiche un message d'erreur"""
        print(f"{self.colors['error']}{self.styles['bold']}✗ {message}{self.colors['reset']}")
    
    def print_warning(self, message: str):
        """Affiche un message d'avertissement"""
        print(f"{self.colors['warning']}{self.styles['bold']}⚠ {message}{self.colors['reset']}")
    
    def print_info(self, message: str):
        """Affiche un message d'information"""
        print(f"{self.colors['info']}{self.styles['bold']}ℹ {message}{self.colors['reset']}")
    
    def print_list(self, items: List[str], title: str = "", color: str = 'info'):
        """
        Affiche une liste stylisée
        
        Args:
            items: Liste des éléments à afficher
            title: Titre de la liste
            color: Couleur à utiliser
        """
        if title:
            self.print_box(title, color=color)
            print()
        
        color_code = self.colors.get(color, self.colors['info'])
        
        for i, item in enumerate(items, 1):
            print(f"{color_code}• {self.styles['bold']}{item}{self.colors['reset']}")
    
    def print_table(self, headers: List[str], rows: List[List[str]], color: str = 'info'):
        """
        Affiche un tableau stylisé
        
        Args:
            headers: En-têtes des colonnes
            rows: Lignes de données
            color: Couleur à utiliser
        """
        if not rows:
            self.print_warning("Aucune donnée à afficher")
            return
        
        # Calculer la largeur des colonnes
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)
        
        color_code = self.colors.get(color, self.colors['info'])
        
        # Ligne de séparation
        separator = "+" + "+".join("-" * width for width in col_widths) + "+"
        
        print(f"{color_code}{separator}{self.colors['reset']}")
        
        # En-têtes
        header_line = "|"
        for i, header in enumerate(headers):
            header_line += f" {self.styles['bold']}{header.ljust(col_widths[i] - 1)}|{self.colors['reset']}"
        print(f"{color_code}{header_line}{self.colors['reset']}")
        print(f"{color_code}{separator}{self.colors['reset']}")
        
        # Lignes de données
        for row in rows:
            row_line = "|"
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_line += f" {str(cell).ljust(col_widths[i] - 1)}|"
            print(f"{color_code}{row_line}{self.colors['reset']}")
        
        print(f"{color_code}{separator}{self.colors['reset']}")
    
    def print_progress_bar(self, current: int, total: int, width: int = 50, color: str = 'primary'):
        """
        Affiche une barre de progression
        
        Args:
            current: Valeur actuelle
            total: Valeur totale
            width: Largeur de la barre
            color: Couleur de la barre
        """
        percentage = (current / total) * 100 if total > 0 else 0
        filled = int((current / total) * width) if total > 0 else 0
        
        color_code = self.colors.get(color, self.colors['primary'])
        bar = f"{color_code}{'█' * filled}{self.colors['reset']}" + "░" * (width - filled)
        
        print(f"\r{color_code}[{bar}] {percentage:.1f}% ({current}/{total}){self.colors['reset']}", end="", flush=True)
        
        if current == total:
            print()  # Nouvelle ligne à la fin
    
    def wait_for_key(self, message: str = "Appuyez sur Entrée pour continuer..."):
        """Attend une touche de l'utilisateur"""
        input(f"{self.colors['info']}{message}{self.colors['reset']}")
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """
        Demande une confirmation
        
        Args:
            message: Message à afficher
            default: Valeur par défaut
        
        Returns:
            bool: True si l'utilisateur confirme
        """
        default_text = "O/n" if default else "o/N"
        prompt = f"{message} ({default_text}): "
        
        response = self.get_input(prompt, 'warning').lower().strip()
        
        if not response:
            return default
        
        return response.startswith('o') or response.startswith('y')
    
    def open_file_explorer(self, title: str = "Sélectionnez un fichier CSV") -> str:
        """
        Ouvre l'explorateur de fichiers Windows et retourne le chemin sélectionné
        
        Args:
            title: Titre de la boîte de dialogue
        
        Returns:
            str: Chemin du fichier sélectionné ou chaîne vide si annulé
        """
        try:
            # Créer un script PowerShell temporaire pour la boîte de dialogue
            ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title = "{title}"
$dialog.Filter = "Fichiers CSV (*.csv)|*.csv|Tous les fichiers (*.*)|*.*"
$dialog.Multiselect = $false

if ($dialog.ShowDialog() -eq "OK") {{
    Write-Output $dialog.FileName
}} else {{
    Write-Output ""
}}
'''
            
            # Écrire le script temporaire
            temp_file = os.path.join(os.environ.get('TEMP', '.'), 'file_dialog.ps1')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(ps_script)
            
            try:
                # Exécuter le script PowerShell
                result = subprocess.run(
                    ['powershell', '-ExecutionPolicy', 'Bypass', '-File', temp_file],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                # Nettoyer le fichier temporaire
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                # Retourner le résultat nettoyé
                file_path = result.stdout.strip()
                return file_path if file_path and os.path.exists(file_path) else ""
                
            except Exception as e:
                self.print_error(f"Erreur lors de l'ouverture de l'explorateur: {e}")
                return ""
                
        except Exception as e:
            self.print_error(f"Impossible de créer la boîte de dialogue: {e}")
            return ""
    
    def select_file(self, title: str = "Sélectionnez un fichier CSV", use_explorer: bool = True) -> str:
        """
        Interface de sélection de fichier
        
        Args:
            title: Titre de la sélection
            use_explorer: Si True, utilise l'explorateur Windows, sinon demande le chemin
        
        Returns:
            str: Chemin du fichier sélectionné
        """
        self.print_box(title, color='info')
        print()
        
        if use_explorer:
            self.print_info("Ouverture de l'explorateur de fichiers...")
            file_path = self.open_file_explorer(title)
            
            if file_path and file_path.endswith('.csv'):
                self.print_success(f"Fichier sélectionné: {os.path.basename(file_path)}")
                return file_path
            else:
                self.print_warning("Aucun fichier sélectionné ou fichier invalide")
                
                # Proposer d'entrer le chemin manuellement
                if self.confirm("Voulez-vous entrer le chemin manuellement?", default=False):
                    return self.select_file(title, use_explorer=False)
                else:
                    return ""
        else:
            # Saisie manuelle du chemin
            file_path = self.get_input("Entrez le chemin du fichier CSV: ", 'info')
            
            if os.path.exists(file_path) and file_path.endswith('.csv'):
                self.print_success(f"Fichier sélectionné: {os.path.basename(file_path)}")
                return file_path
            else:
                self.print_error("Fichier invalide ou introuvable")
                
                # Proposer de réessayer ou d'utiliser l'explorateur
                options = ["Réessayer", "Utiliser l'explorateur", "Annuler"]
                choice = self.print_menu("Que faire?", options)
                
                if choice == 0:
                    return self.select_file(title, use_explorer=False)
                elif choice == 1:
                    return self.select_file(title, use_explorer=True)
                else:
                    return ""
    
    def show_column_selection(self, available_columns: List[str], detected_columns: Dict[str, str]) -> Dict[str, str]:
        """
        Interface de sélection des colonnes avec Tkinter
        
        Args:
            available_columns: Colonnes disponibles dans le CSV
            detected_columns: Colonnes détectées automatiquement
        
        Returns:
            Dict[str, str]: Mapping final des colonnes
        """
        # Utiliser l'interface Tkinter si disponible
        if TKINTER_AVAILABLE:
            try:
                # Appeler l'interface Tkinter directement
                result = select_columns_with_tkinter(available_columns, detected_columns)
                
                if result:
                    return result
                else:
                    return detected_columns
                    
            except Exception:
                return detected_columns
        else:
            return detected_columns
