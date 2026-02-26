import os
import ezdxf
from ezdxf.enums import TextEntityAlignment


class DXFGenerator:
    """Module pour la génération de fichiers DXF"""
    
    def __init__(self):
        self.output_dir = "dxf_output"
    
    def create_dxf_files(self, pieces_data):
        """
        Crée les fichiers DXF à partir des données des pièces
        
        Args:
            pieces_data: Liste de tuples (name, length, width, extra_data)
        
        Returns:
            tuple: (nombre_fichiers_créés, liste_erreurs)
        """
        try:
            # Créer le répertoire de sortie s'il n'existe pas
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            created_files = 0
            errors = []
            
            for piece_data in pieces_data:
                try:
                    # Extraire les données selon le format
                    if len(piece_data) == 4:
                        name, length, width, extra_data = piece_data
                    else:
                        name, length, width = piece_data
                        extra_data = {}
                    
                    # Créer le document DXF
                    doc = ezdxf.new('R2010')
                    doc.layers.new('PIECES', dxfattribs={'color': 1})
                    msp = doc.modelspace()
                    
                    # Dessiner le rectangle
                    rectangle_points = [(0, 0), (length, 0), (length, width), (0, width), (0, 0)]
                    msp.add_lwpolyline(rectangle_points, close=True, dxfattribs={'layer': 'PIECES', 'lineweight': 50})
                    
                    # Calculer la taille du texte en fonction des dimensions de la pièce
                    if length < 50 or width < 50:
                        main_text_size = min(4, max(2, min(length, width) * 0.08))
                        info_text_size = max(1.5, min(length, width) * 0.03)
                    else:
                        main_text_size = max(5, min(length, width) * 0.04)
                        info_text_size = max(2, min(length, width) * 0.02)
                    
                    # Positionner tous les textes à l'intérieur de la pièce
                    text_margin = 2
                    current_y = width - text_margin - 2
                    line_spacing = max(info_text_size + 0.5, 2)
                    
                    # Nom de la pièce (au milieu, centré)
                    name_text = msp.add_text(name, dxfattribs={'layer': 'PIECES', 'height': main_text_size})
                    name_text.set_placement((length/2, width/2), align=TextEntityAlignment.MIDDLE_CENTER)
                    
                    # Code SAP (s'il existe)
                    if extra_data.get('code_sap'):
                        sap_text = msp.add_text(f"CODE SAP: {extra_data['code_sap']}", 
                                             dxfattribs={'layer': 'PIECES', 'height': info_text_size})
                        sap_text.set_placement((text_margin, current_y), align=TextEntityAlignment.TOP_LEFT)
                        current_y -= line_spacing
                    
                    # Référence pièce (s'il existe)
                    if extra_data.get('reference_piece'):
                        ref_text = msp.add_text(f"REF: {extra_data['reference_piece']}", 
                                              dxfattribs={'layer': 'PIECES', 'height': info_text_size})
                        ref_text.set_placement((text_margin, current_y), align=TextEntityAlignment.TOP_LEFT)
                        current_y -= line_spacing
                    
                    # Paquet (s'il existe)
                    if extra_data.get('paquet'):
                        paquet_text = msp.add_text(f"PAQUET: {extra_data['paquet']}", 
                                                  dxfattribs={'layer': 'PIECES', 'height': info_text_size})
                        paquet_text.set_placement((text_margin, current_y), align=TextEntityAlignment.TOP_LEFT)
                        current_y -= line_spacing
                    
                    # Repère (s'il existe)
                    if extra_data.get('repere'):
                        repere_text = msp.add_text(f"REPÈRE: {extra_data['repere']}", 
                                                 dxfattribs={'layer': 'PIECES', 'height': info_text_size})
                        repere_text.set_placement((text_margin, current_y), align=TextEntityAlignment.TOP_LEFT)
                        current_y -= line_spacing
                    
                    # Dimensions en bas
                    dim_text = msp.add_text(f"{length} x {width}", 
                                          dxfattribs={'layer': 'PIECES', 'height': info_text_size})
                    dim_text.set_placement((length/2, text_margin), align=TextEntityAlignment.BOTTOM_CENTER)
                    
                    # Sauvegarder le fichier
                    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"{self.output_dir}/{safe_name}_{length}x{width}.dxf"
                    doc.saveas(filename)
                    created_files += 1
                    
                except Exception as e:
                    error_msg = f"Erreur création pièce {piece_data}: {e}"
                    errors.append(error_msg)
                    continue
            
            return created_files, errors
            
        except Exception as e:
            error_msg = f"Erreur génération DXF: {e}"
            return 0, [error_msg]
    
    def get_output_directory(self):
        """Retourne le répertoire de sortie"""
        return self.output_dir
    
    def set_output_directory(self, directory):
        """Définit le répertoire de sortie"""
        self.output_dir = directory
