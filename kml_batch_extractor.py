#!/usr/bin/env python3
"""
Extracteur batch de fichiers KML
Traite tous les fichiers KML d'un répertoire
"""

import xml.etree.ElementTree as ET
import csv
import json
import os
import glob
from typing import List, Dict, Tuple


class KMLExtractor:
    """Classe pour extraire et exporter les données KML"""
    
    def __init__(self, kml_file_path: str):
        self.kml_file_path = kml_file_path
        self.namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
        self.data = []
        
    def parse_kml(self) -> List[Dict]:
        """Parse le fichier KML et extrait les données"""
        try:
            tree = ET.parse(self.kml_file_path)
            root = tree.getroot()
            
            placemarks = []
            
            for placemark in root.findall('.//kml:Placemark', self.namespace):
                placemark_data = {}
                
                name = placemark.find('kml:name', self.namespace)
                placemark_data['name'] = name.text if name is not None else 'Sans nom'
                
                description = placemark.find('kml:description', self.namespace)
                placemark_data['description'] = description.text if description is not None else ''
                
                coordinates = []
                
                polygon = placemark.find('.//kml:Polygon', self.namespace)
                if polygon is not None:
                    coords_text = polygon.find('.//kml:coordinates', self.namespace)
                    if coords_text is not None:
                        coordinates = self._parse_coordinates(coords_text.text)
                        placemark_data['geometry_type'] = 'Polygon'
                
                linestring = placemark.find('.//kml:LineString', self.namespace)
                if linestring is not None:
                    coords_text = linestring.find('kml:coordinates', self.namespace)
                    if coords_text is not None:
                        coordinates = self._parse_coordinates(coords_text.text)
                        placemark_data['geometry_type'] = 'LineString'
                
                point = placemark.find('.//kml:Point', self.namespace)
                if point is not None:
                    coords_text = point.find('kml:coordinates', self.namespace)
                    if coords_text is not None:
                        coordinates = self._parse_coordinates(coords_text.text)
                        placemark_data['geometry_type'] = 'Point'
                
                placemark_data['coordinates'] = coordinates
                placemark_data['num_points'] = len(coordinates)
                
                if coordinates and placemark_data.get('geometry_type') == 'Polygon':
                    centroid = self._calculate_centroid(coordinates)
                    placemark_data['centroid_lon'] = centroid[0]
                    placemark_data['centroid_lat'] = centroid[1]
                
                placemarks.append(placemark_data)
            
            self.data = placemarks
            return placemarks
        except Exception as e:
            print(f"Erreur lors du parsing de {self.kml_file_path}: {e}")
            return []
    
    def _parse_coordinates(self, coords_text: str) -> List[Tuple[float, float, float]]:
        """Parse le texte de coordonnées KML"""
        coordinates = []
        coords_text = coords_text.strip()
        
        for coord in coords_text.split():
            coord = coord.strip()
            if coord:
                parts = coord.split(',')
                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])
                        alt = float(parts[2]) if len(parts) > 2 else 0.0
                        coordinates.append((lon, lat, alt))
                    except ValueError:
                        continue
        
        return coordinates
    
    def _calculate_centroid(self, coordinates: List[Tuple[float, float, float]]) -> Tuple[float, float]:
        """Calcule le centroïde d'un polygone"""
        if not coordinates:
            return (0.0, 0.0)
        
        lon_sum = sum(coord[0] for coord in coordinates)
        lat_sum = sum(coord[1] for coord in coordinates)
        n = len(coordinates)
        
        return (lon_sum / n, lat_sum / n)
    
    def export_to_csv(self, output_file: str):
        """Exporte les données vers un fichier CSV"""
        if not self.data:
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            meta_writer = csv.writer(csvfile)
            meta_writer.writerow(['Nom', 'Description', 'Type de géométrie', 'Nombre de points', 
                                 'Centroid Longitude', 'Centroid Latitude'])
            
            for item in self.data:
                meta_writer.writerow([
                    item.get('name', ''),
                    item.get('description', ''),
                    item.get('geometry_type', ''),
                    item.get('num_points', 0),
                    item.get('centroid_lon', ''),
                    item.get('centroid_lat', '')
                ])
        
        coords_file = output_file.replace('.csv', '_coordinates.csv')
        with open(coords_file, 'w', newline='', encoding='utf-8') as csvfile:
            coords_writer = csv.writer(csvfile)
            coords_writer.writerow(['Nom du Placemark', 'Point #', 'Longitude', 'Latitude', 'Altitude'])
            
            for item in self.data:
                name = item.get('name', '')
                for idx, coord in enumerate(item.get('coordinates', []), 1):
                    coords_writer.writerow([name, idx, coord[0], coord[1], coord[2]])
    
    def export_to_txt(self, output_file: str):
        """Exporte les données vers un fichier TXT formaté"""
        if not self.data:
            return
        
        with open(output_file, 'w', encoding='utf-8') as txtfile:
            txtfile.write("=" * 80 + "\n")
            txtfile.write("EXTRACTION DE DONNÉES KML\n")
            txtfile.write("=" * 80 + "\n\n")
            txtfile.write(f"Fichier source: {os.path.basename(self.kml_file_path)}\n")
            txtfile.write(f"Nombre de placemarks: {len(self.data)}\n")
            txtfile.write("=" * 80 + "\n\n")
            
            for idx, item in enumerate(self.data, 1):
                txtfile.write(f"\n{'=' * 80}\n")
                txtfile.write(f"PLACEMARK #{idx}: {item.get('name', 'Sans nom')}\n")
                txtfile.write(f"{'=' * 80}\n\n")
                
                txtfile.write(f"Type de géométrie: {item.get('geometry_type', 'N/A')}\n")
                txtfile.write(f"Nombre de points: {item.get('num_points', 0)}\n")
                
                if item.get('description'):
                    txtfile.write(f"Description: {item.get('description')}\n")
                
                if 'centroid_lon' in item:
                    txtfile.write(f"Centroïde: ({item['centroid_lon']:.8f}, {item['centroid_lat']:.8f})\n")
                
                txtfile.write(f"\nCOORDONNÉES ({len(item.get('coordinates', []))} points):\n")
                txtfile.write("-" * 80 + "\n")
                txtfile.write(f"{'#':<6} {'Longitude':<18} {'Latitude':<18} {'Altitude':<12}\n")
                txtfile.write("-" * 80 + "\n")
                
                for point_idx, coord in enumerate(item.get('coordinates', []), 1):
                    txtfile.write(f"{point_idx:<6} {coord[0]:<18.10f} {coord[1]:<18.10f} {coord[2]:<12.2f}\n")
                
                txtfile.write("\n")
    
    def export_to_excel_csv(self, output_file: str):
        """Exporte vers un format CSV compatible Excel"""
        if not self.data:
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Nom', 'Description', 'Type', 'Nb Points', 
                           'Centroid Lon', 'Centroid Lat'])
            
            for item in self.data:
                writer.writerow([
                    item.get('name', ''),
                    item.get('description', ''),
                    item.get('geometry_type', ''),
                    item.get('num_points', 0),
                    str(item.get('centroid_lon', '')).replace('.', ','),
                    str(item.get('centroid_lat', '')).replace('.', ',')
                ])
        
        coords_file = output_file.replace('.csv', '_coordinates.csv')
        with open(coords_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Nom', 'Point', 'Longitude', 'Latitude', 'Altitude'])
            
            for item in self.data:
                name = item.get('name', '')
                for idx, coord in enumerate(item.get('coordinates', []), 1):
                    writer.writerow([
                        name, 
                        idx, 
                        str(coord[0]).replace('.', ','),
                        str(coord[1]).replace('.', ','),
                        str(coord[2]).replace('.', ',')
                    ])
    
    def export_to_json(self, output_file: str):
        """Exporte les données vers un fichier JSON"""
        if not self.data:
            return
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.data, jsonfile, indent=2, ensure_ascii=False)


