import json
import os
from multiprocessing import Manager

from src.output_parser.HoneyBadger import HoneyBadger
from src.output_parser.Mythril import Mythril
from src.output_parser.Oyente import Oyente
from src.output_parser.SarifHolder import SarifHolder
from src.output_parser.Slither import Slither

manager = Manager()
sarif_outputs = manager.dict()
file_names = ["integer_overflow_mul","integer_overflow_minimal","reentrance"]
list_tool =["slither","oyente"]
project_name = "demo_analysis"
folder_results = os.path.join("data/", project_name)
info_wortwhile_path = os.path.join(folder_results, "info_wortwhile.json")
with open(info_wortwhile_path, 'r') as file:
    info_wortwhile_data = json.load(file)
info_wortwhile = info_wortwhile_data.get("list_file_wortwhile")
if info_wortwhile is not None:
    file_names = info_wortwhile["list_file"]
# project_name = "thaovttest1"
for tool in list_tool:
    for file_name in file_names:
        file_name = os.path.splitext(os.path.basename(file_name))[0]
        sarif_outputs[file_name] = SarifHolder()
        with open('data/'+ project_name + '/results/'+ file_name+ '/'+ tool + '_result.json', 'r') as f:
            results = json.load(f)
        sarif_holder = sarif_outputs[file_name]
        file_path_in_repo = 'data/'+ project_name + '/source_code/'+ file_name+ '.sol'
        if tool == 'oyente':
            # Sarif Conversion
            sarif_holder.addRun(Oyente().parseSarif(results, file_path_in_repo))
        elif tool == 'honeybadger':
            sarif_holder.addRun(HoneyBadger().parseSarif(results, file_path_in_repo))
        elif tool == 'mythril':
            # results['analysis'] = json.loads(output)
            sarif_holder.addRun(Mythril().parseSarif(results, file_path_in_repo))
        elif tool == 'slither':
            # file_name_tar_output = tool + '_result.tar'
            # if os.path.exists(os.path.join(output_folder, file_name_tar_output)):
            #     tar = tarfile.open(os.path.join(output_folder, file_name_tar_output))
            #     output_file = tar.extractfile('output.json')
            #     results['analysis'] = json.loads(output_file.read())
            sarif_holder.addRun(Slither().parseSarif(results, file_path_in_repo))

        sarif_outputs[file_name] = sarif_holder
        with open('data/'+ project_name + '/results/'+ file_name+ '/'+ tool + '_result.sarif', 'w') as sarifFile:
            json.dump(sarif_outputs[file_name].printToolRun(tool=tool), sarifFile, indent=2)