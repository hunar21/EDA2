def calculate_mean_plddt(parsed_files, output_file):
    mean_values = []
    for file in parsed_files:
        with open(file, "r") as f:
            lines = f.readlines()
            mean_values.append(float(lines[1].split(":")[1].strip()))  # Extract mean plDDT
    overall_mean = sum(mean_values) / len(mean_values)
    with open(output_file, "w") as f:
        f.write(f"mean_plDDT: {overall_mean}\n")

# Calculate mean for Human and E.Coli
calculate_mean_plddt(["/data/HUMAN/*.parsed"], "/data/human_plDDT_means.csv")
calculate_mean_plddt(["/data/ECOLI/*.parsed"], "/data/ecoli_plDDT_means.csv")
