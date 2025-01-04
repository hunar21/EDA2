from pyspark import SparkContext
import subprocess
import os

# Function to run Merizo search
def run_merizo_search(input_file):
    cmd = [
        'python3', '/path/to/merizo.py', 'easy-search', input_file,
        '/path/to/database/cath-4.3-foldclassdb',
        f"{input_file}_output", "/tmp", "--output_headers"
    ]
    subprocess.run(cmd, check=True)
    return f"Merizo search completed for {input_file}"

# Function to run results parser
def run_parser(input_file):
    output_dir = "/output_dir/"
    search_file = f"{input_file}_output_search.tsv"
    cmd = ['python', '/path/to/results_parser.py', output_dir, search_file]
    subprocess.run(cmd, check=True)
    return f"Parsing completed for {input_file}"

# Function to process each file
def process_protein(input_file):
    run_merizo_search(input_file)
    run_parser(input_file)
    return f"Processing completed for {input_file}"

if __name__ == "__main__":
    # Initialize Spark
    sc = SparkContext(appName="ProteinProcessing")

    # Load input files (assuming they're in HDFS)
    input_dir = "hdfs://master:9000/input/"
    input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.pdb')]

    # Distribute the workload
    rdd = sc.parallelize(input_files)
    results = rdd.map(process_protein).collect()

    # Print results
    for result in results:
        print(result)