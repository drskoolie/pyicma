import json

def generate_html(tree_data_json, geography_colors):
    """
    Generates an HTML file with Cytoscape.js for visualizing the hadith tree.
    """
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hierarchical Cytoscape.js Example with Matn Nodes</title>
  <script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>
  <script src="https://unpkg.com/dagre/dist/dagre.min.js"></script>
  <script src="https://unpkg.com/cytoscape-dagre/cytoscape-dagre.js"></script>
  <style>
    #cy {{
      width: 100%;
      height: 100vh;
      background-color: #f9f9f9;
    }}

    /* Matn style is defined as a special class */
    .matn-box {{
      background-color: #f0f0f0;
      border: 1px solid #ddd;
      padding: 6px;
      border-radius: 3px;
      font-size: 14px;
      font-family: Arial, sans-serif;
      direction: rtl;  /* For Arabic text */
      text-align: right;
    }}
  </style>
</head>
<body>
  <div id="cy"></div>

  <script>
    // Define colors based on geography
    const geographyColors = {json.dumps(geography_colors)};

    // Function to generate a slightly darker border color
    function darkerColor(color) {{
      const darkerHex = (hex) => Math.max(0, hex - 40).toString(16).padStart(2, '0');  // Darken by 40 (hex)
      const r = darkerHex(parseInt(color.slice(1, 3), 16));
      const g = darkerHex(parseInt(color.slice(3, 5), 16));
      const b = darkerHex(parseInt(color.slice(5, 7), 16));
        
      const darkColor = `#${{r}}${{g}}${{b}}`;  // Format correctly as a hex color
      
      return darkColor;
    }}

    const cy = cytoscape({{
      container: document.getElementById('cy'),  // container to render in
      elements: {tree_data_json},

      layout: {{
        name: 'dagre',  // Hierarchical layout (Dagre)
        rankDir: 'TB',  // Top-to-bottom direction
        nodeSep: 50,  // Space between nodes
        edgeSep: 10,  // Space between edges
        rankSep: 100  // Space between levels
      }},

      style: [
        {{
          selector: 'node',
          style: {{
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': (ele) => geographyColors[ele.data('geography')] || '#D3D3D3',  // Assign color based on geography
            'border-color': function(ele) {{ 
              const geographyColor = geographyColors[ele.data('geography')] || '#D3D3D3';
              return darkerColor(geographyColor);  // Apply the darker color
            }},
            'border-width': 2,
            'shape': 'rectangle',
            'width': '150px',
            'height': '40px',
            'font-family': 'Arial, sans-serif',  // Ensure text looks good for Arabic
            'font-size': '14px',
            'direction': 'rtl',  // Right-to-left direction for Arabic text
            'text-align': 'right'
          }}
        }},
        {{
          selector: 'node[isMatn]',  // Style for matn nodes
          style: {{
            'label': 'data(label)',
            'background-color': '#f0f0f0',  // Light gray background for matn
            'border-color': '#ddd',
            'border-width': 2,
            'shape': 'rectangle',
            'width': '150px',  // Match width to parent node
            'height': function(ele) {{
              const textLength = ele.data('label').length;
              const estimatedLines = Math.ceil(textLength / 30);  // Estimate lines based on 30 chars per line
              const baseHeight = 20;  // Base height for a single line
              const buffer = 1.2;  // 20% buffer for additional space
              return (baseHeight * estimatedLines * buffer) + 'px';  // Calculate dynamic height
            }},
            'font-family': 'Arial, sans-serif',
            'font-size': '14px',
            'direction': 'rtl',  // Right-to-left for Arabic text
            'text-halign': 'center',  // Ensure text is aligned to the right within the box
            'text-valign': 'center',  // Vertical alignment (adjust if you need something else)
            'text-wrap': 'wrap',  // Enable text wrapping
            'text-max-width': '150px',  // Match node width
            'padding': '5px'  // Padding for better readability
          }}

        }},
        {{
          selector: 'edge',
          style: {{
            'width': 2,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle'
          }}
        }}
      ],

      userZoomingEnabled: true,  // Re-enable zooming
      userPanningEnabled: true,  // Re-enable panning
      boxSelectionEnabled: false,  // Disable selection box
      autounselectify: true  // Disable node selection
    }});

    // Apply the layout and lock the nodes in place
    cy.layout({{
      name: 'dagre',
      rankDir: 'TB',
      nodeSep: 30,
      edgeSep: 10,
      rankSep: 100
    }}).run();

    // Lock the nodes after the layout
    cy.nodes().forEach(node => {{
      node.lock();  // Lock all nodes to prevent moving
    }});
  </script>
</body>
</html>
    """

    # Save the generated HTML to a file
    with open('hadith_tree_visualization.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    # Example tree data as JSON
    tree_data = [
        { 'data': { 'id': 'A', 'label': 'النبي', 'geography': 'Madinah' } },
        { 'data': { 'id': 'B', 'label': 'ن1a', 'geography': 'Basra' } },
        { 'data': { 'id': 'C', 'label': 'ن1b', 'geography': 'Baghdad' } },
        { 'data': { 'id': 'D', 'label': 'ن0', 'geography': 'Makkah' } },
        { 'data': { 'id': 'E', 'label': 'ن2a', 'geography': 'Basra' } },
        { 'data': { 'id': 'F', 'label': 'ن2b', 'geography': 'Madinah' } },
        { 'data': { 'id': 'MatnE', 'label': 'إنما الأعمال بالنيات', 'isMatn': True } },
        { 'data': { 'id': 'MatnF', 'label': 'لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه', 'isMatn': True } },
        { 'data': { 'source': 'A', 'target': 'B' } },
        { 'data': { 'source': 'A', 'target': 'C' } },
        { 'data': { 'source': 'B', 'target': 'D' } },
        { 'data': { 'source': 'C', 'target': 'D' } },
        { 'data': { 'source': 'D', 'target': 'E' } },
        { 'data': { 'source': 'D', 'target': 'F' } },
        { 'data': { 'source': 'E', 'target': 'MatnE' } },
        { 'data': { 'source': 'F', 'target': 'MatnF' } }
    ]

    # Convert the tree data to JSON string
    tree_data_json = json.dumps(tree_data, ensure_ascii=False)

    # Define geography colors for the visualization
    geography_colors = {
        "Madinah": "#A0D2DB",
        "Makkah": "#FFB7C5",
        "Basra": "#F5CBA7",
        "Baghdad": "#C5E3BF",
        "Unknown": "#D3D3D3"
    }

    # Generate the HTML file with the given tree data and colors
    generate_html(tree_data_json, geography_colors)
