import os
import re

from hadith import Hadith

def load_hadith_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_hadiths():
    hadith_dir = os.path.join(os.path.dirname(__file__), '..', 'hadiths')
    hadith_paths =  sorted(os.listdir(hadith_dir), key=lambda x: int(re.search(r'\d+', x).group()))

    hadiths = []
    for hadith_path in hadith_paths:
        if hadith_path.endswith('.txt'):
            file_path = os.path.join(hadith_dir, hadith_path)
            hadith_text = load_hadith_from_file(file_path)
            hadith = Hadith(hadith_text, hadith_path)
            hadiths.append(hadith)

    return hadiths

if __name__ == "__main__":
    # Directory containing the hadith text files
    hadiths = generate_hadiths()
    for hadith in hadiths:
        hadith.print()

