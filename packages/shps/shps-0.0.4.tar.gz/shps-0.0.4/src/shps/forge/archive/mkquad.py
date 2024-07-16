#!/usr/bin/env python

# Claudio Perez
import os
import sys
import errno
import signal
import inspect
import textwrap
import functools
from datetime import date

import quadpy
import numpy as np


HELP = """
usage: iquad <family>... -n <order>
"""

class TimeoutError(Exception): pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    "https://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish"
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator

@timeout(20)
def get_rule(family, n, fmt="py"):
    q = None
    for s in ["{family}","gauss_{family}"]:
        for lib in [quadpy.c1, quadpy.e1r]:
            if hasattr(lib, s.format(family=family)):
                try:
                    g = getattr(lib, s.format(family=family))
                    q = g(n)
                except AssertionError:
                    return "None"
                except TimeoutError:
                    return "None"
                break
    if q is None:
        print(family, file=sys.stderr)
        return "None"
    print(family, n, file=sys.stderr)
    
    if fmt=="py":
        return f"""
          "degree": {q.degree},
          "points": {repr(q.points.tolist())},
          "weights": {repr(q.weights.tolist())},
          "generator": "{g.__name__}"
        """
    elif  fmt=="c":
        points = textwrap.indent(",\n".join(f"{{{x:20}, {w:20}}}" for x,w in zip(q.points,q.weights)), " "*4)
        return (f"{n}, {q.degree}, {{\n{points}}}")

def get_family(family, rng, fmt="py"):
    if fmt == "py":
        NL = "    },\n        "
        return textwrap.dedent(f"""\
        class {family.replace('_',' ').title().replace(' ','')}(IntervalQuadrature):
            data = {{
                {NL.join(f"{n}: {{{get_rule(family,n,fmt)}" for n in range(*rng))}
                }}
            }}
        """)

    NL = "},\n"
    return (f"""
{NL.join(f"{family}{n:02} = {{{get_rule(family,n,fmt)}" for n in range(*rng))}}}
""")
# }},

#    return (f"""
#struct {{int n; double points[][2];}}
#{NL.join(f"{family}{n:02} = {{{get_rule(family,n,fmt)}" for n in range(*rng))}
#}}
#}};
#        """)
    

#
# Argument parsing
#
rng = (1,100)
source = False
fmt = "py"
families = []
argi = iter(sys.argv[1:])
for arg in argi:
    if arg == "-n":
        rng = tuple(map(int,next(argi).split(",")))
    elif arg == "-s":
        source = True
    elif arg == "-c":
        fmt = "c"
    elif arg == "-h":
        print(HELP)
        sys.exit()
    else:
        families.append(arg)



if source:
    print(textwrap.dedent(f"""
    #!/bin/env python
    # Generated on {date.today()} with the following command:
    #     
    #     {' '.join(sys.argv)}
    #
    """))
    print(textwrap.dedent(f"""
    if __name__ == "__main__":
    """))
    print(textwrap.indent(inspect.getsource(sys.modules[__name__]), " "*4))

if fmt=="py":
    print(textwrap.dedent("""

    class IntervalQuadrature:
        def __init__(self, n):
            data = self.__class__.data[n]
            self.points = data["points"]
            self.weights = data["weights"]
            self.degree = data["degree"]

    """))
else:
    print("""
#include <stdio.h>  // printf
#include <stdlib.h> // atoi

struct IntervalQuadrature {int n, deg; double points[][2];}"
""")


if families:
    if fmt=="c": print(",\n".join(get_family(fam,rng,fmt) for fam in families))
    else:
        for fam in families:
            print(get_family(fam, rng, fmt))
else:
    for fam in "lobatto legendre radau kronrod".split(" "):
        families.append(fam)
        if fmt=="c": print(",\n".join(get_family(fam,(1,100),fmt) for fam in families))
        else:
            print(get_family(fam, (1, 100), fmt))
    for fam in "newton_cotes_closed newton_cotes_open".split(" "):
        families.append(fam)
        if fmt=="c": print(",\n".join(get_family(fam,(1,30),fmt) for fam in families))
        else:
            print(get_family(fam, (1, 30), fmt))

if fmt=="c":
    nl = '\n        '
    print(";\n")
    print("\n".join(f"""

struct IntervalQuadrature *
{fam}(int n)
{{ 
    switch (n) {{
        {nl.join(f'case {n} : return &{fam}{n:02};' for n in range(*rng))}
    }}
}}
""" for fam in families))

    print(r"""

int main(int argc, char **argv){
  const struct IntervalQuadrature *q = legendre(atoi(argv[2]));

  for (int i=0; i < q->n; i++)
    printf("%lf\t%lf\n", q->points[i][0], q->points[i][1]);
}

""")

