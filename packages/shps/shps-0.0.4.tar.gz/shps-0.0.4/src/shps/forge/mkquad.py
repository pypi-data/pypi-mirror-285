#!/usr/bin/env python

# Claudio Perez
import os
import sys
import json
import errno
import signal
import inspect
import textwrap
import functools
from datetime import date

import quadpy
import numpy as np
import re

HELP = """
usage: iquad <family>... -n <order>
"""

#
# Utilities
#

def put(file, block):
    # Create regular expression pattern
    chop = re.compile('#chop-begin.*?#chop-end', re.DOTALL)

    # Open file
    with open(file, "r") as f:
        data = f.read()

    # Chop text between #chop-begin and #chop-end
    data_chopped = chop.sub('', data)

    # Save result
    with open('data', 'w') as f:
        f.write(data_chopped)

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
            try: result = func(*args, **kwargs)
            finally: signal.alarm(0)
            return result
        return wrapper
    return decorator

@timeout(10)
def get_rule(family, n):
    q = None
    for s in ["{family}","gauss_{family}","{family}_gauss"]:
        for lib in [quadpy.c1, quadpy.e1r, quadpy.e1r2]:
            if hasattr(lib, s.format(family=family)):
                try:
                    g = getattr(lib, s.format(family=family))
                    q = g(n)
                except AssertionError:
                    return [None]*3
                #except TimeoutError:
                #    return [None]*3
                break
    if q is None:
#       print(family, file=sys.stderr)
        return [None]*3
    print(family, n, file=sys.stderr)
    return n,q,g


def print_rule(n, q, g, fmt):
    if fmt=="py":

        return f"""
          "degree": {q.degree},
          "points": {repr(q.points.tolist())},
          "weights": {repr(q.weights.tolist())},
          "generator": "{g.__name__}"
        """
    elif  fmt=="c":
        points = textwrap.indent(
            ",\n".join(f"{{{x:20}, {w:20}}}" for x,w in zip(q.points,q.weights)),
            " "*4
        )
        return (f"{n}, {q.degree}, {{\n{points}}}")

def get_family(family, rng, fmt="py", fams=None):
    rules = []
    for n in range(*rng):
        try:
            rules.append(get_rule(family,n))
        except TimeoutError:
            break
    #rules = [get_rule(family,n) for n in range(*rng)]
    if fams is not None:
        fams.update({family:rules})

    if fmt == "py":
        NL = "    },\n        "
        return textwrap.dedent(f"""\
        class {family.replace('_',' ').title().replace(' ','')}(IntervalQuadrature):
            data = {{
                {NL.join(f"{n}: {{{print_rule(n,q,g,fmt)}" for n,q,g in rules if q)}
                }}
            }}
        """)

    NL = "},\n"
    return (f"""
{NL.join(f"{family}{n:02} = {{{print_rule(n,q,g,fmt)}" for n,q,g in rules if q)}}}

""")



#
# Argument parsing
#
rng = (1,100)
source = False
write_json = False
fmt = "py"
families = []
argi = iter(sys.argv[1:])
for arg in argi:
    if arg == "-n":
        rng = tuple(map(int,next(argi).split(",")))
    elif arg == "-s":
        source = True
    elif arg == "-json":
        write_json = True
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
#include <string.h> // strcmp

const static struct IntervalQuadrature {int n, deg; double points[][2];}""")


fams = {}
if families:
    if fmt=="c":
        print(",\n".join(get_family(fam,rng,fmt,fams) for fam in families))
    else:
        for fam in families:
            print(get_family(fam, rng, fmt, fams))
else:
    families = "lobatto legendre radau kronrod".split(" ")
    rng1 = rng
    if fmt=="c":
        print(",\n".join(get_family(fam,rng1,fmt, fams) for fam in families), ",")
    else:
        for fam in families:
            print(get_family(fam, rng1, fmt, fams))
    #
    families = "newton_cotes_closed newton_cotes_open".split(" ")

    if fmt=="c":
        print(",\n".join(get_family(fam,rng,fmt,fams) for fam in families), ",")

    else:
        for fam in families:
            print(get_family(fam, rng, fmt,fams))

if fmt=="c":
    nl = '\n        '
    print("end;")
    print("\n".join(f"""

const struct IntervalQuadrature *
{fam}(int n)
{{ 
    switch (n) {{
        {nl.join(f'case {n} : return &{fam}{n:02};' for n,q,g in dat if n)}
    }}
    return NULL;
}}
""" for fam,dat in fams.items()))

    rnl = r"\n"
    tab = "\t"
    print(rf"""
static void
print_usage()
{{
    printf("usage: iquad <family> <n>\n\n"
           "    Family\n"
           {(nl+'   ').join(fr'"    {fam:<20}{tab}{dat[0][0]}, {dat[-1][0]}{rnl}"' for fam,dat in fams.items())}
           "{rnl}"
    );
}}
""")

    print(r"""

int main(int argc, char **argv){
  const struct IntervalQuadrature *(*fn)(int);

  int i = 1;
  if (argc < 2) print_usage();
  else if (strcmp(argv[i], "legendre")==0) fn = &legendre;
  else if (strcmp(argv[i], "lobatto" )==0) fn = &lobatto;
  else if (strcmp(argv[i], "kronrod" )==0) fn = &kronrod;
  else if (strcmp(argv[i], "radau"   )==0) fn = &radau;
  else if (strcmp(argv[i], "cotes_closed" )==0) fn = &newton_cotes_closed;
  else if (strcmp(argv[i], "cotes_open" )==0) fn = &newton_cotes_open;
  else if (strcmp(argv[i], "-h" )==0) {
    print_usage();
    return 0;
  } else {
      fprintf(stderr, "Unknown rule specifier '%s'\n", argv[i]);
      return EXIT_FAILURE;
  }

  const struct IntervalQuadrature *q = fn(atoi(argv[2]));

  for (int i=0; i < q->n; i++)
    printf("%lf\t%lf\n", q->points[i][0], q->points[i][1]);

}
""")

if write_json:
    with open("iquad.json","w+") as f:
        json.dump({
            fam: [
                {k: v.tolist() if hasattr(v,"tolist") else v
                    for k,v in vars(rule[1]).items()} for rule in fams[fam] if rule[0]
            ] for fam in fams
        }, f, indent=4)

