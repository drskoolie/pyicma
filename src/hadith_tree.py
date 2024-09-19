import json
from hadith_database import HadithDatabase
from generate_html import generate_html

class HadithTree:
    def __init__(self, db_name='data/hadith.db'):
        self.db = HadithDatabase(db_name)

    def fetch_hadith_tree_data(self, hadith_id):
        """
        Query the hadith and isnad from the database and format it into a JSON structure
        for Cytoscape.js visualization, including geography and position information.
        """
        hadith_data = self.db.get_hadith_with_isnad(hadith_id)

        if not hadith_data:
            raise ValueError(f"No hadith found for id {hadith_id}")

        # Extract matn and comment from the first row
        matn = hadith_data[0][0]
        comment = hadith_data[0][1] if hadith_data[0][1] else ""

        # Extract the isnad chain (narrators' names, locations, and positions)
        isnad = []
        for row in hadith_data:
            narrator_name = row[2]  # Narrator's name
            geography = row[3]  # Narrator's geography
            position = row[4]  # Position in the isnad chain
            isnad.append({"name": narrator_name, "geography": geography, "position_in_chain": position})

        # Build a hierarchical structure where the Prophet is the root
        tree_data = self.build_hadith_tree(isnad, matn)
        return tree_data

    def build_hadith_tree(self, isnad, matn):
        """
        Build the hierarchical tree, starting from the child to the root.
        Narrators at the same level should share the same children, and the matn should be placed only once at the last child.
        """
        # Group narrators by their position in the chain
        isnad_by_position = {}
        for narrator in isnad:
            position = narrator["position_in_chain"]
            if position not in isnad_by_position:
                isnad_by_position[position] = []
            isnad_by_position[position].append(narrator)

        # Start with the lowest position (child) where the matn is located
        last_position = min(isnad_by_position.keys())
        last_narrators = isnad_by_position[last_position]

        # Create the initial node where matn will be stored
        tree_data = {
            "name": last_narrators[0]["name"],
            "geography": last_narrators[0]["geography"],
            "position_in_chain": last_narrators[0]["position_in_chain"],
            "matn": matn,  # Add the matn to the lowest position (child)
            "children": []
        }

        # Shared last node for multiple narrators at the lowest position
        if len(last_narrators) > 1:
            last_node = {
                "name": None,
                "children": [{"name": n["name"], "geography": n["geography"], "position_in_chain": n["position_in_chain"]} for n in last_narrators]
            }
        else:
            last_node = tree_data

        # Traverse upwards from the lowest position to the root
        for position in sorted(isnad_by_position.keys())[1:]:
            narrators_at_position = isnad_by_position[position]
            new_nodes = []
            for narrator in narrators_at_position:
                new_node = {
                    "name": narrator["name"],
                    "geography": narrator["geography"],
                    "position_in_chain": narrator["position_in_chain"],
                    "children": [last_node]  # Shared children for narrators at the same level
                }
                new_nodes.append(new_node)

            # Handle shared children for narrators at the same level
            if len(new_nodes) > 1:
                last_node = {
                    "name": None,
                    "children": new_nodes
                }
            else:
                last_node = new_nodes[0]  # Move up to the next position

        return last_node  # Return the final tree structure

    def generate_tree_html(self, hadith_id, geography_colors):
        """
        Generate the Cytoscape.js HTML visualization for the given hadith_id.
        """
        tree_data = self.fetch_hadith_tree_data(hadith_id)
        tree_data_json = json.dumps(tree_data, ensure_ascii=False)  # Convert to JSON

        # Call the generate_html function to create the HTML file
        generate_html(tree_data_json, geography_colors)

    def close(self):
        """
        Close the database connection.
        """
        self.db.close()


if __name__ == "__main__":
    # Initialize the HadithTree
    hadith_tree = HadithTree()

    # Define geography colors for visualization
    geography_colors = {
        "Madinah": "#A0D2DB",
        "Makkah": "#FFB7C5",
        "Basra": "#F5CBA7",
        "Baghdad": "#C5E3BF",
        "Unknown": "#D3D3D3"
    }

    # Generate tree visualization for a hadith with id 1
    hadith_tree.generate_tree_html(1, geography_colors)

    # Close the database connection
    hadith_tree.close()

