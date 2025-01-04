from pyspark.sql import SparkSession
import pandas as pd

spark = SparkSession.builder.appName("GenerateSummaries").getOrCreate()

def generate_summary(parsed_files, output_file):
    rows = []
    for file in parsed_files:
        with open(file, "r") as f:
            rows.extend(f.readlines()[2:])  # Skip header lines
    df = pd.DataFrame([row.split(",") for row in rows], columns=["cath_id", "count"])
    spark_df = spark.createDataFrame(df)
    spark_df.groupBy("cath_id").sum("count").write.csv(output_file)

# Human Summary
generate_summary(["/data/HUMAN/*.parsed"], "/data/human_cath_summary.csv")

# E.Coli Summary
generate_summary(["/data/ECOLI/*.parsed"], "/data/ecoli_cath_summary.csv")
