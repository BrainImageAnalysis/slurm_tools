#!/usr/bin/python3

from slurm import slurm_tools
import sys
import os
import argparse

parser = argparse.ArgumentParser(description='Whatever.')

parser.add_argument('--slurm', action='store_true')
parser.add_argument('--foo', type=int, default=42, help='FOO!')


args = parser.parse_args()

if not args.slurm:
    script_file = __file__
    script_location = os.path.dirname(os.path.realpath(script_file))
    command_line_args = " ".join(sys.argv)
    SLURM_commands=[script_location+"/"+command_line_args+" --slurm"];

    res, success=slurm_tools.slurm_submit(SLURM_commands,
        name="hello",
        mem=5000,
        output=script_location+'/example_03.out')  
else:
    print(args.foo)
