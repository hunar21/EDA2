import argparse
import os
import time
import pickle
import socket
import numpy as np
import pandas as pd
from pyspark import SparkConf, SparkContext
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def get_host_ip():
    """
    Returns the IP address of the current host.
    This is used to set the Spark master URL automatically.
    """
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception as e:
        print(f"Error retrieving host IP: {e}")
        return None

# Preprocessing function (same as in test.py)
def load_and_preprocess(csv_file, sequence_length=60, scaler=None, is_training=False):
    data = pd.read_csv(csv_file)
    data['Date'] = pd.to_datetime(data['Date'])
    data.sort_values('Date', inplace=True)
    data.set_index('Date', inplace=True)
    data = data.dropna(subset=['Close'])
    close_data = data['Close'].values.reshape(-1, 1)
    
    if is_training:
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(close_data)
    else:
        scaled_data = scaler.transform(close_data)
    
    X, y = [], []
    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i-sequence_length:i, 0])
        y.append(scaled_data[i, 0])
    
    if len(X) == 0:
        return np.empty((0, sequence_length, 1)), np.empty((0,)), scaler
    
    X = np.array(X)
    y = np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y, scaler

def process_partition(files, sequence_length, scaler_path, model_path):
    """
    In each partition, load the model and scaler once (assuming these files
    reside on a shared filesystem accessible at the given absolute paths).
    Then, process each CSV file in the partition.
    """
    try:
        model = load_model(model_path)
    except Exception as e:
        print(f"Error loading model from {model_path}: {e}")
        raise e
    try:
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
    except Exception as e:
        print(f"Error loading scaler from {scaler_path}: {e}")
        raise e
    
    results = []
    for csv_file in files:
        try:
            print(f"Processing {csv_file} ...")
            X_test, y_test, _ = load_and_preprocess(csv_file, sequence_length=sequence_length, scaler=scaler, is_training=False)
            if X_test.size == 0:
                msg = f"Not enough data to form sequences for {csv_file}."
                print(msg)
                results.append(msg)
                continue

            predictions = model.predict(X_test)
            predictions_actual = scaler.inverse_transform(predictions)
            y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
            
            # Check for NaN values
            if np.isnan(predictions_actual).any() or np.isnan(y_test_actual).any():
                msg = f"NaN values found in predictions or actual values for {csv_file}."
                print(msg)
                results.append(msg)
                continue

            mse = mean_squared_error(y_test_actual, predictions_actual)
            mae = mean_absolute_error(y_test_actual, predictions_actual)
            r2 = r2_score(y_test_actual, predictions_actual)
            
            tolerance = 0.05  # 5% tolerance
            epsilon = 1e-8
            relative_errors = np.abs(y_test_actual - predictions_actual) / (np.abs(y_test_actual) + epsilon)
            accuracy = np.mean(relative_errors < tolerance) * 100

            # Write the accuracy to an output file (overwriting if it exists)
            output_txt_filename = csv_file.replace('.csv', '_accuracy.txt')
            with open(output_txt_filename, 'w') as f:
                f.write(f"{accuracy:.2f}%\n")
            msg = f"Processed {csv_file} with accuracy {accuracy:.2f}%."
            print(msg)
            results.append(msg)
        except Exception as e:
            error_msg = f"Error processing {csv_file}: {str(e)}"
            print(error_msg)
            results.append(error_msg)
    return results

def main():
    parser = argparse.ArgumentParser(
        description='Distributed test.py job using PySpark'
    )
    parser.add_argument('--csv_dir', type=str, required=True, help='Directory containing CSV files')
    parser.add_argument('--sequence_length', type=int, default=60, help='Number of days per sequence')
    parser.add_argument('--iterations', type=int, default=10, help='Number of iterations to run')
    # Use absolute paths for model and scaler files on shared storage (e.g., NFS)
    parser.add_argument('--model_path', type=str, default='/data/local/pipeline_scripts/stock_lstm_model.h5', help='Absolute path to the Keras model file')
    parser.add_argument('--scaler_path', type=str, default='/data/local/pipeline_scripts/scaler.pkl', help='Absolute path to the scaler pickle file')
    args = parser.parse_args()

    # Get list of CSV files from the specified directory
    csv_files = [os.path.join(args.csv_dir, f) for f in os.listdir(args.csv_dir) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the provided directory.")
        return

    # Dynamically obtain the host IP and use it as the master
    host_ip = get_host_ip()
    if not host_ip:
        print("Failed to determine host IP. Exiting.")
        return
    print(f"Using host IP: {host_ip} as Spark master.")

    # Initialize Spark context with master set to the discovered IP
    conf = SparkConf().setAppName("DistributedTestJob").setMaster(f"spark://{host_ip}:7077")
    sc = SparkContext(conf=conf)

    start_time = time.time()
    
    # Increase the number of partitions to leverage parallelism (adjust numSlices as needed)
    files_rdd = sc.parallelize(csv_files, numSlices=12)

    for iteration in range(args.iterations):
        print(f"\n--- Iteration {iteration+1} of {args.iterations} ---")
        iteration_results = files_rdd.mapPartitions(
            lambda files: process_partition(list(files), args.sequence_length, args.scaler_path, args.model_path)
        ).collect()
        for res in iteration_results:
            print(res)

    sc.stop()
    total_time = time.time() - start_time
    print(f"\n--- Total Processing Time: {total_time:.2f} seconds ---")

if __name__ == '__main__':
    main()
