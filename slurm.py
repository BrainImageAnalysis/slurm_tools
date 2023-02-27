import subprocess
import math
import sys
import argparse 
import json
import time
import datetime
import os
import re
import __main__
import argparse

class slurmjob:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()

    def submit(self,slurm_params,*args, **kwargs):
        script_file = __main__.__file__
        script_location = os.path.dirname(os.path.realpath(script_file))
        command_line_args = " ".join(sys.argv)
        SLURM_commands=[script_location+"/"+command_line_args+" --slurm"]
        
        
        self.parser.add_argument('--slurm', action='store_true', help=argparse.SUPPRESS)
        self.parser.add_argument('--noslurm', action='store_true')
        self.args = self.parser.parse_args()

        if not self.args.slurm and not self.args.noslurm:

            res, success=slurm_tools.slurm_submit(SLURM_commands,**slurm_params)  
            if not success:
                print(res)
                
            assert(success)

        else:
            self.run(*args, **kwargs)
            self.args = self.parser.parse_args()

    def run(self,*args, **kwargs):
        pass

class slurm_tools:
        @staticmethod
        def get_notebook_job_info():
            job_id = os.getenv('SLURM_JOBID')   
            job_info,success = slurm_tools.bash_run("scontrol show job "+job_id)
            job_dict = {}
            for j in job_info[0].split():
                j = j.split("=")
                job_dict[j[0]] = j[1]
            return job_dict

        @staticmethod
        def print_host_info():
            sinfo = slurm_tools.get_notebook_job_info()
            print("##############################################")
            print("JobId :",sinfo["JobId"])
            print("StartTime :",sinfo["StartTime"])
            print("NodeList :",sinfo["NodeList"])
            print("NumCPUs :",sinfo["NumCPUs"])
            print("MinMemoryNode :",sinfo["MinMemoryNode"])
            if "TresPerNode" in sinfo:
                print("TresPerNode :",sinfo["TresPerNode"])
            print("##############################################")

        @staticmethod
        def bash_run(command):
                #proc = subprocess.Popen(['/bin/bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf8')
                #out, errors = proc.communicate(input=command)
                #return out, (proc.returncode == 0)
                #print(command)
                proc = subprocess.Popen(['/bin/bash'],text=True ,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                return proc.communicate(command) , (proc.returncode == 0)
        
        @staticmethod
        def _check_if_valid_log_folder(outfile):
            folder = os.path.dirname(outfile)
            if len(folder) == 0 or not (os.access(folder, os.W_OK)):
                return False
            else:
                return True 
            
        @staticmethod
        def slurm_submit(commands,**kwargs):
            params={}
            params['quiet']=True
            params['debug']=False
            params['mem']=5000
            params['cores']=2
            params['append']=False
            params['time']='01-00:00:00'
            params['queue']='bigmem'
            params['feature']=''
            params['export']='ALL'
            params['gres']=''
            params['nodelist']=''
            params['exclude']=''
            params['depends'] = []
            params['error'] = None
            


            if kwargs is not None:
                for key, value in kwargs.items():
                    params[key]=value;

            if not 'output' in params:
                print("#E: please specify an output file" )
                return "0", False
            
            if "partition" in params:
                params['queue'] = params['partition']
                
            print(params)

            batch='printf "'
            batch=batch+'#!/bin/bash \\n'

            if 'name' in params:
                params['name']=params['name'].replace(' ','-');
                batch=batch+'#SBATCH --job-name=\"'+format(params['name'])+'\"\\n';
                
            batch=batch+'#SBATCH --export '+format(params['export'])+'\\n';
            batch=batch+'#SBATCH -c '+format(params['cores'])+'\\n'
            batch=batch+'#SBATCH --mem '+format(params['mem'])+'\\n'
            batch=batch+'#SBATCH -t '+format(params['time'])+'\\n'
            
            
                
            if (params['output']!=None):
                if not slurm_tools._check_if_valid_log_folder(params['output']):
                    print("#E: make sure that "+params['output']+" contains the full file path" )
                    print("#E: and that you have write perimssions" )
                    return "0", False
                batch=batch+'#SBATCH --output '+params['output']+'\\n';
                if params['error'] is None:
                    params['error'] = params['output']+"_err"
                
            if (params['error']!=None):
                if not slurm_tools._check_if_valid_log_folder(params['error']):
                    print("#E: make sure that "+params['error']+" contains the full file path" )
                    print("#E: and that you have write perimssions" )
                    return "0", False;
                batch=batch+'#SBATCH --error '+params['error']+'\\n';
                    
                    
            batch=batch+'#SBATCH -p '+format(params['queue'])+'\\n'
            if len(params['feature'])>0:
                batch=batch+'#SBATCH --constraint=\"'+format(params['feature'])+'\"\\n'

            if len(params['nodelist'])>0:
                batch=batch+'#SBATCH --nodelist='+format(params['nodelist'])+'\\n'
            if len(params['exclude'])>0:
                batch=batch+'#SBATCH --exclude='+format(params['exclude'])+'\\n'


            if len(params['gres'])>0:
                batch=batch+'#SBATCH --gres=\"'+format(params['gres'])+'\"\\n'

            if len(params['depends'])>0:
                    batch=batch+'#SBATCH --depends=afterok:'+(":".join(params['depends']))+'\\n'

            if params['append']:
                batch=batch+'#SBATCH --open-mode append\\n'
            else:
                batch=batch+'#SBATCH --open-mode truncate\\n'

            for command in commands:
                command = command.replace('$','\$')
                batch=batch+command+'\\n'


            batch=batch+'" | sbatch'

            if  params['debug']:
                batch="";
                for command in commands:
                    command.replace('"','\"')
                    batch=batch+command+';'
                    res, success=bash_run(batch)
                    res="0"

            else:

                if not params['quiet']:
                    print("#I: BATCH SCRIPT: ---------------------------------")
                    print(batch)
                    print("#I: -----------------------------------------------")
                batch='histchars=;'+batch+';unset histchars;'
                res, success = slurm_tools.bash_run(batch)
                if success:
                    res=res[0].split()[-1]
                    if not params['quiet']:
                        print(res)
                    job_state, success= slurm_tools.bash_run('squeue -h  --job '+res+'  -o "%t"')
                    if success:
                        job_state=[f for f in job_state[0].split("\n") if (len(f)>0)]
                        if len(job_state)==1:
                            success = ( job_state[0] in {'R','PD','CF','CG'} )
                        else:
                            print("#E: cannot find the JOB in the queue")
                            success=False

            return res, success
    
        @staticmethod
        def _wait_for_jobs(job_ids):
            if len(job_ids)==0:
                return False, True, 1

            jobids=",".join([str(f) for f in job_ids])

            job_state, success = slurm_tools.bash_run('squeue -h  --job '+jobids+'  -o "%t"')

            is_running=False

            if success:
                job_state=[f for f in job_state[0].split("\n") if (len(f)>0)]
                progress=len(job_ids)-len(job_state)
                for job in job_state:
                    running = ( job  in {'R','PD','CF','CG'} )
                    if not running:
                        progress += 1
                    if ( job in {'F','CA','TO','NF','SW'} ):
                        return False,False, 0
                    is_running=(is_running or running)

            else:
                progress = len(job_ids)

            return is_running, True, (float(progress)/float(len(job_ids)))


        @staticmethod
        def wait_for_jobs(jobids,progress_scale=(0,1)):
            print("waiting .....")
            progress_old=-1
            is_running=True
            while (is_running):
                is_running, success, progress =  slurm_tools._wait_for_jobs(jobids)
                if not success:
                    jobids=",".join([str(f) for f in jobids])
                    print("#W: warning, killing jobs")
                    job_state, success = slurm_tools.bash_run('scancel '+jobids)
                    if not success:
                        print("#W: "+job_state[1])
                else:
                    if progress!=progress_old:
                        progress_old = progress
                        print(int(100*(progress_scale[0]+progress_scale[1]*progress)))
                if is_running:
                    time.sleep( 10 )

            if not success:
                raise CPipeError("tracking jobs failed");
            
            print("done")

        @staticmethod
        def killall(jobids):
            if len(jobids)>0:
                jobids=",".join([str(f) for f in jobids])
                print("#W: warning, killing jobs")
                job_state, success = slurm_tools.bash_run('scancel '+jobids)
                if not success:
                    print("#W: "+job_state[1])
            else:
                print("#W: joblist is empty")
                




