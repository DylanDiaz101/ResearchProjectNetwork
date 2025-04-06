import os
import webbrowser
from pyvis.network import Network
import networkx as nx
import pandas as pd

# Load the CSV
df = pd.read_csv("ResearchTopicNetwork.csv")

# Build subject mapping
source_subjects = {}
for _, row in df.iterrows():
    src = row["Source"]
    if src not in source_subjects:
        source_subjects[src] = row["Subject"]

# Create the graph
G = nx.Graph()
for _, row in df.iterrows():
    G.add_edge(row["Source"], row["Target"], type=row["Type"])

source_nodes = set(df["Source"].unique())
target_nodes = set(df["Target"].unique())

# Define our color palette
concept_color = "#d51818"   # Professional blue for Concepts
method_color = "#A60000"    # Polished orange for Methods
project_color = "#aeaeae"   # Light grey for Projects

# Create the Pyvis network
net = Network(height="750px", width="100%", bgcolor="white", font_color="black", notebook=False)

# Add nodes/edges
for node in G.nodes():
    if node in source_nodes:
        subject = source_subjects.get(node, "Concept")
        color = method_color if subject == "Method" else concept_color
        size = 30
    else:
        color = project_color
        size = 15
    net.add_node(node, label=node, color=color, size=size)

for src, dst, data in G.edges(data=True):
    net.add_edge(src, dst)

# Edit physics
net.toggle_physics(True)
net.set_options('''
var options = {
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -2000,
      "centralGravity": 0.3,
      "springLength": 200,
      "springConstant": 0.02,
      "damping": 0.5,
      "avoidOverlap": 0.1
    },
    "minVelocity": 0.75
  },
  "interaction": {
    "dragNodes": true
  }
}
''')

# Write to a temporary HTML file
temp_html_file = "temp_network.html"
net.write_html(temp_html_file)

# Legend HTML with a high z-index and absolute positioning
legend_html = f"""
<!-- BEGIN CUSTOM LEGEND -->
<div style="position: absolute; top: 10px; right: 10px;
            padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9;
            z-index: 9999; font-family: sans-serif;">
    <h4 style="margin: 0 0 5px 0;">Key</h4>
    <p style="margin: 0;">
      <span style="color:{concept_color}; font-size:20px;">&#11044;</span>
      Concepts
    </p>
    <p style="margin: 0;">
      <span style="color:{method_color}; font-size:20px;">&#11044;</span>
      Methods
    </p>
    <p style="margin: 0;">
      <span style="color:{project_color}; font-size:20px;">&#11044;</span>
      Projects
    </p>
</div>
<!-- END CUSTOM LEGEND -->
"""

with open(temp_html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Insert legend before the closing </body> (so it appears on top)
body_end_index = html_content.lower().rfind("</body>")
if body_end_index != -1:
    html_content = (
        html_content[:body_end_index]
        + legend_html
        + html_content[body_end_index:]
    )

final_html_file = "research_topic_network.html"
if os.path.exists(final_html_file):
    os.remove(final_html_file)

# Write the updated HTML
with open(final_html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# Open the final HTML
webbrowser.open(final_html_file)
