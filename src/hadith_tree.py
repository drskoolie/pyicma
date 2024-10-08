import json
from hadith_database import HadithDatabase
from generate_html import generate_html

class HadithTree:
    def __init__(self, db_name='data/hadith.db'):
        self.db = HadithDatabase(db_name)

    def fetch_all_hadiths(self):
        """
        Fetch all hadiths from the database along with their isnads and matn.
        This will return a list of isnad chains and a list of corresponding matn.
        """
        hadiths = self.db.get_all_hadiths_with_isnad()  # Assuming a function that fetches all hadiths with isnad
        hadith_list = []
        matn_list = []

        for hadith_data in hadiths:
            isnad_chain = hadith_data["isnad"]  # Extract isnad
            matn = hadith_data["matn"]  # Extract matn
            hadith_list.append(isnad_chain)
            matn_list.append(matn)

        return hadith_list, matn_list

    def build_hadith_tree_for_multiple_hadiths(self, hadith_list, matn_list):
        """
        Build a hierarchical tree for multiple hadiths, ensuring shared narrators
        (except for the last child node) do not create duplicate nodes.
        """
        nodes = []
        edges = []
        seen_narrators = {}  # To track narrators that have already been added (except last child)

        for hadith_id, isnad in enumerate(hadith_list):
            matn = matn_list[hadith_id]

            # Sort isnad by position_in_chain in ascending order
            isnad_sorted = sorted(isnad, key=lambda x: x["position_in_chain"], reverse=True)  # Reverse order to treat position 0 as the child

            last_narrator = None  # Track the last narrator to connect it to the matn
            for idx, narrator in enumerate(isnad_sorted):
                narrator_name = narrator["name"]
                narrator_position = narrator["position_in_chain"]

                # Only the last child node should be duplicated
                if narrator_name not in seen_narrators or narrator_position == 0:  # Allow duplication only for the last child node
                    node_id = f"n{narrator_name}_{narrator_position}_{hadith_id}" if narrator_position == 0 else f"n{narrator_name}"
                    
                    node = {
                        "data": {
                            "id": node_id,
                            "label": narrator_name,
                            "geography": narrator["geography"]
                        }
                    }
                    nodes.append(node)
                    
                    # Only add the narrator to seen_narrators if it's not the last child node
                    if narrator_position != 0:  # Do not track the last child node to allow multiple instances
                        seen_narrators[narrator_name] = node_id
                else:
                    node_id = seen_narrators[narrator_name]

                # Add edge from the previous node to the current node
                if last_narrator:
                    edges.append({
                        "data": {
                            "source": last_narrator,
                            "target": node_id
                        }
                    })

                # Update the last narrator
                last_narrator = node_id

            # Add the matn node
            matn_node_id = f"matn_{hadith_id}"
            matn_node = {
                "data": {
                    "id": matn_node_id,
                    "label": matn,
                    "isMatn": True
                }
            }
            nodes.append(matn_node)

            # Connect the matn to the last child narrator
            edges.append({
                "data": {
                    "source": last_narrator,  # Last child node is the source
                    "target": matn_node_id  # Matn is the target
                }
            })

        return nodes + edges

    def generate_tree_from_database(self, geography_colors):
        """
        Fetch all hadiths from the database, build the hierarchical tree, and generate the HTML file.
        """
        # Fetch all hadiths and isnads from the database
        hadith_list, matn_list = self.fetch_all_hadiths()

        # Build the tree with all the hadiths
        tree_data = self.build_hadith_tree_for_multiple_hadiths(hadith_list, matn_list)

        # Pass the tree data to the generate_html function
        generate_html(json.dumps(tree_data, ensure_ascii=False), geography_colors)

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

        # Build a hierarchical structure where the root is the last narrator
        tree_data = self.build_hadith_tree(isnad, matn)
        return tree_data

    def build_hadith_tree(self, isnad, matn):
        """
        Build a hierarchical tree compatible with Cytoscape.js, starting with the child node (position = 0).
        Each node represents a narrator, and edges represent the isnad chain.
        """
        nodes = []
        edges = []

        # Sort isnad by position_in_chain in ascending order
        isnad_sorted = sorted(isnad, key=lambda x: x["position_in_chain"])

        # Group narrators by their position in the isnad
        isnad_by_position = {}
        for idx, narrator in enumerate(isnad_sorted):
            position = narrator['position_in_chain']
            if position not in isnad_by_position:
                isnad_by_position[position] = []
            isnad_by_position[position].append({
                "id": f"n{idx}",
                "name": narrator["name"],
                "geography": narrator["geography"]
            })

        # Create nodes for each narrator, starting from the child
        for position, narrators in isnad_by_position.items():
            for narrator in narrators:
                node = {
                    "data": {
                        "id": narrator["id"],
                        "label": narrator["name"],
                        "geography": narrator["geography"]
                    }
                }
                nodes.append(node)

        # Add edges between nodes at different levels
        positions_sorted = sorted(isnad_by_position.keys())
        for i in range(1, len(positions_sorted)):
            current_position = positions_sorted[i]
            previous_position = positions_sorted[i - 1]

            # Connect all narrators at the current level to the previous level (parent node)
            for current_narrator in isnad_by_position[current_position]:
                for previous_narrator in isnad_by_position[previous_position]:
                    edges.append({
                        "data": {
                            "source": current_narrator["id"],
                            "target": previous_narrator["id"]
                        }
                    })

        # Add a node for the matn (place it visually below the last child)
        matn_node = {
            "data": {
                "id": "matn",
                "label": matn,
                "isMatn": True
            }
        }
        nodes.append(matn_node)

        # Connect the matn to the last position's narrators
        last_position = positions_sorted[0]  # The child node(s) at the lowest position
        for narrator in isnad_by_position[last_position]:
            edges.append({
                "data": {
                    "source": narrator["id"],
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
    # hadith_tree.generate_tree_html(1, geography_colors)
    hadith_tree.generate_tree_from_database(geography_colors)

    # Close the database connection
    hadith_tree.close()
