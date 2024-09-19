import json
from hadith_database import HadithDatabase
from generate_html import generate_html

class HadithTree:
    def __init__(self, db_name='data/hadith.db'):
        self.db = HadithDatabase(db_name)

    def fetch_hadith_tree_data(self, hadith_id):
        """
        Query the hadith and isnad from the database and format it into a Cytoscape.js compatible JSON structure.
        """
        hadith_data = self.db.get_hadith_with_isnad(hadith_id)

        if not hadith_data:
            raise ValueError(f"No hadith found for id {hadith_id}")

        # Extract matn and comment from the first row
        matn = hadith_data[0][0]

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
        Build a hierarchical tree compatible with Cytoscape.js.
        Each node represents a narrator, and edges represent the isnad chain.
        """
        # Define the root node (Prophet)
        nodes = []
        edges = []

        # Create nodes for each narrator
        for idx, narrator in enumerate(isnad):
            node = {
                "data": {
                    "id": f"n{idx}",
                    "label": narrator["name"],
                    "geography": narrator["geography"]
                }
            }
            nodes.append(node)

            # Add edge to the previous narrator (linking them)
            if idx > 0:
                edges.append({
                    "data": {
                        "source": f"n{idx - 1}",
                        "target": f"n{idx}"
                    }
                })

        # Add a node for the matn (at the end of the isnad)
        matn_node = {
            "data": {
                "id": "matn",
                "label": matn,
                "isMatn": True
            }
        }
        nodes.append(matn_node)

        # Connect the last narrator to the matn node
        if nodes:
            last_narrator_id = nodes[-2]["data"]["id"]
            edges.append({
                "data": {
                    "source": last_narrator_id,
                    "target": "matn"
                }
            })

        # Return the combined nodes and edges for Cytoscape.js
        return nodes + edges

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
