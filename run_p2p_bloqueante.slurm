#!/bin/bash
#SBATCH --job-name=mpi_p2p_bloqueante
#SBATCH --partition=hype
#SBATCH --time=2:00:00
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

declare -a nodes_array=("2" "4" "8")  
declare -a ntasks_array=("40" "80" "160")  
declare -a n_sizes=("1024" "2048" "4096" "8192") 

OUTPUT_FILE="benchmark_results_mpi_p2p_bloqueante.out"

for nodes in "${nodes_array[@]}"; do
    for ntasks in "${ntasks_array[@]}"; do
        for n in "${n_sizes[@]}"; do
            # Create machinefile dynamically with hostname info
            MACHINEFILE="nodes.$SLURM_JOB_ID"
            srun -l hostname | sort -n | awk '{print $2}' > $MACHINEFILE

            # Update SLURM script for the new nodes and ntasks values
            sed -i "s/#SBATCH --nodes=[0-9]\+/#SBATCH --nodes=$nodes/" $SLURM_SCRIPT
            sed -i "s/#SBATCH --ntasks=[0-9]\+/#SBATCH --ntasks=$ntasks/" $SLURM_SCRIPT

            # Print configuration info to output file
            echo "Running with Nodes: $nodes, NTASKS: $ntasks, N Size: $n" >> $OUTPUT_FILE
            echo "SLURM Job Node List: $SLURM_JOB_NODELIST" >> $OUTPUT_FILE
            echo "-----------------------------" >> $OUTPUT_FILE

            # Run MPI program with appropriate arguments and log output
            mpirun -np $ntasks \
                   -machinefile $MACHINEFILE \
                   --mca btl ^openib \
                   --mca btl_tcp_if_include eno2 \
                   --bind-to none ./mpi_p2p_bloqueante $n >> $OUTPUT_FILE
                   
            # Separator in output file
            echo "=============================" >> $OUTPUT_FILE
        done
    done
done
