import os
import hashlib
import time

class File:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.hex_signature = self.get_hex_signature()
        self.modified_time = time.ctime(os.path.getmtime(path))
        self.md5_hash = self.calculate_md5()

    def get_hex_signature(self):
        '''Retourne les 5 premiers octets en hexadécimal'''
        with open(self.path, 'rb') as f:
            first_bytes = f.read(5)
        return ''.join(f'{byte:02x}' for byte in first_bytes)

    def calculate_md5(self):
        '''Calcule le hash MD5 du fichier'''
        hash_md5 = hashlib.md5()
        with open(self.path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def __repr__(self):
        return f"{self.name} | {self.size} octets | {self.hex_signature} | {self.md5_hash} | {self.modified_time}"

def get_all_files(directory):
    '''Liste tous les fichiers d'un répertoire récursivement'''
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_list.append(File(file_path))
            except PermissionError:
                print(f"Permission refusée : {file_path}")
            except Exception as e:
                print(f"Erreur avec {file_path}: {e}")
    return file_list

def find_duplicates(directory):
    '''Détecte les fichiers en doublon'''
    files = get_all_files(directory)
    seen = {}
    duplicates = []
    
    for file in files:
        file_signature = (file.size, file.hex_signature, file.md5_hash)
        if file_signature in seen:
            duplicates.append((file, seen[file_signature]))
        else:
            seen[file_signature] = file
    
    return duplicates

def compare_directories(dir1, dir2):
    '''Compare les fichiers de deux répertoires et identifie les doublons dans dir2'''
    files_dir1 = get_all_files(dir1)
    files_dir2 = get_all_files(dir2)
    
    signatures_dir1 = {(file.size, file.hex_signature, file.md5_hash): file for file in files_dir1}
    duplicates = []
    
    for file in files_dir2:
        file_signature = (file.size, file.hex_signature, file.md5_hash)
        if file_signature in signatures_dir1:
            duplicates.append((file, signatures_dir1[file_signature]))
    
    return duplicates

def get_directory_size_by_type(directory):
    '''Calcule la somme des tailles des fichiers par type'''
    file_types = {
        "texte": {"txt", "doc", "docx", "odt", "csv", "xls", "ppt", "odp"},
        "images": {"jpg", "png", "bmp", "gif", "svg"},
        "vidéo": {"mp4", "avi", "mov", "mpeg", "wmv"},
        "audio": {"mp3", "mp2", "wav", "bwf"},
        "autre": set()
    }
    sizes = {category: 0 for category in file_types}
    
    files = get_all_files(directory)
    for file in files:
        ext = file.name.split(".")[-1].lower()
        category = next((cat for cat, exts in file_types.items() if ext in exts), "autre")
        sizes[category] += file.size
    
    return sizes

def main():
    choice = input("Choisissez une option: (1) Analyser un répertoire, (2) Comparer deux répertoires : ")
    
    if choice == "1":
        directory = input("Entrez le chemin du répertoire à analyser : ")
        duplicates = find_duplicates(directory)
        
        if duplicates:
            print("Fichiers en doublon détectés :")
            for file1, file2 in duplicates:
                print(f"Doublon trouvé : \n  {file1} \n  {file2}\n")
        else:
            print("Aucun doublon trouvé.")
        
        sizes = get_directory_size_by_type(directory)
        print("\nSomme des fichiers par type :")
        for category, size in sizes.items():
            print(f"{category}: {size} octets")
    
    elif choice == "2":
        dir1 = input("Entrez le chemin du premier répertoire : ")
        dir2 = input("Entrez le chemin du second répertoire : ")
        duplicates = compare_directories(dir1, dir2)
        
        if duplicates:
            print("Fichiers en doublon trouvés dans le second répertoire :")
            for file2, file1 in duplicates:
                print(f"Doublon dans {dir2}: {file2} \n  Correspondant dans {dir1}: {file1}\n")
        else:
            print("Aucun doublon trouvé entre les deux répertoires.")

if __name__ == "__main__":
    main()
