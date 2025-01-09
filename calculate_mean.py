import os
import sys
import csv

def calculate_mean_plddt(input_dir, output_file):
    # Collect all .parsed files from the input directory
    parsed_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".parsed")]

    if not parsed_files:
        print(f"No .parsed files found in directory {input_dir}")
        sys.exit(1)

    plDDT_values = []

    for file_path in parsed_files:
        with open(file_path, "r") as file:
            for line in file:
                if "mean plddt" in line.lower():
                    try:
                        value = float(line.split(":")[1].strip())
                        plDDT_values.append(value)
                    except ValueError:
                        print(f"Skipping invalid line in {file_path}: {line.strip()}")

    # Calculate the mean and standard deviation
    if plDDT_values:
        overall_mean = sum(plDDT_values) / len(plDDT_values)
        overall_stddev = (sum([(x - overall_mean) ** 2 for x in plDDT_values]) / (len(plDDT_values) - 1)) ** 0.5
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
        print("Usage: python calculate_mean.py <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]  # Path to input directory
    output_dir = sys.argv[2]  # Base path for output
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "pl_DDT_means.csv")

    calculate_mean_plddt(input_dir, output_file)