def process_directory(directory_path: str, output_dir: str = None, export_format: str = 'all'):
    """
    Traite tous les fichiers KML d'un répertoire
    
    Args:
        directory_path: Chemin du répertoire contenant les fichiers KML
        output_dir: Répertoire de sortie (par défaut: sous-dossier 'output' dans le répertoire source)
        export_format: Format d'export (csv, txt, excel, json, all)
    """
    if not os.path.exists(directory_path):
        print(f"Erreur: Le répertoire '{directory_path}' n'existe pas.")
        return
    
    if output_dir is None:
        output_dir = os.path.join(directory_path, 'kml_output')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    kml_files = glob.glob(os.path.join(directory_path, '*.kml'))
    
    if not kml_files:
        print(f"Aucun fichier KML trouvé dans {directory_path}")
        return
    
    print(f"\n{'=' * 80}")
    print(f"Traitement de {len(kml_files)} fichier(s) KML")
    print(f"Répertoire source: {directory_path}")
    print(f"Répertoire de sortie: {output_dir}")
    print(f"{'=' * 80}\n")
    
    total_placemarks = 0
    total_points = 0
    
    for idx, kml_file in enumerate(kml_files, 1):
        filename = os.path.basename(kml_file)
        base_name = os.path.splitext(filename)[0]
        
        print(f"[{idx}/{len(kml_files)}] Traitement de {filename}...")
        
        extractor = KMLExtractor(kml_file)
        data = extractor.parse_kml()
        
        if not data:
            print(f"  ⚠️  Aucune donnée extraite de {filename}")
            continue
        
        num_placemarks = len(data)
        num_points = sum(item.get('num_points', 0) for item in data)
        total_placemarks += num_placemarks
        total_points += num_points
        
        print(f"  ✓ {num_placemarks} placemark(s), {num_points} point(s)")
        
        if export_format in ['csv', 'all']:
            output_file = os.path.join(output_dir, f"{base_name}_data.csv")
            extractor.export_to_csv(output_file)
        
        if export_format in ['txt', 'all']:
            output_file = os.path.join(output_dir, f"{base_name}_data.txt")
            extractor.export_to_txt(output_file)
        
        if export_format in ['excel', 'all']:
            output_file = os.path.join(output_dir, f"{base_name}_excel.csv")
            extractor.export_to_excel_csv(output_file)
        
        if export_format in ['json', 'all']:
            output_file = os.path.join(output_dir, f"{base_name}_data.json")
            extractor.export_to_json(output_file)
    
    print(f"\n{'=' * 80}")
    print(f"✅ Traitement terminé!")
    print(f"Total: {len(kml_files)} fichiers, {total_placemarks} placemarks, {total_points} points")
    print(f"Résultats dans: {output_dir}")
    print(f"{'=' * 80}\n")


def main():
    """Fonction principale"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python kml_batch_extractor.py <repertoire> [repertoire_sortie] [format]")
        print("Formats disponibles: csv, txt, excel, json, all (défaut: all)")
        print("\nExemples:")
        print("  python kml_batch_extractor.py ./mes_fichiers_kml")
        print("  python kml_batch_extractor.py ./mes_fichiers_kml ./resultats")
        print("  python kml_batch_extractor.py ./mes_fichiers_kml ./resultats csv")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    export_format = sys.argv[3].lower() if len(sys.argv) > 3 else 'all'
    
    # Si output_dir ressemble à un format, c'est probablement le format
    if output_dir and output_dir.lower() in ['csv', 'txt', 'excel', 'json', 'all']:
        export_format = output_dir.lower()
        output_dir = None
    
    process_directory(directory_path, output_dir, export_format)


if __name__ == "__main__":
    main()