import os
import subprocess

nodes_array = ["1", "2", "4"]
ntasks_array = ["40", "80", "160"]
n_sizes = ["512", "1024", "2048", "4096"]
file_names = ["mpi_coletiva", "mpi_p2p_bloqueante", "mpi_p2p_naobloqueante"]

batch_script_dir = "batch_scripts"
os.makedirs(batch_script_dir, exist_ok=True)

for nodes in nodes_array:
    for ntasks in ntasks_array:
        for n_size in n_sizes:
            for file_name in file_names:
                job_name = f"{file_name}_nodes{nodes}_ntasks{ntasks}_nsize{n_size}"
                output_file = f"{job_name}_%j.out"

                # Check if the output file already exists
                if not any(file.startswith(f"{job_name}_") and file.endswith(".out") for file in os.listdir('.')):
                    batch_script_content = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition=hype
#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}
#SBATCH --time=2:00:00
#SBATCH --output={output_file}
#SBATCH --error={job_name}_%j.err

MACHINEFILE="nodes.$SLURM_JOB_ID"
srun -l hostname | sort -n | awk '{{print $2}}' > $MACHINEFILE

mpirun -np $SLURM_NTASKS \\
       -machinefile $MACHINEFILE \\
       --mca btl ^openib \\
       --mca btl_tcp_if_include eno2 \\
       --bind-to none -np $SLURM_NTASKS \\
       ./{file_name} {n_size}
"""

                    batch_script_path = os.path.join(batch_script_dir, f"{job_name}.sh")
                    with open(batch_script_path, 'w') as batch_script_file:
                        batch_script_file.write(batch_script_content)

                    subprocess.run(["sbatch", batch_script_path])
                else:
                    print(f"Skipping job {job_name} as the output file already exists.")
