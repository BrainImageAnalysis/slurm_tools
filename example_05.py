#!/usr/bin/python3
import sys
import os
sys.path.append("/disk/soft/bia_software/slurm_tools/")
from slurm import slurmjob


script_file = __file__
script_location = os.path.dirname(os.path.realpath(script_file))

params = {}
params['quiet'] = True
params['debug'] = False
params['mem'] = "16G"
params['cores'] = 2
params['append'] = False
params['time'] = '01-00:00:00'
params['feature'] = ''
params['export'] = 'ALL'
#params['partition'] = 'bigmem'
#params['gres'] = ''
params['partition'] = 'gpu'
params['gres'] = 'gpu:1'
params['nodelist'] = ''
params['exclude'] = ''
params['depends'] = []
params['error'] = None
params['output'] = script_location+'/example_05.out'

print("outputs are here:",params['output'])
print("error outputs are here:",params['output']+".err")


def myfun():
    print("some external fun that should run")


class myclass(slurmjob):
    def __init__(self) -> None:
        super().__init__()
        self.parser.add_argument('--message', type=str,required=True)

    def run(self, **kwargs):
        print(self.args.message)
        #CODE TO RUN HERE
        myfun()

test = myclass()
test.submit(slurm_params=params)