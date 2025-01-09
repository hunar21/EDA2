import os
import sys
import pandas as pd
from glob import glob

def merge_parsed_files(input_dir, output_csv):
    # Collect all .parsed files from the input directory
    parsed_files = glob(os.path.join(input_dir, "*.parsed"))
    
    if not parsed_files:
        print(f"No .parsed files found in directory {input_dir}")
        sys.exit(1)

    # Initialize an empty DataFrame to hold merged data
    merged_data = pd.DataFrame(columns=["cath_code", "count"])

    for file_path in parsed_files:
        # Read the file, skip the header
        file_data = pd.read_csv(file_path, skiprows=1, header=None, names=["cath_code", "count"])
        merged_data = pd.concat([merged_data, file_data], ignore_index=True)

    # Remove rows where cath_code is "cath_id"
    merged_data = merged_data[merged_data["cath_code"] != "cath_id"]

    # Ensure "count" is of integer type
    merged_data["count"] = merged_data["count"].astype(int)

    # Aggregate by cath_code
    aggregated_data = merged_data.groupby("cath_code", as_index=False).sum()

    # Save the aggregated data to a CSV file
    aggregated_data.to_csv(output_csv, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python summarise_script.py <input_dir> <output_dir> <output_name>")
        sys.exit(1)

    input_dir = sys.argv[1]  # Path to input directory
    output_dir = sys.argv[2]  # Base path for output
    output_name = sys.argv[3]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    output_csv = os.path.join(output_dir, output_name + "_cath_summary.csv")

    # Merge and process the parsed files
    merge_parsed_files(input_dir, output_csv)

    print(f"Merged output saved at {output_csv}")
