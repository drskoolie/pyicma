import re
from anytree import Node

import arabic_reshaper
from bidi.algorithm import get_display


def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)  # Correct letter shapes
    bidi_text = get_display(reshaped_text)  # Apply bidi transformation
    return bidi_text

class Hadith():
    def __init__(self, raw_text, file_path=""):
        self.raw_text = raw_text
        self.file_path = file_path

        self.introductory_words = [
            'حَدَّثَنَا', 'أَخْبَرَنَا', 'سَمِعْتُ', 'ذَكَرَ', 'رَوَى', 
            'قَالَ', 'قَالَ:','عَنْ', 'عَنِ', 'أَنْبَأَنَا', 'يُقَالُ', 'زَعَمَ',
            'أُرِيْنَا', 'يُرْوَى', 'حَدَّثَنِي', 'بَلَغَنَا', 'ثُمَّ',
            'يُحَدِّثُ', 'في', 'حديثه', 'نا', 'قالا:',
        ]
        self.introductory_words = [self.remove_tashkeel(word) for word in self.introductory_words]


        self.isnads, self.matn, self.comment = self.extract_isnads_and_matn(self.raw_text)
        self.narrators = self.extract_narrators(self.isnads)
        self.matn = self.remove_tashkeel(self.matn)
        self.comment = self.remove_tashkeel(self.comment)

    def remove_tashkeel(self, text):
        # Unicode ranges for tashkeel (Arabic diacritics)
        tashkeel_regex = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670]')
        return tashkeel_regex.sub('', text)

    def remove_honorifics(self, text):
     # Define patterns for the phrases
        patterns = [
            r" رضي الله عنه",  # Radya allahu anhu
            r" صلى الله عليه وسلم",  # Salat allah alayhi wasalam
        ]
        
        # Iterate over the patterns and remove each one from the text
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        
        # Return the cleaned text
        return text

    def extract_isnads_and_matn(self, raw_text):
        # Split the text by the new line separating the isnad and matn
        parts = raw_text.strip().split("\n\n")
        
        if len(parts) == 2:
            isnad_section = parts[0]
            matn_section = parts[1]
            comment_section = ""
        elif len(parts) == 3:
            isnad_section = parts[0]
            matn_section = parts[1]
            comment_section = parts[2]

        else:
            isnad_section = ""
            matn_section = raw_text

        # Split the isnad part into individual lines (narrators)
        isnad_lines = isnad_section.strip().split("\n")
        
        return isnad_lines, matn_section, comment_section

    def remove_introductory_words(self, isnad):
        # Split the line into individual words
        words = isnad.split()
        
        # Filter out the words that match any of the common introductory words
        filtered_words = [word for word in words if self.remove_tashkeel(word) not in self.introductory_words]
        
        # Join the remaining words to form the narrator's full name
        narrator_name = ' '.join(filtered_words)
        
        return narrator_name

    def extract_narrators(self, isnads):
        narrators = []
        
        for isnad in isnads:
            # Remove introductory words and extract the narrator's name
            narrator = self.remove_introductory_words(isnad)
            
            # Only add non-empty narrator names
            if narrator:
                narrators.append(narrator)
        
        processed_narrators = self.process_narrators(narrators)
        processed_narrators = [self.remove_tashkeel(narrator) for narrator in processed_narrators]
        processed_narrators = [self.remove_honorifics(narrator) for narrator in processed_narrators]
        processed_narrators = [self.split_narrators_at_wa(narrator) for narrator in processed_narrators]

        return processed_narrators

    def process_narrators(self, narrators):
        processed_narrators = []
        for narrator in narrators:
            if "#" in narrator:
                # Split on hash and use the part after the hash as the actual narrator name
                actual_narrator_name = narrator.split("# ")[1].strip()
                processed_narrators.append(actual_narrator_name)
            else:
                # If no hash, use the full name
                processed_narrators.append(narrator)
        return processed_narrators

    def split_narrators_at_wa(self, text):
        # Check for the pattern where "و" has a space before and after it
        if " و " in text:
            # Split the text into two narrators based on the " و "
            narrators = text.split(" و ")
            return [narrator.strip() for narrator in narrators]  # Return the two narrators as a list
        else:
            return text  # If no " و " with spaces, return the text as a single narrator


    def build_isnad_tree(narrators):
        narrators.reverse()

        # The first narrator will be the root of the tree
        root = Node(narrators[0])
        current_node = root

        # Loop through the remaining narrators and build the chain
        for narrator in narrators[1:]:
            current_node = Node(narrator, parent=current_node)

        return root

    def __str__(self):
        # Build the string representation of the Hadith
        hadith_str = "-----\n"
        if self.file_path:
            hadith_str += f"File Path:\n{self.file_path}\n\n"

        hadith_str += "Narrators:\n"
        for narrator in self.narrators:
            if isinstance(narrator, list):
                my_str = " || ".join(narrator)
                hadith_str += f"{fix_arabic_text(my_str)}\n"
            else:
                hadith_str += f"{fix_arabic_text(narrator)}\n"

        hadith_str += "\nMatn:\n"
        hadith_str += f"{fix_arabic_text(self.matn)}\n"

        if self.comment:
            hadith_str += "\nComment:\n"
            hadith_str += f"{fix_arabic_text(self.comment)}\n"

        hadith_str += "-----\n"
        return hadith_str



if __name__ == "__main__":
    # Example hadith text
    hadith_text = """
    حَدَّثَنَا يُونُسُ قَالَ # يونس بن حبيب
    حَدَّثَنَا أَبُو دَاوُدَ
    قَالَ حَدَّثَنَا شُعْبَةُ
    عَنْ قَتَادَةَ
    عَنْ زُرَارَةَ
    عَنْ أَبِي هُرَيْرَةَ
    عَنِ النَّبِيِّ صلى الله عليه وسلم قَالَ

    إِذَا بَاتَتِ الْمَرْأَةُ هَاجِرَةً لِفِرَاشِ زَوْجِهَا
    لَعَنَتْهَا الْمَلَائِكَةُ حَتَّى تُصْبِحَ أَوْ تُرَاجِعَ

    "شَكَّ أَبُو دَاوُدَ"
    """

    hadith = Hadith(hadith_text, "Test")
    print(hadith)
