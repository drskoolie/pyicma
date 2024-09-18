import os
import re

from hadith import Hadith

def load_hadith_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

if __name__ == "__main__":
    # Directory containing the hadith text files
    hadith_dir = os.path.join(os.path.dirname(__file__), '..', 'hadiths')
    hadith_paths =  sorted(os.listdir(hadith_dir), key=lambda x: int(re.search(r'\d+', x).group()))

    # Load and process each hadith file
    for hadith_path in hadith_paths:
        if hadith_path.endswith('.txt'):
            file_path = os.path.join(hadith_dir, hadith_path)
            hadith_text = load_hadith_from_file(file_path)
            hadith = Hadith(hadith_text)
            print(f"Processing '{hadith_path}'")
            hadith.print_hadith()
            print("----\n")
