import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional


class ColumnSelector:
    """Interface tkinter simple pour la sélection des colonnes"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None
        self.confirmed = False
    
    def select_columns(self, available_columns: List[str], detected_columns: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Ouvre une fenêtre tkinter pour la sélection des colonnes
        
        Args:
            available_columns: Liste des colonnes disponibles dans le CSV
            detected_columns: Colonnes détectées automatiquement
        
        Returns:
            Dict[str, str]: Mapping final des colonnes ou None si annulé
        """
        # Créer la fenêtre
        if self.parent:
            self.root = tk.Toplevel(self.parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("Sélection des colonnes")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables pour stocker les sélections
        self.variables = {}
        self.comboboxes = {}
        
        # Créer l'interface
        self.create_widgets(available_columns, detected_columns)
        
        # Centrer la fenêtre
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Attendre la fermeture
        self.root.wait_window()
        
        if self.confirmed:
            return self.result
        else:
            return None
    
    def create_widgets(self, available_columns: List[str], detected_columns: Dict[str, str]):
        """Crée les widgets de l'interface"""
        
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Canvas pour la scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Colonnes obligatoires
        required_frame = ttk.LabelFrame(scrollable_frame, text="Colonnes obligatoires", padding=10)
        required_frame.pack(fill='x', padx=5, pady=5)
        
        required_columns = [
            ("name", "Nom de la pièce", True),
            ("length", "Longueur", True),
            ("width", "Largeur", True)
        ]
        
        for key, label, required in required_columns:
            self.create_column_row(required_frame, key, label, required, available_columns, detected_columns)
        
        # Colonnes optionnelles
        optional_frame = ttk.LabelFrame(scrollable_frame, text="Colonnes optionnelles", padding=10)
        optional_frame.pack(fill='x', padx=5, pady=5)
        
        optional_columns = [
            ("code_sap", "Code SAP", False),
            ("reference_kit", "Référence kit", False),
            ("reference_piece", "Référence pièce", False),
            ("paquet", "Paquet", False),
            ("repere", "Repère", False)
        ]
        
        for key, label, required in optional_columns:
            self.create_column_row(optional_frame, key, label, required, available_columns, detected_columns)
        
        # Boutons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.confirm_selection).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Annuler", command=self.cancel_selection).pack(side='right', padx=5)
        
        # Pack du canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_column_row(self, parent, key: str, label: str, required: bool, 
                       available_columns: List[str], detected_columns: Dict[str, str]):
        """Crée une ligne de sélection de colonne"""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill='x', pady=2)
        
        # Label
        label_text = label + " *" if required else label
        ttk.Label(row_frame, text=label_text, width=20).pack(side='left', padx=5)
        
        # Variable et combobox
        var = tk.StringVar()
        current_value = detected_columns.get(key, "")
        var.set(current_value)
        
        self.variables[key] = var
        
        combobox = ttk.Combobox(row_frame, textvariable=var, 
                              values=[""] + available_columns,
                              state='readonly', width=30)
        combobox.pack(side='left', padx=5, fill='x', expand=True)
        
        self.comboboxes[key] = combobox
        
        # Indicateur visuel pour les colonnes détectées
        if current_value:
            ttk.Label(row_frame, text="✓", foreground="green").pack(side='left', padx=5)
    
    def confirm_selection(self):
        """Confirme la sélection des colonnes"""
        self.result = {}
        
        # Vérifier les colonnes obligatoires
        required_columns = ['name', 'length', 'width']
        missing_required = []
        
        for key in required_columns:
            value = self.variables[key].get().strip()
            if not value:
                missing_required.append(key)
            else:
                self.result[key] = value
        
        if missing_required:
            messagebox.showerror("Erreur", 
                             f"Les colonnes obligatoires suivantes ne sont pas sélectionnées :\n" +
                             ", ".join(missing_required))
            return
        
        # Ajouter les colonnes optionnelles
        optional_columns = ['code_sap', 'reference_kit', 'reference_piece', 'paquet', 'repere']
        for key in optional_columns:
            value = self.variables[key].get().strip()
            if value:
                self.result[key] = value
        
        self.confirmed = True
        self.root.destroy()
    
    def cancel_selection(self):
        """Annule la sélection"""
        self.confirmed = False
        self.root.destroy()


def select_columns_with_tkinter(available_columns: List[str], detected_columns: Dict[str, str]) -> Optional[Dict[str, str]]:
    """
    Fonction utilitaire pour ouvrir le sélecteur de colonnes
    
    Args:
        available_columns: Liste des colonnes disponibles dans le CSV
        detected_columns: Colonnes détectées automatiquement
    
    Returns:
        Dict[str, str]: Mapping final des colonnes ou None si annulé
    """
    try:
        selector = ColumnSelector()
        return selector.select_columns(available_columns, detected_columns)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du sélecteur de colonnes: {e}")
        return None
