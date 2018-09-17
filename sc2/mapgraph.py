from functools import lru_cache

class PathingError(Exception):
    pass

def neighbors(graph, node):
    return (n for n in (
        (node[0]-1, node[1]),
        (node[0]+1, node[1]),
        (node[0], node[1]-1),
        (node[0], node[1]+1)
    ) if 0 <= n[0] < graph.width and 0 <= n[1] < graph.height)

@lru_cache
def closest_free(graph, start):
    if graph.is_empty(start):
        return start

    pending = {start}
    visited = set()

    while pending:
        for node in neighbors(graph, pending.pop()):
            if node not in visited:
                if graph.is_empty(node):
                    return node

                if node not in pending and node not in visited:
                    pending.add(tile)

    raise PathingError("No free nodes")

@lru_cache
def a_star(graph, start, end):
    assert isinstance(start, tuple)
    assert isinstance(end, tuple)

    if not graph.is_empty(start):
        raise PathingError("Must start from an empty square")

    if not graph.is_empty(end):
        raise PathingError("Must end to an empty square")

    pending = {start}
    visited = set()

    def make_path(node):
        path = []
        while node.parent:
            path.insert(0, node)
            node = node.parent
        return path

    while pending:
        current = min(pending, key=lambda p: p.approx)

        if current == end:
            return make_path(current)

        pending.remove(current)
        visited.add(current)

        for node in neighbors(graph, current):
            if node not in visited and graph.is_empty(node):
                node.approx = (end[0] - node[0]) ** 2 + (end[1] - node[1]) ** 2
                node.parent = current

                if node not in pending:
                    pending.add(node)

    raise PathingError("No route")

@lru_cache
def walking_distance(graph, start, end):
    return len(a_star(graph, start, end))
