import json
import os


def combine_results(tool,project_name,file_name,results_folder):
    # create file combine_results
    combine_results_path = 'data/' + project_name + "/results/" + file_name + '/combine_results.json'
    if os.path.exists(combine_results_path):
        with open(combine_results_path, 'r') as combine_results_file:
            combine_result = json.load(combine_results_file)
    else:
        combine_result = {}
    output_folder = os.path.join(results_folder, file_name)
    file_name_sarif_output = tool + '_result.sarif'
    with open(os.path.join(output_folder, file_name_sarif_output), 'w') as sarifFile:
        sarif_data = json.load(sarifFile)
    # print("sarif_data")
    # print(sarif_data)
