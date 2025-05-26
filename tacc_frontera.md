# TACC-Frontera
## Build MiV Environment 

virtualenv seems to be a easier way to create virtual env here.
Main website:
```shell
# Portal:
https://frontera-portal.tacc.utexas.edu/
# Dashboard:
https://frontera-portal.tacc.utexas.edu/workbench/dashboard
```
Store your large files in scratch, not home and work.
<img width="208" alt="Screenshot 2025-05-25 at 9 41 13 PM" src="https://github.com/user-attachments/assets/26c1b452-205f-41cd-ba8b-22a3d32eb602" />

When you first create env:
```shell
# bulid Python virtualenv
cd ~
# This means you will create your env in home directory.

mkdir python-env
cd python-env

# Create env for MiV
virtualenv miv_env

# active environment
source ~/python-env/miv_env/bin/activate

# deactivate environment
deactivate　

# you can use pip to install packages
```
Install MiV-os:
```shall
# First load python 3.9, or you mivos will not work, you can first check available python:
module avail python

# Then load newer python:
module load python3/3.9.2

# Then activate you env:
source ~/python-env/miv_env/bin/activate

# install
pip install MiV-OS

# This should be enough to run miv-os code

# When you plan to run a file:
cd /your/path/to/jobscript/
sbatch jobscript.txt # <-change this to your job script's name
```

## Common Commands

```shell
# To directory $SCRATCH. The default directory is $HOME when you login in.
cd $SCRATCH

# check your job status
squeue -u your_account

# delete your job
scancel job_ID

# view loaded module
# module related commands need at computing node
module list

# view avail module
module avail
```

## Job Script Example

```shell
#!/bin/bash

#SBATCH -J NWB_mpi           # Job name
#SBATCH -o NWB_mpi.o%j       # Name of stdout output file
#SBATCH -e NWB_mpi.e%j       # Name of stderr error file

#SBATCH -p development          # Queue (partition) name
#SBATCH -N 4             # Total # of nodes
#SBATCH -n 8             # Total # of mpi tasks
#SBATCH -t 02:00:00        # Run time (hh:mm:ss)
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A IBN22011       # Project/Allocation name (req'd if you have more than 1)
#SBATCH --mail-user=qixianw2@illinois.edu

module load python3/3.9.2  # load the modules you need

module list 
pwd
date

ibrun python3 /scratch1/10197/qxwang/NWB_MPI/nwb_test_2.py # <- change this name
```

You should use ibrun instead of mpirun or mpiexec here, and -np means total GPU numbers.
