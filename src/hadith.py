import re
from anytree import Node, RenderTree

import arabic_reshaper
from bidi.algorithm import get_display


def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)  # Correct letter shapes
    bidi_text = get_display(reshaped_text)  # Apply bidi transformation
    return bidi_text

class Hadith():
    def __init__(self, raw_text):
        self.introductory_words = [
            'حَدَّثَنَا', 'أَخْبَرَنَا', 'سَمِعْتُ', 'ذَكَرَ', 'رَوَى', 
            'قَالَ', 'قَالَ:','عَنْ', 'عَنِ', 'أَنْبَأَنَا', 'يُقَالُ', 'زَعَمَ',
            'أُرِيْنَا', 'يُرْوَى', 'حَدَّثَنِي', 'بَلَغَنَا', 'ثُمَّ',
            'يُحَدِّثُ', 'في', 'حديثه', 'نا', 
        ]

        self.introductory_words = [self.remove_tashkeel(word) for word in self.introductory_words]

        self.raw_text = raw_text
        self.isnads, self.matn = self.extract_isnads_and_matn(self.raw_text)
        self.narrators = self.extract_narrators(self.isnads)


    def remove_tashkeel(self, text):
        # Unicode ranges for tashkeel (Arabic diacritics)
        tashkeel_regex = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670]')
        return tashkeel_regex.sub('', text)

    def extract_isnads_and_matn(self, raw_text):
        # Split the text by the new line separating the isnad and matn
        parts = raw_text.strip().split("\n\n", 1)  # Split once at the first empty line
        
        if len(parts) == 2:
            isnad_section = parts[0]
            matn_section = parts[1]
        else:
            isnad_section = ""
            matn_section = raw_text

        # Split the isnad part into individual lines (narrators)
        isnad_lines = isnad_section.strip().split("\n")
        
        return isnad_lines, matn_section

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
        
        return narrators

    def build_isnad_tree(narrators):
        narrators.reverse()

        # The first narrator will be the root of the tree
        root = Node(narrators[0])
        current_node = root

        # Loop through the remaining narrators and build the chain
        for narrator in narrators[1:]:
            current_node = Node(narrator, parent=current_node)

        return root

    def print_hadith(self):
        # Fix and print narrators using fix_arabic_text
        print("Narrators:")
        for narrator in self.narrators:
            print(fix_arabic_text(narrator))

        # Fix and print matn using fix_arabic_text
        print("\nMatn:")
        print(fix_arabic_text(self.matn))


if __name__ == "__main__":
    # Example hadith text
    hadith_text = """
    حَدَّثَنَا يُونُسُ قَالَ
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

    hadith = Hadith(hadith_text)
    hadith.print_hadith()
