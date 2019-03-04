from graphviz import Digraph
from core.service_manager import Status


class Dot:
    def __init__(self, service_manager):
        self.service_manager = service_manager

    def print(self, render_format='svg'):
        dot = Digraph(node_attr={'shape': 'plaintext'})

        for service_name, service_data in self.service_manager.services().items():
            content = "<<table border='0' cellborder='1' cellspacing='0'>"
            content += "<tr><td cellpadding='6'><b>{}</b></td></tr>".format(service_name)

            for dep in service_data['depends_on']:
                dot.edge(service_name, dep)

            for node, node_data in service_data['nodes'].items():
                color = 'bgcolor="red"' if node_data['status'] != Status.UP else ''
                content += "<tr><td cellpadding='6' {}>{}</td></tr>".format(color, node)

            content += "</table>>"
            dot.node(service_name, content)
        return dot.pipe(format=render_format)
