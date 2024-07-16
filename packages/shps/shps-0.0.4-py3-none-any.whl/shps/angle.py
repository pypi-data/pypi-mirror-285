from itertools import cycle
from math import sqrt

def _make_nodes(n):
    """Implement spiral node numbering"""
    dx,dy = 1,0            # Starting increments
    x,y = 0,0              # Starting location
    output = [[None]* n for j in range(n)]

    slopes = cycle(((1,1), (-1/sqrt(2), -1/sqrt(2)), (1, 1)))

    mx,my = next(slopes)
    for i in range(sum(n-i for i in range(n))):
        yield (x*mx/(n-1),  y*my/(n-1)), i
        output[x][y] = i + 1
        nx,ny = x+dx, y+dy
        if 0<=nx<n and 0<=ny<n and output[nx][ny] is None:
            x,y = nx,ny
        else:
            dx,dy = -dy,dx
            mx, my = next(slopes)
            x,y = x+dx, y+dy
            # x,y = x+dx, y+dy


class Triangle:
    def __init__(self, order):
        self.order = order
        self.n = order + 1
        self.nn = sum(self.n - i for i in range(self.n))

        self._nodes = None

    @property
    def nodes(self):
        if self._nodes is None:
            self._nodes = {}
            for j,(xy,i) in enumerate(_make_nodes(self.n)):
                if (0 < i < 3*(self.n-1)):
                    if not i%(self.n-1):
                        i //= self.n-1
                    else:
                        i += 2 - i//(self.n-1)
                self._nodes.update({i+1: xy})
        return self._nodes


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    for n in Triangle(3).nodes.values():
        plt.scatter(*n)
    plt.show()

