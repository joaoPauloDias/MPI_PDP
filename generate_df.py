import os
import re
import pandas as pd

def parse_filename(filename):
    pattern = r"mpi_(?P<comm_type>(p2p_\w+|coletiva))_nodes(?P<nodes>\d+)_ntasks(?P<tasks>\d+)_nsize(?P<nsize>\d+)_(?P<id>\d+)"
    match = re.match(pattern, filename)
    if match:
        return match.groupdict()
    return None

def parse_file_content(file_path):
    with open(file_path, 'r') as f:
        content = f.readlines()
        
        if len(content) < 4:
            print(f"Warning: Skipping file {file_path} (not enough content).")
            return None
        
        comm_type = content[0].strip()
        matrix_size = int(content[1].split(":")[1].strip())
        execution_time = float(content[2].split(":")[1].strip())
        comm_time = float(content[3].split(":")[1].strip())
    
    return comm_type, matrix_size, execution_time, comm_time

def categorize_files(directory):
    data = []

    for filename in os.listdir(directory):
        if filename.endswith(".out"):
            parsed_data = parse_filename(filename)
            if parsed_data:
                file_path = os.path.join(directory, filename)
                parsed_content = parse_file_content(file_path)
                if parsed_content:
                    comm_type, matrix_size, execution_time, comm_time = parsed_content

                    data.append({
                        'comm_type': parsed_data['comm_type'],
                        'nodes': parsed_data['nodes'],
                        'tasks': parsed_data['tasks'],
                        'nsize': parsed_data['nsize'],
                        'matrix_size': matrix_size,
                        'execution_time': execution_time,
                        'comm_time': comm_time
                    })
    
    df = pd.DataFrame(data)
    return df

folder_path = "/home/jpdias/Documents/mpi/MPI_PDP"

df = categorize_files(folder_path)

csv_file_path = "mpi_data.csv"

df.to_csv(csv_file_path, index=False)

print(f"Data has been written to {csv_file_path}")
