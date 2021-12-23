import glob
import json
import os

from analyse import worthwhite
from src.interface.results import combine_results, final_results

# list_file = [f for f in glob.glob("data/demo_analysis/source_code/*.sol")]
# list_tool = ["mythril","slither","oyente","honeybadger"]
list_file = ["data/demo_analysis/source_code/0x0cbe050f75bc8f8c2d6c0d249fea125fd6e1acc9.sol"]
list_tool = ["mythril"]
project_name = "thaovttest1"
worthwhite(list_tool=list_tool, list_file=list_file,project_name=project_name,aggregate_sarif=True,unique_sarif_output=False)
# print("Phân tích từng tool xong")
# folder_results = os.path.join("data/", project_name)
# info_wortwhile_path = os.path.join(folder_results, "info_wortwhile.json")
# with open(info_wortwhile_path, 'r') as file:
#     info_wortwhile_data = json.load(file)
# info_wortwhile = info_wortwhile_data.get("list_file_wortwhile")
# if info_wortwhile is not None:
#     list_file = info_wortwhile["list_file"]
#     data_file_tool = info_wortwhile["data"]
#     for file in list_file:
#         results_folder = os.path.join("data/", project_name,"results/")
#         tool_of_file = data_file_tool[file]
#         file_name = os.path.splitext(file)[0]
#         for tool in tool_of_file:
#             combine_results(tool, file_name, results_folder)
#         data_final_results = final_results(file_name, results_folder,project_name)
print("đã xong")