import os
import hashlib
import time
import shutil

class File:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.hex_signature = self.get_hex_signature()
        self.modified_time = os.path.getmtime(path)
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
        return f"{self.name} | {self.size} octets | {self.hex_signature} | {self.md5_hash} | {time.ctime(self.modified_time)}"

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

def compare_and_transfer(dir1, dir2):
    '''Compare les fichiers des deux répertoires et copie les fichiers uniques ou plus récents de rep2 vers rep1'''
    files_dir1 = {file.name: file for file in get_all_files(dir1)}
    files_dir2 = get_all_files(dir2)

    files_copied = 0
    for file in files_dir2:
        dest_path = os.path.join(dir1, file.name)

        # Vérifier si le fichier existe déjà dans rep1
        if file.name in files_dir1:
            existing_file = files_dir1[file.name]
            # Remplacement uniquement si le fichier de rep2 est plus récent
            if file.modified_time > existing_file.modified_time:
                print(f"Remplacement de {existing_file.name} par une version plus récente.")
                shutil.copy2(file.path, dest_path)
                files_copied += 1
        else:
            # Fichier absent dans rep1, on le copie
            print(f"Ajout de {file.name} dans {dir1}")
            shutil.copy2(file.path, dest_path)
            files_copied += 1

    print(f"\n{files_copied} fichiers transférés vers {dir1}.")

def main():
    choice = input("Choisissez une option: (1) Analyser un répertoire, (2) Comparer et rapatrier les fichiers : ")
    
    if choice == "1":
        directory = input("Entrez le chemin du répertoire à analyser : ")
        files = get_all_files(directory)

        if files:
            print("Fichiers trouvés :")
            for file in files:
                print(file)
        else:
            print("Aucun fichier trouvé.")
    
    elif choice == "2":
        dir1 = input("Entrez le chemin du répertoire principal (destination) : ")
        dir2 = input("Entrez le chemin du second répertoire (source) : ")
        compare_and_transfer(dir1, dir2)

if __name__ == "__main__":
    main()
