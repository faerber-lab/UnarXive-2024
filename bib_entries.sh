#!/bin/bash
#SBATCH --job-name=bib_entries            
#SBATCH --nodes=1                      
#SBATCH --ntasks=1                     
#SBATCH --cpus-per-task=8              
#SBATCH --mem=64G                      
#SBATCH --gres=gpu:1              
#SBATCH --time=5:00:00   
#SBATCH --output=bib_entries.out
#SBATCH --error=duplicbib_entriesates.err
# No modules needed for rsync over SSH
# If needed, load SSH/rsync environment modules here (typically not required)
source ../env/bin/activate  

python3 count_matched_bib.py

