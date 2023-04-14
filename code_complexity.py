# create python code to load each python file from a directory called "python_files", and for each file compute cyclomatic complexity, maintainability index, and halsted complexity metrics for each file using the radon package
# followed by: please store the results for each of the metrics to a dictionary that is keyed by the file name
# follwed by: the radon python package does not work with python 3.9.  Instead please use the radon command line interface to run each analysis.
# followed by: cc_result[file_path] is a list rather than a dictionary. please store this list directly to the metrics dictionary
# followed by: please wrap the call to analyze_file within a try/catch loop to catch KeyErrors that will occur if the file fails to be processed.
# followed by: please save the resulting metrics dictionary to a pickle file. 
# followed by: you are using the wrong command for the halsead metrics. please use 'radon hal' to compute those metrics.  in addition, please save the raw metrics obtained using 'radon raw' to the metrics dictionary as well.
# metrics['cyclomatic_complexity'] is a list rather than a dictionary.  please loop over it accordingly.

# additional manual fixes by RP


import os
import json
import subprocess
import pickle

def analyze_python_files(directory):
    results = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    results[file] = analyze_file(file_path)
                except KeyError as e:
                    print(f"Error processing {file}: {e}")
    return results

def analyze_file(file_path):
    metrics = {}

    # Compute cyclomatic complexity
    cc_output = subprocess.run(['radon', 'cc', '-j', file_path], capture_output=True, text=True)
    cc_result = json.loads(cc_output.stdout)
    metrics['cyclomatic_complexity'] = cc_result[file_path]

    # Compute Halstead metrics
    h_output = subprocess.run(['radon', 'hal', '-j', file_path], capture_output=True, text=True)
    h_result = json.loads(h_output.stdout)
    metrics['halstead_complexity'] = h_result[file_path]

    # Compute raw metrics
    raw_output = subprocess.run(['radon', 'raw', '-j', file_path], capture_output=True, text=True)
    raw_result = json.loads(raw_output.stdout)
    metrics['raw_metrics'] = raw_result[file_path]

    # Compute maintainability index
    mi_output = subprocess.run(['radon', 'mi', '-j', file_path], capture_output=True, text=True)
    mi_result = json.loads(mi_output.stdout)
    metrics['maintainability_index'] = mi_result[file_path]

    flake8_output = subprocess.run(['flake8', file_path], capture_output=True, text=True)
    metrics['flake8'] = flake8_output.stdout.strip().split("\n")

    return metrics


def save_to_pickle(data, file_name):
    with open(file_name, 'wb') as f:
        pickle.dump(data, f)


if __name__ == '__main__':
    directory =  'github_code' #  'chatgpt_code' #
    results = analyze_python_files(directory)

    # Save the results to a pickle file
    pickle_file = f'metrics_{directory}.pickle'
    save_to_pickle(results, pickle_file)

    for file_name, metrics in results.items():
        print(f"File: {file_name}")
        print("Cyclomatic Complexity:")
        if isinstance(metrics['cyclomatic_complexity'], dict) and 'error' in metrics['cyclomatic_complexity']:
            print(f" - {metrics['cyclomatic_complexity']['error']}")
        else:
            for item in metrics['cyclomatic_complexity']:
                function = item['name']
                complexity = item['complexity']
                print(f" - Function: {function} - CC: {complexity}")
        print(f"Halstead complexity: {metrics['halstead_complexity']}")
        print(f"Raw metrics: {metrics['raw_metrics']}")
        print(f"Maintainability index: {metrics['maintainability_index']}\n")
