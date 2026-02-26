import csv
import requests
import json


class CSVAnalyzer:
    """Module pour l'analyse de fichiers CSV et détection automatique des colonnes"""
    
    def __init__(self):
        self.file_path = ""
        self.available_columns = []
        self.detected_columns = {}
        self.pieces_data = []
    
    def analyze_file(self, file_path):
        """
        Analyse le fichier CSV et détecte automatiquement les colonnes
        
        Args:
            file_path: Chemin vers le fichier CSV
        
        Returns:
            dict: Résultats de l'analyse avec colonnes détectées et données extraites
        """
        self.file_path = file_path
        
        try:
            # Détecter le séparateur et lire les colonnes
            self.available_columns = self._detect_columns(file_path)
            
            # Lire le contenu pour Ollama
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                csv_content = file.read()
            
            # Utiliser Ollama pour la détection automatique
            ollama_result = self._ask_ollama_model(csv_content)
            
            # Initialiser les colonnes détectées
            self.detected_columns = {
                'name': None,
                'length': None,
                'width': None,
                'code_sap': None,
                'reference_kit': None,
                'reference_piece': None,
                'paquet': None,
                'repere': None
            }
            
            # Utiliser les résultats d'Ollama si disponibles et valides
            if ollama_result and ollama_result.get('name_column') and ollama_result.get('length_column') and ollama_result.get('width_column'):
                self._apply_ollama_results(ollama_result)
            else:
                # Fallback : détection manuelle
                self._manual_column_detection()
            
            # Extraire les données
            self._extract_data()
            
            return {
                'available_columns': self.available_columns,
                'detected_columns': self.detected_columns,
                'pieces_data': self.pieces_data,
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _calculate_similarity(self, str1, str2):
        """Calcule la similarité entre deux chaînes (ratio de Levenshtein simplifié)"""
        if str1 == str2:
            return 1.0
        
        # Similarité basique : longueur commune / longueur moyenne
        common_chars = set(str1.lower()) & set(str2.lower())
        total_chars = set(str1.lower()) | set(str2.lower())
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)
    
    def _detect_columns(self, file_path):
        """Détecte le séparateur et extrait les noms de colonnes"""
        with open(file_path, 'r', encoding='utf-8-sig') as file:  # utf-8-sig pour supprimer le BOM
            first_line = file.readline().strip()
            file.seek(0)
            
            # Vérifier si c'est un CSV spécial (tout sur une ligne)
            if ';' in first_line and len(first_line.split(';')) >= 6:
                # Mode spécial : tout sur une ligne avec ; comme séparateur
                # Détecter automatiquement les noms de colonnes
                parts = [part.strip() for part in first_line.split(';')]
                if len(parts) >= 7:
                    return parts[:8]  # Prendre les 8 premières colonnes
                else:
                    return ['LONGUEUR', 'nom des pièces', 'LARGEUR', 'Code SAP', 'référence kit', 'repère', 'paquet', 'référence pièce']
            
            # Mode normal : détection du séparateur
            for separator in [';', ',', '\t']:
                try:
                    reader = csv.reader(file, delimiter=separator)
                    columns = next(reader)
                    if len(columns) > 1:
                        return [col.strip() for col in columns]
                except:
                    file.seek(0)
                    continue
            
            # Séparateur par défaut
            file.seek(0)
            reader = csv.reader(file)
            return [col.strip() for col in next(reader)]
    
    def _ask_ollama_model(self, csv_content, model="gpt-oss:20b"):
        """Utilise Ollama pour détecter automatiquement les colonnes"""
        prompt = f"""
Analyse ce CSV et identifie les colonnes pour créer des fichiers DXF.

Contenu CSV:
{csv_content}

INSTRUCTIONS IMPORTANTES:
- Les colonnes peuvent être dans n'importe quel ordre
- Le séparateur est probablement le point-virgule (;)
- Il faut trouver les VRAIS noms de colonnes exacts comme ils apparaissent dans le CSV
- Retourner SEULEMENT le JSON demandé, sans explication

COLONNES À IDENTIFIER (ordre indifférent):
1. Nom de la pièce: cherche "nom des pièces", "blaze des pièces", "pièce", "désignation" ou similaire
2. Longueur: cherche "LONGUEUR", "longueur", "long" ou similaire  
3. Largeur: cherche "LARGEUR", "largeur", "larg" ou similaire
4. Code SAP: cherche "Code SAP", "CODE SAP", "code sap" ou similaire
5. Référence kit: cherche "référence kit", "ref kit", "reference kit" ou similaire
6. Référence pièce: cherche "référence pièce", "ref pièce", "reference pièce" ou similaire
7. Paquet: cherche "paquet", "lot" ou similaire
8. Repère: cherche "repère", "repere", "position" ou similaire

EXTRAIT LES NOMS EXACTS des colonnes du CSV (avec espaces et majuscules/minuscules comme dans le fichier).

Retourne OBLIGATOIREMENT ce JSON exact:
{{
    "name_column": "nom_exact_colonne_piece",
    "length_column": "nom_exact_colonne_longueur", 
    "width_column": "nom_exact_colonne_largeur",
    "code_sap_column": "nom_exact_colonne_code_sap",
    "reference_kit_column": "nom_exact_colonne_ref_kit",
    "reference_piece_column": "nom_exact_colonne_ref_piece",
    "paquet_column": "nom_exact_colonne_paquet",
    "repere_column": "nom_exact_colonne_repere"
}}

RÈGLE FINALE: Utiliser UNIQUEMENT les noms exacts des colonnes trouvées dans le CSV. Si une colonne n'existe pas, mettre null.
"""
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                try:
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_text[start_idx:end_idx]
                        return json.loads(json_str)
                    else:
                        return None
                        
                except json.JSONDecodeError:
                    return None
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    def _apply_ollama_results(self, ollama_result):
        """Applique les résultats de l'analyse Ollama"""
        if ollama_result.get('name_column'):
            self.detected_columns['name'] = ollama_result['name_column']
        if ollama_result.get('length_column'):
            self.detected_columns['length'] = ollama_result['length_column']
        if ollama_result.get('width_column'):
            self.detected_columns['width'] = ollama_result['width_column']
        if ollama_result.get('code_sap_column'):
            self.detected_columns['code_sap'] = ollama_result['code_sap_column']
        if ollama_result.get('reference_kit_column'):
            self.detected_columns['reference_kit'] = ollama_result['reference_kit_column']
        if ollama_result.get('reference_piece_column'):
            self.detected_columns['reference_piece'] = ollama_result['reference_piece_column']
        if ollama_result.get('paquet_column'):
            self.detected_columns['paquet'] = ollama_result['paquet_column']
        if ollama_result.get('repere_column'):
            self.detected_columns['repere'] = ollama_result['repere_column']
    
    def _manual_column_detection(self):
        """Détection manuelle des colonnes basée sur les noms connus"""
        for col in self.available_columns:
            col_clean = col.strip().lower()
            if 'blaze' in col_clean or 'pièce' in col_clean or 'solide' in col_clean or 'nom' in col_clean:
                self.detected_columns['name'] = col.strip()
            elif 'longueur' in col_clean or 'long' in col_clean:
                self.detected_columns['length'] = col.strip()
            elif 'largeur' in col_clean or 'larg' in col_clean:
                self.detected_columns['width'] = col.strip()
            elif 'code sap' in col_clean or 'sap' in col_clean:
                self.detected_columns['code_sap'] = col.strip()
            elif 'référence kit' in col_clean or 'kit' in col_clean:
                self.detected_columns['reference_kit'] = col.strip()
            elif 'référence pièce' in col_clean or 'ref pièce' in col_clean:
                self.detected_columns['reference_piece'] = col.strip()
            elif 'paquet' in col_clean:
                self.detected_columns['paquet'] = col.strip()
            elif 'repère' in col_clean or 'repere' in col_clean:
                self.detected_columns['repere'] = col.strip()
    
    def _extract_special_csv_data(self):
        """Extrait les données du format CSV spécial (tout sur une ligne)"""
        self.pieces_data = []
        
        with open(self.file_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
            
            # Ignorer la première ligne si elle contient les en-têtes
            data_lines = lines[1:] if len(lines) > 1 else lines
            
            for index, line in enumerate(data_lines):
                line = line.strip()
                if not line:
                    continue
                
                # Parser la ligne manuellement
                parts = [part.strip() for part in line.split(';')]
                
                if len(parts) >= 7:
                    try:
                        length = float(parts[1])      # LONGUEUR (index 1)
                        name = parts[0]              # noms des parallélogrammes (index 0)
                        width = float(parts[2])      # LARGEUR (index 2)
                        code_sap = parts[3]         # Code SAP (index 3)
                        reference_kit = parts[4]     # référence kit (index 4)
                        repere = parts[5]           # repère (index 5)
                        paquet = parts[6]           # paquet (index 6)
                        reference_piece = parts[7] if len(parts) > 7 else ''  # référence pièce (index 7)
                        
                        # Créer les données extra
                        extra_data = {
                            'code_sap': code_sap,
                            'reference_kit': reference_kit,
                            'repere': repere,
                            'paquet': paquet,
                            'reference_piece': reference_piece
                        }
                        
                        if name and length > 0 and width > 0:
                            self.pieces_data.append((name, length, width, extra_data))
                            
                    except (ValueError, TypeError):
                        continue  # Ignorer silencieusement les erreurs de conversion
                    except Exception:
                        continue  # Ignorer silencieusement les autres erreurs
    
    def _extract_data(self):
        """Extrait les données du CSV en utilisant les colonnes détectées"""
        try:
            # Vérifier si c'est le format spécial CSV
            if len(self.available_columns) >= 7 and any('LONGUEUR' in col for col in self.available_columns):
                self._extract_special_csv_data()
                # Mettre à jour les colonnes détectées avec les vrais noms
                self.detected_columns = {
                    'name': self.available_columns[0] if len(self.available_columns) > 0 else 'noms des solides',
                    'length': self.available_columns[1],
                    'width': self.available_columns[2] if len(self.available_columns) > 2 else 'LARGEUR',
                    'code_sap': self.available_columns[3] if len(self.available_columns) > 3 else 'Code SAP',
                    'reference_kit': self.available_columns[4] if len(self.available_columns) > 4 else 'référence kit',
                    'repere': self.available_columns[5] if len(self.available_columns) > 5 else 'repère',
                    'paquet': self.available_columns[6] if len(self.available_columns) > 6 else 'paquet',
                    'reference_piece': self.available_columns[7] if len(self.available_columns) > 7 else 'référence pièce'
                }
                return
            
            # Mode normal : traitement CSV standard
            # Créer un mapping de correspondance des colonnes
            column_mapping = {}
            
            # Fonction pour trouver la meilleure correspondance
            def find_best_match(target_col, available_cols):
                for detected_col in available_cols:
                    if detected_col and target_col and detected_col.lower() == target_col.lower():
                        return detected_col
                return None
            
            # Mapper les colonnes détectées avec les vraies colonnes
            for key, detected_col in self.detected_columns.items():
                if detected_col:
                    mapped_col = find_best_match(detected_col, self.available_columns)
                    if not mapped_col:
                        # Mapping flexible : ignorer les espaces et la casse
                        for available_col in self.available_columns:
                            if (detected_col.lower().strip() == available_col.lower().strip() or
                                detected_col.replace(' ', '').lower() == available_col.replace(' ', '').lower() or
                                detected_col.replace('_', '').lower() == available_col.replace('_', '').lower()):
                                mapped_col = available_col
                                print(f"Mapping flexible: '{detected_col}' -> '{available_col}'")
                                break
                    
                    if mapped_col:
                        column_mapping[key] = mapped_col
                    else:
                        print(f"ERREUR: Impossible de mapper '{detected_col}' vers les colonnes disponibles")
                        print(f"Colonnes disponibles: {self.available_columns}")
                        # Pour le debug, montrer les correspondances possibles
                        for available_col in self.available_columns:
                            similarity = self._calculate_similarity(detected_col.lower(), available_col.lower())
                            if similarity > 0.5:  # Seuil de similarité
                                print(f"  Similarité {similarity:.2f}: '{detected_col}' <-> '{available_col}'")
            
            # Vérifier que les colonnes obligatoires sont présentes
            required_cols = ['name', 'length', 'width']
            missing_cols = [col for col in required_cols if col not in column_mapping]
            
            if missing_cols:
                print(f"Colonnes obligatoires manquantes: {missing_cols}")
                return
            
            print(f"Mapping des colonnes: {column_mapping}")
            
            # Lire toutes les données du CSV
            self.pieces_data = []
            with open(self.file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for index, row in enumerate(reader):
                    try:
                        # Extraire et valider les données obligatoires
                        name = str(row[column_mapping['name']]).strip()
                        
                        # Essayer de convertir les dimensions en nombres
                        try:
                            length = float(row[column_mapping['length']])
                        except (ValueError, TypeError):
                            print(f"Erreur ligne {index}: impossible de convertir la longueur '{row[column_mapping['length']]}' en nombre")
                            continue
                        
                        try:
                            width = float(row[column_mapping['width']])
                        except (ValueError, TypeError):
                            print(f"Erreur ligne {index}: impossible de convertir la largeur '{row[column_mapping['width']]}' en nombre")
                            continue
                        
                        # Valider que les dimensions sont positives
                        if length <= 0 or width <= 0:
                            print(f"Erreur ligne {index}: dimensions invalides ({length}x{width})")
                            continue
                        
                        # Ajouter les données de disposition si disponibles
                        extra_data = {}
                        for key in ['code_sap', 'reference_kit', 'reference_piece', 'paquet', 'repere']:
                            if key in column_mapping and column_mapping[key] in row:
                                extra_data[key] = str(row[column_mapping[key]]).strip()
                        
                        if name and length > 0 and width > 0:
                            self.pieces_data.append((name, length, width, extra_data))
                            print(f"Pièce ajoutée: {name} ({length}x{width})")
                        else:
                            print(f"Pièce ignorée: name='{name}', length={length}, width={width}")
                    
                    except Exception as e:
                        print(f"Erreur ligne {index}: {e}")
                        continue
            
            print(f"Total pièces extraites: {len(self.pieces_data)}")
            
            # Mettre à jour les colonnes détectées avec les noms corrigés
            for key, value in column_mapping.items():
                self.detected_columns[key] = value
                
        except Exception as e:
            print(f"Erreur extraction automatique: {e}")
    
    def update_column_mapping(self, column_key, column_name):
        """
        Met à jour manuellement le mapping d'une colonne et ré-extrait les données
        
        Args:
            column_key: Clé de la colonne ('name', 'length', etc.)
            column_name: Nom de la colonne dans le CSV
        """
        if column_name in self.available_columns:
            self.detected_columns[column_key] = column_name
            self._extract_data()
            return True
        return False
    
    def get_available_columns(self):
        """Retourne la liste des colonnes disponibles"""
        return self.available_columns
    
    def get_detected_columns(self):
        """Retourne les colonnes détectées"""
        return self.detected_columns
    
    def get_pieces_data(self):
        """Retourne les données des pièces extraites"""
        return self.pieces_data
