#!/usr/bin/python3
from slurm import slurm_tools
              
SLURM_commands=["cd ~","ls -l","sleep 10","time"];
res, success=slurm_tools.slurm_submit(SLURM_commands,
    name="hello",
    mem=5000,
    output='example_02.out')      

print("job number: "+res)
