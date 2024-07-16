
from shps import plane, child

from .types import Shape, Nodes, Tuple


class Tag(int): ...

def block(ne: Tuple[int,int],
          family: Shape,
          points: Nodes  = None,
          nstart: Tag  = 1,
          estart: Tag  = 1,
#         element = None,
          stencil: Shape = None,
          exclude = None,
          join    = None,
          radius  = 1e-8,
          number  = "feap"
          )->Block: ...

def grid(ne: Tuple[int,int], nn=(2,2))->Block: ...

def plot(nodes, cells):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    for cell in cells.values():
        ax.plot(*zip(*[nodes[i] for i in cell], nodes[cell[0]]))
    return ax

if __name__ == "__main__":
    import sys,pprint

    ne = int(sys.argv[1]), int(sys.argv[2])

    if len(sys.argv) > 3:
        nn = int(sys.argv[3]), int(sys.argv[4])

    else:
        nn = 2,2
    # nodes, cells = grid(ne, nn)


# First block
    element = plane.Lagrange(4)
    points  = {
            1: (0.0, 0.0),
            2: (1.1, 0.0),
            3: (1.0, 1.0),
            4: (0.0, 1.0),
            5: (0.5,-0.1),
            6: (1.1, 0.5)
    }

    nodes, cells = block(ne, element, points=points)

# Second Block
    element = plane.Serendipity(4)
    points  = {
            1: (1.1, 0.0),
            2: (2.0, 0.0),
            3: (2.0, 1.0),
            4: (1.0, 1.0),
            5: (1.5,-0.1),
#           7: (2.1, 0.5),
            8: (1.1, 0.5)
    }
    other = dict(nodes=nodes, cells=cells)
    nodes, cells = block(ne, element, points=points, join=other)



    pprint.PrettyPrinter(indent=4).pprint(nodes)
    pprint.PrettyPrinter(indent=4).pprint(cells)

    from plotting import Plotter
    ax = plot(nodes, cells)
    ax.axis("equal")
#   ax = None
    Plotter(ax=ax).nodes(nodes).show()

