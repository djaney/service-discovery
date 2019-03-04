from graphviz import Digraph


class Dot:
    def __init__(self, service_manager):
        self.service_manager = service_manager

    def print(self, render_format='svg'):
        dot = Digraph()

        for service_name, service_data in self.service_manager.services().items():
            dot.node(service_name)
            for dep in service_data['depends_on']:
                dot.edge(service_name, dep)
        return dot.pipe(format=render_format)
