from typing import List
from kabinet.api.schema import NodeFragment, EdgeFragment, DiagramFragment
from kabinet.traits import Edge


def find_connected_edges(
    node: NodeFragment, diagram: DiagramFragment
) -> List[EdgeFragment]:
    con_edges = []

    for el in diagram.elements:
        if isinstance(el, Edge):
            if el.source == node.id:
                con_edges.append(el)

    return con_edges
