from pyspark.sql import SparkSession
import sys
import os
import csv

def calculate_mean_plddt(input_dirs, output_files):

    spark = SparkSession.builder.appName("CalculateMeanPLDDT").getOrCreate()
    df = spark.read.text(f"file://{input_dir}/*.parsed")
    plDDT_values = (
            df.rdd
            .map(lambda row: float(row.value.split(":")[1].strip()) if "mean plddt" in row.value.lower() else None)
            .filter(lambda x: x is not None)
            .collect())

    # Calculate the mean
    if len(plDDT_values) > 0:
        overall_mean = sum(plDDT_values) / len(plDDT_values)
        overall_stddev = (sum([(x - overall_mean) ** 2 for x in plDDT_values]) / len(plDDT_values)) ** 0.5
    else:
        overall_mean = 0.0
        overall_stddev = 0.0

    # Write the results to the output file
    with open(output_file, "w", newline="\n") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["mean_plDDT", "plDDT_std"])
        writer.writeheader()
        writer.writerow({"mean_plDDT": overall_mean, "plDDT_std": overall_stddev})


    print(f"Mean and standard deviation written to {output_file}")

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: spark-submit calculate_mean.py <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]  # Path to input directory
    output_dir = sys.argv[2]  # Base path for output
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "pl_DDT_means.csv")
   
    calculate_mean_plddt(input_dir, output_file)
