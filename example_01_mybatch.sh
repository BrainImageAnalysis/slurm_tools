#!/bin/bash
#SBATCH --gres=gpu:1
#SBATCH --mem 16G
#SBATCH -c 10
#SBATCH -t 240
#SBATCH -o ./example01_mybatch.out
#SBATCH -e ./example01_mybatch.out
echo $HOSTNAME
source /disk/soft/MODULES/init.sh
source /etc/profile.d/modules.sh
module load matlab/v2016
which matlab
module unload matlab/v2016
module load matlab/v2019
which matlab
PARAM=1
matlab -r "myvar = ${PARAM}; fprintf('this is a matlab session with parameter %d\n',myvar);exit;"
sleep 5
echo "done"
