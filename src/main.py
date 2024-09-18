import os
from hadith import Hadith

def load_hadith_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

if __name__ == "__main__":
    # Directory containing the hadith text files
    hadiths_dir = os.path.join(os.path.dirname(__file__), '..', 'hadiths')

    # Load and process each hadith file
    for file_name in sorted(os.listdir(hadiths_dir)):
        if file_name.endswith('.txt'):
            file_path = os.path.join(hadiths_dir, file_name)
            hadith_text = load_hadith_from_file(file_path)
            hadith = Hadith(hadith_text)
            print(f"Processing '{file_name}'")
            hadith.print_hadith()
            print("----\n")
