from mpdfg.utils.constants import (
    GRAPHVIZ_NODE_DATA,
    GRAPHVIZ_NODE_DATA_ROW,
    GRAPHVIZ_LINK_DATA,
    GRAPHVIZ_LINK_DATA_ROW,
    GRAPHVIZ_START_END_LINK_DATA,
)
import graphviz

from mpdfg.utils.diagrammer import (
    ids_mapping,
    dimensions_min_and_max,
    format_time,
    link_width,
    background_color,
)


class GraphVizDiagrammer:
    def __init__(
        self,
        dfg: dict,
        start_activities: dict,
        end_activities: dict,
        visualize_frequency: bool = True,
        visualize_time: bool = True,
        visualize_cost: bool = True,
        cost_currency: str = "USD",
        rankdir: str = "TB",
    ):
        self.dfg = dfg
        self.start_activities = start_activities
        self.end_activities = end_activities
        self.visualize_frequency = visualize_frequency
        self.visualize_time = visualize_time
        self.visualize_cost = visualize_cost
        self.cost_currency = cost_currency
        self.rankdir = rankdir
        self.activities_ids = {}
        self.dimensions_min_and_max = {}
        self.diagram = graphviz.Digraph("mpdfg", comment="Multi Perspective DFG")

        self.set_activities_ids_mapping()
        self.set_dimensions_min_and_max()

    def set_activities_ids_mapping(self):
        self.activities_ids = ids_mapping(self.dfg["activities"])

    def set_dimensions_min_and_max(self):
        self.dimensions_min_and_max = dimensions_min_and_max(
            self.dfg["activities"], self.dfg["connections"]
        )

    def build_diagram(self):
        self.add_config()
        self.add_activities()
        self.add_connections()

    def add_config(self):
        self.diagram.graph_attr["rankdir"] = self.rankdir
        self.diagram.node(
            "start",
            label="&#9650;",
            shape="circle",
            fontsize="20",
            margin="0.05",
            style="filled",
            fillcolor="green",
        )
        self.diagram.node(
            "complete",
            label="&#9632;",
            shape="circle",
            fontsize="20",
            margin="0.05",
            style="filled",
            fillcolor="red",
        )

    def add_activities(self):
        for activity in self.dfg["activities"].keys():
            self.add_activity_node(activity)

    def add_activity_node(self, activity):
        activity_id = self.activities_ids[activity]
        label = self.build_activity_label(activity)
        self.diagram.node(activity_id, label=f"<{label}>", shape="none")

    def build_activity_label(self, activity):
        dimensions_rows_data = " "
        for dimension, measure in self.dfg["activities"][activity].items():
            bgcolor, content = self.activity_label_data(activity, dimension, measure)
            if content != "":
                dimensions_rows_data += GRAPHVIZ_NODE_DATA_ROW.format(bgcolor, content)

        return GRAPHVIZ_NODE_DATA.format(dimensions_rows_data)

    def activity_label_data(self, activity, dimension, measure):
        bgcolor = background_color(measure, dimension, self.dimensions_min_and_max[dimension])
        content = ""
        if dimension == "frequency":
            bgcolor = bgcolor if self.visualize_frequency else "royalblue"
            content = (
                f"{activity} ({'{0:,}'.format(measure)})" if self.visualize_frequency else activity
            )

        elif dimension == "time" and self.visualize_time:
            content = format_time(measure)

        elif dimension == "cost" and self.visualize_cost:
            content = f"{'{0:,}'.format(measure)} {self.cost_currency}"

        return bgcolor, content

    def add_connections(self):
        self.add_extreme_connection_edges("start")
        self.add_extreme_connection_edges("complete")
        for connection in self.dfg["connections"]:
            self.add_connection_edge(connection)

    def add_extreme_connection_edges(self, extreme):
        activities = self.start_activities if extreme == "start" else self.end_activities

        for activity, frequency in activities.items():
            activity_id = self.activities_ids[activity]
            frequency = frequency if self.visualize_frequency else " "
            penwidth = (
                link_width(frequency, self.dimensions_min_and_max["frequency"])
                if self.visualize_frequency
                else 1
            )
            color = (
                background_color(frequency, "frequency", self.dimensions_min_and_max["frequency"])
                if self.visualize_frequency
                else "black"
            )
            self.diagram.edge(
                "start" if extreme == "start" else activity_id,
                "complete" if extreme == "complete" else activity_id,
                penwidth=str(penwidth),
                color="gray75",
                fontsize="16",
                style="dashed",
                arrowhead="none",
                label=f"<{GRAPHVIZ_START_END_LINK_DATA.format(color, frequency)}>",
            )

    def add_connection_edge(self, connection):
        activity, following_activity = (
            self.activities_ids[connection[0]],
            self.activities_ids[connection[1]],
        )
        penwidth = (
            link_width(
                self.dfg["connections"][connection]["frequency"],
                self.dimensions_min_and_max["frequency"],
            )
            if self.visualize_frequency
            else 1
        )
        if self.visualize_frequency or self.visualize_time:
            label = self.build_connection_label(connection)
            self.diagram.edge(
                activity, following_activity, penwidth=str(penwidth), label=f"<{label}>"
            )
        else:
            self.diagram.edge(activity, following_activity, penwidth=str(penwidth))

    def build_connection_label(self, connection):
        dimensions_string = " "
        for dimension, measure in self.dfg["connections"][connection].items():
            bgcolor, content = self.connection_label_data(dimension, measure)
            if content != "":
                dimensions_string += GRAPHVIZ_LINK_DATA_ROW.format(bgcolor, content)

        return GRAPHVIZ_LINK_DATA.format(dimensions_string)

    def connection_label_data(self, dimension, measure):
        bgcolor = background_color(measure, dimension, self.dimensions_min_and_max[dimension])
        content = ""
        if dimension == "frequency":
            content = "{0:,}".format(measure) if self.visualize_frequency else content
        elif dimension == "time" and self.visualize_time:
            content = format_time(measure)

        return bgcolor, content

    def get_diagram_string(self):
        return self.diagram.source
