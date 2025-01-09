from pyspark import SparkContext, SparkConf
import os
import subprocess
import socket
import sys

def get_host_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception as e:
        print(f"Error retrieving host IP: {e}")
        return None

def run_merizo(input_file, output_dir):
    try:
        output_file = os.path.join(output_dir, os.path.basename(input_file) + "_search.tsv")
        cmd = [
            'python3', '/data/local/pipeline_scripts/merizo/merizo_search/merizo.py', 'easy-search', input_file,
            '/data/local/extracted/db/cath-4.3-foldclassdb', output_file, 'tmp',
            '--output_headers', '-d', 'cpu'
        ]
        subprocess.run(cmd, check=True)
        output_file = output_file + "_search.tsv"
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error running Merizo Search for {input_file}: {e}")
        return None

def run_parser(search_file):
    if not search_file:
        print("No search file provided to run_parser.")
        return None

    try:
        cmd = ['python', '/data/local/pipeline_scripts/results_parser.py', os.path.abspath(search_file)]
        subprocess.run(cmd, check=True)
        return search_file.replace("_search.tsv", ".parsed")
    except subprocess.CalledProcessError as e:
        print(f"Error running Results Parser for {search_file}: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: spark-submit pipeline_script.py <input_directory> <output_directory>")
        sys.exit(1)
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    host_ip = get_host_ip()
    if not host_ip:
        print("Failed to determine the host IP address. Exiting.")
        exit(1)


    # Setup Spark configuration
    conf = (
        SparkConf()
        .setAppName("MerizoPipeline")
        .setMaster(f"spark://{host_ip}:7077")
        .set("spark.executor.memory", "24g")
        .set("spark.executor.cores", "4")
        .set("spark.dynamicAllocation.executorIdleTimeout", "600s")
        .set("spark.task.maxFailures", "4")  # Retry tasks up to 4 times
    )
    sc = SparkContext(conf=conf)

    # Directory containing .pdb files
    pdb_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdb")]
    print(f"Found {len(pdb_files)} .pdb files in {input_dir}")

    # Step 1: Parallelize Merizo Search across the cluster
    num_partitions = 24  # Adjusted to better utilize the cluster
    search_files = sc.parallelize(pdb_files, numSlices=num_partitions).map(lambda file: run_merizo(file, output_dir)).collect()
    print(f"Generated search files: {search_files}")

    # Step 2: Parallelize Results Parsing across the cluster
    parsed_files = sc.parallelize(search_files, numSlices=num_partitions).map(run_parser).collect()
    print("Pipeline execution completed.")

    # Logging results
    successful_searches = [sf for sf in search_files if sf is not None]
    successful_parses = [pf for pf in parsed_files if pf is not None]

    print(f"Successfully processed {len(successful_searches)} files with run_merizo.")
    print(f"Successfully parsed {len(successful_parses)} files with run_parser.")