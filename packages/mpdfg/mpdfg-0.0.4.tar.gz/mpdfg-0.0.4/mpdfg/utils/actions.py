import tempfile
import shutil
from math import sqrt
from graphviz import Source
from mpdfg.utils.constants import MERMAID_UPPER_HTML, MERMAID_LOWER_HTML


def save_graphviz_diagram(dfg_string: str, file_path: str, format: str):
    tmp_file = tempfile.NamedTemporaryFile(suffix=".gv")
    tmp_file.close()
    src = Source(dfg_string, tmp_file.name, format=format)

    render = src.render(cleanup=True)
    shutil.copyfile(render, f"{file_path}.{format}")


def save_mermaid_diagram(dfg_string: str, file_path: str):
    diagram_string = MERMAID_UPPER_HTML + dfg_string + MERMAID_LOWER_HTML
    with open(f"{file_path}.html", "w") as f:
        f.write(diagram_string)


def image_size(dfg, rankdir):
    horizontal_directions = ["LR", "RL"]
    number_of_nodes = len(dfg["activities"].keys())
    node_size = 4
    edge_length = 5
    estimated_width = sqrt(number_of_nodes) * node_size
    estimated_height = sqrt(number_of_nodes) * node_size + edge_length * 3
    if rankdir in horizontal_directions:
        estimated_width = sqrt(number_of_nodes) * node_size * 3.5
        estimated_height = sqrt(number_of_nodes) * node_size + edge_length * 30
        estimated_width, estimated_height = estimated_height, estimated_width
    return (estimated_width, estimated_height)
