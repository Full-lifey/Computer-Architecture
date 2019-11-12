#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

print(sys.argv)

if not sys.argv[1]:
    print("Error: no argument supplied")

else:
    instructions = [line.rstrip('\n') for line in open(sys.argv[1])]
    # with open(sys.argv[1]) as instructions:
    program = []
    for line in instructions:
        comment = line.find('#')
        if comment >= 0:
            line = line[:comment]
        # print(line)
        line = line.rstrip()
        if len(line) == 8:
            program.append(line)

    # print(program)
    cpu = CPU()

    cpu.load(program)
    cpu.run()
