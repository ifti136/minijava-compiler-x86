# compiler/utils/tree_visualizer.py
from graphviz import Digraph
import os

def visualize_parse_tree(root, filename="output/parse_tree"):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    dot = Digraph(comment="Parse Tree", node_attr={'shape': 'box', 'fontname': 'Courier'})
    seen = set()

    def label_of(n):
        if n is None:
            return "None"
        return getattr(n, 'name', n.__class__.__name__)

    def uid(obj):
        return str(id(obj))

    def add(node):
        nid = uid(node)
        if nid in seen:
            return
        seen.add(nid)
        dot.node(nid, label_of(node))

        # preferred children attribute
        children = getattr(node, 'children', None)
        if children is not None:
            for c in children:
                if c is None:
                    continue
                cid = uid(c)
                dot.node(cid, label_of(c))
                dot.edge(nid, cid)
                add(c)
            return

        # fallback: inspect attributes that may hold AST nodes or lists
        for attr in dir(node):
            if attr.startswith('_') or attr in ('name', 'children'):
                continue
            try:
                val = getattr(node, attr)
            except Exception:
                continue
            if isinstance(val, list) and val:
                for c in val:
                    if c is None:
                        continue
                    cid = uid(c)
                    dot.node(cid, label_of(c))
                    dot.edge(nid, cid)
                    add(c)
            elif hasattr(val, 'name'):
                cid = uid(val)
                dot.node(cid, label_of(val))
                dot.edge(nid, cid)
                add(val)

    add(root)
    outpath = filename
    if not outpath.lower().endswith('.png'):
        outpath = filename + '.png'
    base = os.path.splitext(outpath)[0]
    dot.render(base, format='png', cleanup=True)
    return outpath
