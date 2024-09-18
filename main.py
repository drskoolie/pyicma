from anytree import Node, RenderTree

import arabic_reshaper
from bidi.algorithm import get_display

def extract_isnads_and_matn(hadith_text):
    # Split the text by the new line separating the isnad and matn
    parts = hadith_text.strip().split("\n\n", 1)  # Split once at the first empty line
    
    if len(parts) == 2:
        isnad_section = parts[0]
        matn_section = parts[1]
    else:
        isnad_section = ""
        matn_section = hadith_text

    # Split the isnad part into individual lines (narrators)
    isnad_lines = isnad_section.strip().split("\n")
    
    return isnad_lines, matn_section


def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)  # Correct letter shapes
    bidi_text = get_display(reshaped_text)  # Apply bidi transformation
    return bidi_text

def remove_introductory_words(isnad_line):
    # List of common introductory words to remove
    words_to_remove = ['حَدَّثَنَا', 'قَالَ', 'عَنْ', 'عَنِ']
    
    # Split the line into individual words
    words = isnad_line.split()
    
    # Filter out the words that match any of the common introductory words
    filtered_words = [word for word in words if word not in words_to_remove]
    
    # Join the remaining words to form the narrator's full name
    narrator_name = ' '.join(filtered_words)
    
    return narrator_name

def extract_narrators(isnad_lines):
    narrators = []
    
    for line in isnad_lines:
        # Remove introductory words and extract the narrator's name
        narrator = remove_introductory_words(line)
        
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

    isnad_lines, matn = extract_isnads_and_matn(hadith_text)
    narrators = extract_narrators(isnad_lines)

    ## Print
    fixed_isnad_lines = [fix_arabic_text(line) for line in isnad_lines]
    print("Isnad Lines:")
    for fixed_isnad_line in fixed_isnad_lines:
        print(fixed_isnad_line)
    print("Narrators:")
    for narrator in narrators:
        print(fix_arabic_text(narrator))

    isnad_tree = build_isnad_tree(narrators)
    for pre, fill, node in RenderTree(isnad_tree):
        name = fix_arabic_text(node.name)
        print(f"{pre}{name}")
    print("\nMatn:")
    print(fix_arabic_text(matn))

