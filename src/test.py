import json
from generate_html import generate_html

def test_generate_html_with_correct_order():
    """
    Test the generate_html function with a sample tree structure and correct placement of matn.
    """
    # Example tree data with narrators and a long matn
    tree_data = [
        {
            "data": {
                "id": "n0",
                "label": "Narrator1",
                "geography": "Madinah"
            }
        },
        {
            "data": {
                "id": "n1",
                "label": "Narrator2",
                "geography": "Makkah"
            }
        },
        {
            "data": {
                "id": "n2",
                "label": "Narrator3",
                "geography": "Basra"
            }
        },
        {
            "data": {
                "id": "matn",
                "label": "إذا باتت المرأة مهاجرة فراش زوجها لعنتها الملائكة حتى تصبح إلا إذا كانت من أمر شرعي أو عذر مقبول.",
                "isMatn": True
            }
        },
        # Define edges to connect narrators and matn
        {
            "data": {
                "source": "n2",
                "target": "n1"  # Connect Narrator3 to Narrator2
            }
        },
        {
            "data": {
                "source": "n1",
                "target": "n0"  # Connect Narrator2 to Narrator1
            }
        },
        {
            "data": {
                "source": "n0",
                "target": "matn"  # Matn is connected to the last narrator (root)
            }
        }
    ]

    # Define geography colors for visualization
    geography_colors = {
        "Madinah": "#A0D2DB",
        "Makkah": "#FFB7C5",
        "Basra": "#F5CBA7",
        "Unknown": "#D3D3D3"
    }

    # Convert tree data to JSON and generate the HTML visualization
    tree_data_json = json.dumps(tree_data, ensure_ascii=False)
    generate_html(tree_data_json, geography_colors)

if __name__ == "__main__":
    # Test the generate_html function with a sample tree and correct matn placement
    test_generate_html_with_correct_order()
