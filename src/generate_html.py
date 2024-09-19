def generate_html(data_json, geography_colors):
    # HTML template with placeholders for data and geography colors
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>D3.js Tree with Proper Matn Alignment and Dynamic Height</title>
      <style>
        html, body {{
            margin: 0;
            padding: 0;
            overflow: hidden;  /* Prevent scroll bar */
            height: 100%;
            }}

        .node rect {{
          stroke-width: 1.5px;
          width: 150px;
          height: 30px;
        }}

        .node text {{
          font: 12px sans-serif;
          text-anchor: middle;
          alignment-baseline: middle;
          dominant-baseline: middle;
          fill: #333;
        }}

        .matn {{
          font-size: 12px;
          fill: #555;
          direction: rtl; /* Right-to-left direction for Arabic */
          text-align: right; /* Right-align the Arabic text */
          word-wrap: break-word;
        }}

        .link {{
          fill: none;
          stroke: #ccc;
          stroke-width: 2px;
        }}

        svg {{
          width: 100%;
          height: 100vh;
          background-color: #f9f9f9;
        }}
      </style>
    </head>
    <body>
      <svg></svg>

      <script src="https://d3js.org/d3.v6.min.js"></script>
      <script>
        // Data provided from Python
        const data = {data_json};

        const svg = d3.select("svg");
        const width = window.innerWidth;
        const height = window.innerHeight;

        const margin = {{top: 40, right: 120, bottom: 40, left: 120}};  // Increase top and bottom margin for better spacing
        const gWidth = width - margin.right - margin.left;
        const gHeight = height - margin.top - margin.bottom;

        // Create a group element that holds the tree
        const g = svg.append("g").attr("transform", `translate(${{margin.left}},${{margin.top}})`);

        // Create the tree layout with better spacing to avoid x-axis overlap
        const tree = d3.tree()
          .nodeSize([250, 100])  // Adjust nodeSize for wider x-spacing
          .separation((a, b) => (a.parent == b.parent ? 1.5 : 2)); // Increase separation between nodes to avoid overlap

        const root = d3.hierarchy(data);

        // Generate the hierarchical layout (top-down)
        tree(root);

        // Create links (the lines connecting nodes)
        const link = g.selectAll(".link")
          .data(root.links())
          .enter().append("path")
          .attr("class", "link")
          .attr("d", d3.linkVertical()
            .x(d => d.x)  // x is the horizontal position
            .y(d => d.y)); // y is the vertical position

        // Define modern pastel color scale for regions, injected from Python
        const colorScale = d3.scaleOrdinal()
          .domain({list(geography_colors.keys())})
          .range({list(geography_colors.values())});

        // Create nodes (rectangles representing narrators)
        const node = g.selectAll(".node")
          .data(root.descendants())
          .enter().append("g")
          .attr("class", "node")
          .attr("transform", d => `translate(${{d.x - 75}},${{d.y - 15}})`); // Adjust based on rectangle size (75 = half of width, 15 = half of height)

        // Append a rectangle for each node and apply fill and stroke based on geography
        node.append("rect")
          .attr("fill", d => colorScale(d.data.geography))  // Fill color based on geography
          .attr("stroke", d => d3.rgb(colorScale(d.data.geography)).darker());  // Border color slightly darker than fill

        // Add text inside the rectangle
        node.append("text")
          .attr("dy", 20)  // Adjust vertical centering within the box
          .attr("x", 75)   // Center text in the middle of the box
          .text(d => d.data.name);

        // Function to wrap text based on character width, adjusted for overflow
        function wrapTextByWidth(text, maxWidth) {{
          const words = text.split(' ');
          const svg = d3.select("body").append("svg").attr("width", 0).attr("height", 0);  // Offscreen SVG to measure text width
          const tempText = svg.append("text").style("font-size", "12px").style("visibility", "hidden");

          let line = '';
          const lines = [];

          words.forEach(word => {{
            const testLine = line + word + ' ';
            tempText.text(testLine);
            const textWidth = tempText.node().getComputedTextLength();

            if (textWidth < maxWidth) {{
              line = testLine;
            }} else {{
              lines.push(line);
              line = word + ' ';
            }}
          }});

          lines.push(line);  // Push the final line

          tempText.remove();  // Remove the temporary text element
          return lines;
        }}

        // Add the matn text itself, wrapping it manually and right-aligning it under the node
        node.filter(d => d.data.matn)
          .append("text")
          .attr("x", 150)  // Start the text from the right edge of the node
          .attr("y", 50)  // Start slightly below the rect's top
          .style("font-size", "12px")
          .style("fill", "#555")
          .style("text-anchor", "end")  // Right-align the text
          .each(function(d) {{
            const wrappedLines = wrapTextByWidth(d.data.matn, 140);  // Adjusted width to prevent overflow
            wrappedLines.forEach((line, i) => {{
              d3.select(this).append("tspan")
                .attr("x", 150)  // Align each line to the right side of the node
                .attr("dy", i === 0 ? 0 : 15)  // Line spacing
                .text(line);
            }});
          }});

        // Enable zooming and panning
        svg.call(d3.zoom().on("zoom", (event) => {{
          g.attr("transform", event.transform);
        }}));
      </script>
    </body>
    </html>
    """

    # Write the generated HTML content to a file
    with open('tree.html', 'w', encoding='utf-8') as file:
        file.write(html_template)

# Example usage:
data_json = {
    "name": "عبد الصمد بن عبد الوارث",
    "geography": "Region 1",
    "children": [
        {
            "name": "إسحاق بن راهويه",
            "geography": "Region 2"
        },
        {
            "name": "شعبة بن الحجاج",
            "geography": "Region 1",
            "children": [
                { 
                    "name": "هشام بن بختي", 
                    "geography": "Region 3",
                    "matn": "Matn for هشام بن بختي: حدثنا قتيبة بن سعيد قال: حدثنا ليث عن ابن شهاب..."
                },
                {
                    "name": "عبد الصمد بن عبد الوارث",
                    "geography": "Region 2",
                    "children": [
                        { 
                            "name": "Additional Narrator 1", 
                            "geography": "Region 1",
                            "matn": "Matn for Additional Narrator 1: حدثنا قتيبة بن سعيد قال: حدثنا ليث عن ابن شهاب..."
                        },
                        { 
                            "name": "Additional Narrator 2", 
                            "geography": "Region 3",
                            "matn": "Matn for Additional Narrator 2: حدثنا قتيبة بن سعيد قال: حدثنا ليث عن ابن شهاب..."
                        }
                    ]
                }
            ]
        }
    ]
}

# Geography colors mapping
geography_colors = {
    "Region 1": "#A0D2DB",
    "Region 2": "#FFB7C5",
    "Region 3": "#F5CBA7"
}

# Call the function to generate the HTML file
generate_html(data_json, geography_colors)

