"""""" # start delvewheel patch
def _delvewheel_patch_1_7_1():
    import os
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'bliss_bind.libs'))
    if os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_7_1()
del _delvewheel_patch_1_7_1
# end delvewheel patch

from .bliss_bind_ext import Graph, Digraph, Stats


class NamedGraph():
    def __init__(self):
        # maps node index to node names
        self.node_name = {}

        # maps node names to colors/indces
        self.node_color = {}
        self.node_index = {}

        # maps node names to a set of neighbour node names
        self.neighbours = {}

        self.g = Graph()

    def add_node(self, name, color):
        v = self.g.add_vertex(color=color)
        if v is None:
            return

        self.node_name[v] = name
        self.node_index[name] = v
        self.node_color[name] = color
        self.neighbours[name] = set()

    def add_link(self, node1, node2):
        self.g.add_edge(self.node_index[node1],
                        self.node_index[node2])
        self.neighbours[node1].add(node2)
        self.neighbours[node2].add(node1)

    def __eq__(self, other):
        return self.node_color == other.node_color and \
            self.neighbours == other.neighbours

    def __hash__(self):
        return hash(
            (frozenset(self.node_color.items()),
             frozenset((i, frozenset(j))
             for i, j in sorted(self.neighbours.items()))))

    def canonical_labelling(self):
        labelling, _ = self.g.canonical_form()
        return {self.node_name[i]: l
                for i, l in enumerate(labelling)}

    def canonical_graph(self):
        return self.relabel(self.canonical_labelling())

    def relabel(self, labelling):
        if set(labelling) != set(self.node_index):
            raise ValueError("labelling does not map nodes")

        cpy = NamedGraph()
        for name, l in labelling.items():
            if l in cpy.node_index:
                raise ValueError("labelling is not a bijection")
            cpy.add_node(l, self.node_color[name])

        for name, l in labelling.items():
            for n in self.neighbours[name]:
                if n >= name:
                    cpy.add_link(l, labelling[n])

        return cpy

    def __copy__(self):
        return self.relabel({n: n for n in self.node_index})

    def get_isomorphism(self, other):
        self_degs = sorted(map(len, self.neighbours.values()))
        other_degs = sorted(map(len, other.neighbours.values()))
        if self_degs != other_degs:
            return None

        self_cols = sorted(self.node_color.values())
        other_cols = sorted(other.node_color.values())
        if self_cols != other_cols:
            return None

        this_can_labelling = self.canonical_labelling()
        other_can_labelling = other.canonical_labelling()
        if self.relabel(this_can_labelling) != \
                other.relabel(other_can_labelling):
            return None

        inverse_can_labelling = {v: k for k, v in other_can_labelling.items()}
        return {k: inverse_can_labelling[v]
                for k, v in this_can_labelling.items()}

    def find_automorphisms(self):
        perms = []
        self.g.find_automorphisms(
                callback=lambda x: perms.append(x))

        return perms
