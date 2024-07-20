import json
from test2va.generator.core.GUIMethodReader import get_gui_method
from test2va.generator.core.MethodGenerator import generate_all
import os

from .core.GUI import GUIMethod


# Define the folder path
def generator(input_path):
    task_parsed_report_path_list = []  # reports end wil _parsed.json

    # Iterate over all files in the folder
    for file_name in os.listdir(input_path):
        # Check if the file name ends with "_parsed.json"
        if file_name.endswith("_parsed.json"):
            # Construct the full file path
            task_parsed_report_path_list.append(os.path.join(input_path, file_name))

    task_total = len(task_parsed_report_path_list)
    index = 0
    while index < task_total:
        task_parsed_report_path = task_parsed_report_path_list[index]
        task_mutant_report_path = task_parsed_report_path.replace("java_parsed", "mutate_res")

        print(task_parsed_report_path)
        print(index)

        # 1. generating GUIMethod obj to represent the task method in the report
        test_method: GUIMethod = get_gui_method(task_parsed_report_path,
                                                task_mutant_report_path)

        # 2. Output the method as code
        generate_all(test_method, "java", task_mutant_report_path)

        index += 1
