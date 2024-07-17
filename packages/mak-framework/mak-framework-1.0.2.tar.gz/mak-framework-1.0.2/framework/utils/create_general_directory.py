import os
import json
from datetime import datetime


def read_json(filename):
    """
    Reads JSON data from a file.

    Args:
    - filename (str): The path to the JSON file.

    Returns:
    - dict: The parsed JSON data.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON from '{filename}'.")
        return None


def get_file(filename, file_extension=""):
    """
    Locates a file within the directory structure.

    Args:
    - filename (str): The name of the file to locate.
    - file_extension (str): Optional extension filter for the file.

    Returns:
    - str or None: The path to the file if found, otherwise None.
    """
    current_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file_extension == "" or file.endswith(file_extension):
                if file == filename:
                    return os.path.join(root, file)
    return None


def create_directories(base_dir: str):
    """
    Creates necessary directory structure for reports.

    Args:
    - base_dir (str): The base directory path.

    Returns:
    - str: The path to the 'Results' directory created.
    """
    try:
        base_dir = os.path.normpath(base_dir)
        reports_dir = os.path.join(base_dir, "Reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%d-%m-%Y---%I-%M-%S-%p')
        results_dir = os.path.join(reports_dir, f"Results---{timestamp}")
        os.makedirs(results_dir, exist_ok=True)

        return results_dir
    except OSError as e:
        print(f"Error: Failed to create directories - {e}")
        return None


try:
    jsonFile = get_file('results_dir.json')
    if jsonFile:
        data = read_json(jsonFile)
        if data:
            base_directory = data.get('base_directory', '')
        else:
            print("Failed to read JSON data from file. Using default directory.")
            base_directory = 'D:\\'
    else:
        print("Failed to locate JSON file. Using default directory.")
        base_directory = 'D:\\'

    RESULTS_DIR = create_directories(base_directory)
    if RESULTS_DIR:
        print(f"Results directory created at: {RESULTS_DIR}")
    else:
        print("Failed to create results directory.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
