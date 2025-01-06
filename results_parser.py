import sys
import csv
import json
from collections import defaultdict
import statistics

# Get the input search file
search_file = sys.argv[1]
output_file = search_file.replace("_search.tsv", ".parsed")

cath_ids = defaultdict(int)
plDDT_values = []

with open(search_file, "r") as fhIn:
    next(fhIn)
    msreader = csv.reader(fhIn, delimiter='\t') 
    tot_entries = 0
    for i, row in enumerate(msreader):
        tot_entries = i + 1
        plDDT_values.append(float(row[3]))
        meta = row[15]
        data = json.loads(meta)
        cath_ids[data["cath"]] += 1

with open(output_file, "w", encoding="utf-8") as fhOut:
    if plDDT_values:
        fhOut.write(f"#{search_file} Results. mean plddt: {statistics.mean(plDDT_values)}\n")
    else:
        fhOut.write(f"#{search_file} Results. mean plddt: 0\n")
    fhOut.write("cath_id,count\n")
    for cath, v in cath_ids.items():
        fhOut.write(f"{cath},{v}\n")
