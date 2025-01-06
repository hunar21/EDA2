from pyspark.sql import SparkSession
import os
from glob import glob
import sys

def merge_parsed_files(input_dir, output_csv):
    spark = SparkSession.builder.appName("MergeParsedFiles").getOrCreate()
    text_rdd = spark.sparkContext.wholeTextFiles(f"{input_dir}/*.parsed")

    # Process each file: remove first line (mean plDDT) and split remaining lines
    def process_file(file_content):
        file_lines = file_content.splitlines()
        return file_lines[1:]  # Skip the first line

    data_rdd = (
        text_rdd.flatMap(lambda file: process_file(file[1]))
                .map(lambda line: line.split(','))  # Split lines into cath_id and count
    )

    df = spark.createDataFrame(data_rdd, ["cath_code", "count"])
    df = df.filter(df.cath_code != "cath_id")
    df.coalesce(1).write.csv(output_csv, header=True, mode="overwrite")

if __name__ == "__main__":
     # Parse arguments
    if len(sys.argv) != 4:
        print("Usage: spark-submit summarise_script.py <input_dir> <output_dir> <output_name>")
        sys.exit(1)

    input_dir = sys.argv[1]  # Path to input directory
    output_dir = sys.argv[2]  # Base path for output
    output_name = sys.argv[3]

    # Merge parsed files
    merge_parsed_files(input_dir, output_dir)

     # Rename the output file to the desired final name
    part_files = glob(f"{output_dir}/part-*.csv")
    if len(part_files) == 1:
        os.rename(part_files[0], os.path.join(output_dir, output_name+"_cath_summary.csv"))
        print(f"Merged output saved at {os.path.join(output_dir, 'summary.csv')}")
    else:
        print(f"Unexpected number of part files: {part_files}")

    # Optional: Remove additional files like _SUCCESS
    success_file = os.path.join(output_dir, "_SUCCESS")
    if os.path.exists(success_file):
        os.remove(success_file)
