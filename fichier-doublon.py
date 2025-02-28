import os
import hashlib
import datetime
from collections import defaultdict
import argparse

# 1. Classe File pour représenter un fichier
class File:
    def __init__(self, path):
        """Initialise un objet File à partir du chemin du fichier."""
        self.path = path
        self.name = os.path.basename(path)  # Nom du fichier
        self.size = os.path.getsize(path)   # Taille en octets
        self.first_bytes = self.get_first_bytes()  # 5 premiers octets en hexa
        self.last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))  # Date de dernière modification
        self.md5 = self.calculate_md5()     # Signature MD5

    def get_first_bytes(self):
        """Lit les 5 premiers octets du fichier et les retourne en hexadécimal."""
        try:
            with open(self.path, 'rb') as f:
                bytes_data = f.read(5)
            return bytes_data.hex()
        except Exception as e:
            print(f"Erreur lors de la lecture des premiers octets de {self.path}: {e}")
            return "0000000000"  # Valeur par défaut en cas d’erreur

    def calculate_md5(self):
        """Calcule la signature MD5 du fichier."""
        hash_md5 = hashlib.md5()
        try:
            with open(self.path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Erreur lors du calcul MD5 de {self.path}: {e}")
            return ""  # Valeur par défaut en cas d’erreur

    def __repr__(self):
        """Représentation textuelle de l’objet File."""
        return f"File(name={self.name}, size={self.size}, md5={self.md5})"

# 2. Fonction pour parcourir un répertoire et collecter les fichiers
def get_all_files(directory):
    """Parcourt un répertoire et ses sous-répertoires pour créer une liste d’objets File."""
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                file_obj = File(path)
                file_list.append(file_obj)
            except Exception as e:
                print(f"Erreur lors du traitement de {path}: {e}")
    return file_list

# 3. Fonction pour détecter les doublons dans un seul répertoire
def find_duplicates(file_list):
    """Identifie les groupes de fichiers en doublons en fonction de leur contenu."""
    size_dict = defaultdict(list)
    for file in file_list:
        size_dict[file.size].append(file)

    duplicates = []
    for size, files in size_dict.items():
        if len(files) > 1:
            first_bytes_dict = defaultdict(list)
            for file in files:
                first_bytes_dict[file.first_bytes].append(file)
            for first_bytes, fb_files in first_bytes_dict.items():
                if len(fb_files) > 1:
                    md5_dict = defaultdict(list)
                    for file in fb_files:
                        md5_dict[file.md5].append(file)
                    for md5, md5_files in md5_dict.items():
                        if len(md5_files) > 1:
                            duplicates.append(md5_files)
    return duplicates

# 4. Fonction utilitaire pour déterminer la catégorie d’un fichier
def get_file_category(file_path):
    """Retourne la catégorie du fichier en fonction de son extension."""
    text_extensions = {'txt', 'doc', 'docx', 'odt', 'csv', 'xls', 'ppt', 'odp'}
    image_extensions = {'jpg', 'png', 'bmp', 'gif', 'svg'}
    video_extensions = {'mp4', 'avi', 'mov', 'mpeg', 'wmv'}
    audio_extensions = {'mp3', 'mp2', 'wav', 'bwf'}
    
    extension = os.path.splitext(file_path)[1].lower().lstrip('.')
    if extension in text_extensions:
        return 'texte'
    elif extension in image_extensions:
        return 'images'
    elif extension in video_extensions:
        return 'vidéo'
    elif extension in audio_extensions:
        return 'audio'
    else:
        return 'autre'

# 5. Fonction pour calculer la somme des tailles par catégorie
def calculate_size_by_category(file_list):
    """Calcule la taille totale des fichiers par catégorie."""
    size_by_category = defaultdict(int)
    for file in file_list:
        category = get_file_category(file.path)
        size_by_category[category] += file.size
    return size_by_category

# 6. Fonction pour détecter les doublons dans rep2 par rapport à rep1
def find_duplicates_in_rep2(rep1_files, rep2_files):
    """Identifie les fichiers de rep2 qui sont des doublons par rapport à rep1."""
    rep1_size_dict = defaultdict(list)
    for file in rep1_files:
        rep1_size_dict[file.size].append(file)

    duplicates = []
    for rep2_file in rep2_files:
        if rep2_file.size in rep1_size_dict:
            for rep1_file in rep1_size_dict[rep2_file.size]:
                if rep2_file.md5 == rep1_file.md5:
                    duplicates.append(rep2_file)
                    break
    return duplicates

# 7. Programme principal
def main():
    """Point d’entrée du programme, gère les arguments et lance les analyses."""
    parser = argparse.ArgumentParser(description="Analyse de fichiers dans des répertoires")
    parser.add_argument("directory", nargs='?', help="Chemin du répertoire à analyser")
    parser.add_argument("rep2", nargs='?', help="Chemin du second répertoire pour la comparaison")
    parser.add_argument("--duplicates", action="store_true", help="Détecter les fichiers en doublons dans un répertoire")
    parser.add_argument("--size-by-type", action="store_true", help="Calculer la somme des tailles par type de fichier")
    parser.add_argument("--compare-rep", action="store_true", help="Comparer deux répertoires pour trouver les doublons dans rep2")
    
    args = parser.parse_args()

    if args.compare_rep:
        if not args.directory or not args.rep2:
            print("Usage pour --compare-rep : python script.py rep1 rep2 --compare-rep")
            return
        print(f"Comparaison entre {args.directory} et {args.rep2}")
        rep1_files = get_all_files(args.directory)
        rep2_files = get_all_files(args.rep2)
        duplicates_in_rep2 = find_duplicates_in_rep2(rep1_files, rep2_files)
        if duplicates_in_rep2:
            print("\nFichiers en doublons dans rep2 par rapport à rep1 :")
            for file in duplicates_in_rep2:
                print(f"  - {file.path} (taille: {file.size} octets)")
        else:
            print("Aucun fichier en doublon dans rep2 par rapport à rep1.")
    else:
        if not args.directory:
            print("Usage : python script.py <répertoire> [--duplicates] [--size-by-type] [--compare-rep rep2]")
            return
        print(f"Analyse du répertoire : {args.directory}")
        file_list = get_all_files(args.directory)
        print(f"Nombre de fichiers analysés : {len(file_list)}")

        if args.duplicates:
            duplicates = find_duplicates(file_list)
            if duplicates:
                print("\nDoublons trouvés :")
                for i, group in enumerate(duplicates, 1):
                    print(f"Groupe {i} :")
                    for file in group:
                        print(f"  - {file.path} (taille: {file.size} octets)")
            else:
                print("Aucun doublon trouvé.")

        if args.size_by_type:
            size_by_category = calculate_size_by_category(file_list)
            print("\nSomme des tailles par catégorie :")
            for category, size in size_by_category.items():
                print(f"{category.capitalize()} : {size} octets")

# Lancement du programme
if __name__ == "__main__":
    main()