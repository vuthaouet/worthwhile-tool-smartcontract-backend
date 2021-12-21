#!/usr/bin/env python3

import json
import os
import pathlib
import sys
import yaml

from datetime import timedelta
from multiprocessing import Manager, Pool

from src.docker_api.docker_api import analyse_files
from src.output_parser.SarifHolder import SarifHolder
from time import time, localtime, strftime


cfg_dataset_path = os.path.abspath('config/dataset/dataset.yaml')
# with open(cfg_dataset_path, 'r') as ymlfile:
#     try:
#         cfg_dataset = yaml.safe_load(ymlfile)
#         # print('cfg_dataset')
#         # print(cfg_dataset)
#     except yaml.YAMLError as exc:
#         print(exc)

output_folder = strftime("%Y%d%m", localtime())
pathlib.Path('results/logs/').mkdir(parents=True, exist_ok=True)
logs = open('results/logs/Analyse_' + output_folder + '.log', 'w')



def analyse(args):
    global logs, output_folder
    (tool, file,project_name, sarif_outputs, import_path, output_version, nb_task, nb_task_done, total_execution, start_time) = args
    info_wortwhile_path = 'data/'+ project_name + '/info_wortwhile.json'
    if os.path.exists(info_wortwhile_path):
        with open(info_wortwhile_path, 'r') as info_wortwhile:
            data_info_wortwhile = json.load(info_wortwhile)
    else:
        data_info_wortwhile ={}
        data_info_wortwhile['list_file_wortwhile']={}

    try:
        start = time()

        sys.stdout.write('\x1b[1;37m' + 'Analysing file [%d/%d]: ' % (nb_task_done.value, nb_task) + '\x1b[0m')
        sys.stdout.write('\x1b[1;34m' + file + '\x1b[0m')
        sys.stdout.write('\x1b[1;37m' + ' [' + tool + ']' + '\x1b[0m' + '\n')

        analyse_files(tool, file, logs, project_name, sarif_outputs, output_version, import_path)

        nb_task_done.value += 1

        total_execution.value += time() - start

        duration = str(timedelta(seconds=round(time() - start)))

        task_sec = nb_task_done.value / (time() - start_time)
        remaining_time = str(timedelta(seconds=round((nb_task - nb_task_done.value) / task_sec)))
        # if file not in data_info_wortwhile["list_file_wortwhile"]["list_tool"]:
        #     t = 1
        basename_file = os.path.basename(file)
        if not data_info_wortwhile["list_file_wortwhile"].get("list_file"):
            data_info_wortwhile["list_file_wortwhile"]["list_file"] = []
            data_info_wortwhile["list_file_wortwhile"]["data"] ={}
            data_info_wortwhile["list_file_wortwhile"]["data"][basename_file] =[]
            data_info_wortwhile["list_file_wortwhile"]["list_file"].append(basename_file)
            data_info_wortwhile["list_file_wortwhile"]["data"][basename_file].append(tool)
        elif basename_file not in data_info_wortwhile["list_file_wortwhile"]["list_file"]:
            data_info_wortwhile["list_file_wortwhile"]["data"][basename_file] = []
            data_info_wortwhile["list_file_wortwhile"]["list_file"].append(basename_file)
            data_info_wortwhile["list_file_wortwhile"]["data"][basename_file].append(tool)
        elif tool not in data_info_wortwhile["list_file_wortwhile"]["data"][basename_file]:
            data_info_wortwhile["list_file_wortwhile"]["data"][basename_file].append(tool)
        with open(info_wortwhile_path, "w") as info_wortwhile_file:
            json.dump(data_info_wortwhile, info_wortwhile_file)
        sys.stdout.write(
            '\x1b[1;37m' + 'Done [%d/%d, %s]: ' % (nb_task_done.value, nb_task, remaining_time) + '\x1b[0m')
        sys.stdout.write('\x1b[1;34m' + file + '\x1b[0m')
        sys.stdout.write('\x1b[1;37m' + ' [' + tool + '] in ' + duration + ' ' + '\x1b[0m' + '\n')
        logs.write('[%d/%d] ' % (nb_task_done.value, nb_task) + file + ' [' + tool + '] in ' + duration + ' \n')
    except Exception as e:
        print(e)
        raise e



def worthwhite(list_tool, list_file,project_name, import_path= 'FILE',  output_version='all', skip_existing=False, processes=1,aggregate_sarif=False,unique_sarif_output=False ):
    global logs, output_folder
    logs.write('Arguments passed: ' + str(sys.argv) + '\n')
    files_to_analyze = []

    for file in list_file:
        if os.path.basename(file).endswith('.sol'):
            files_to_analyze.append(file)
        elif os.path.isdir(file):
            if import_path == "FILE":
                import_path = file
            for root, dirs, files in os.walk(file):
                for name in files:
                    if name.endswith('.sol'):
                        # if its running on a windows machine
                        if os.name == 'nt':
                            files_to_analyze.append(os.path.join(root, name).replace('\\', '/'))
                        else:
                            files_to_analyze.append(os.path.join(root, name))
        else:
            print('%s is not a directory or a solidity file' % file)


    # Setting up analysis variables
    start_time = time()
    manager = Manager()

    nb_task_done = manager.Value('i', 0)
    total_execution = manager.Value('f', 0)
    nb_task = len(files_to_analyze) * len(list_tool)

    sarif_outputs = manager.dict()
    tasks = []
    file_names = []
    for file in files_to_analyze:
        for tool in list_tool:
            results_folder = 'data/'+ project_name + '/results/'
            if not os.path.exists(results_folder):
                os.makedirs(results_folder)

            if skip_existing:
                file_name = os.path.splitext(os.path.basename(file))[0]
                file_name_json_output = tool + '_result.json'
                folder = os.path.join(results_folder, file_name, file_name_json_output)
                if os.path.exists(folder):
                    continue

            tasks.append((tool, file,project_name, sarif_outputs, import_path, output_version, nb_task, nb_task_done,
                          total_execution, start_time))
        file_names.append(os.path.splitext(os.path.basename(file))[0])

    # initialize all sarif outputs
    for file_name in file_names:
        sarif_outputs[file_name] = SarifHolder()

    with Pool(processes=processes) as pool:
        pool.map(analyse, tasks)

    if aggregate_sarif:
        for file_name in file_names:
            sarif_file_path = '/'+ project_name + '/results/' + '/' + file_name + '.sarif'
            with open(sarif_file_path, 'w') as sarif_file:
                json.dump(sarif_outputs[file_name].print(), sarif_file, indent=2)

    if unique_sarif_output:
        sarif_holder = SarifHolder()
        for sarif_output in sarif_outputs.values():
            for run in sarif_output.sarif.runs:
                sarif_holder.addRun(run)
        sarif_file_path = 'data/'+ project_name + '/results/'+ file_name+ '.sarif'
        with open(sarif_file_path, 'w') as sarif_file:
            json.dump(sarif_holder.print(), sarif_file, indent=2)
    print("trong ddos")
    return logs
if __name__ == '__main__':
    start_time = time()
    list_tool = ['oyente', 'mythril','slither','honeybadger']
    list_file = ['dataset/reentrance.sol']
    logs = worthwhite(list_tool, list_file)
    elapsed_time = round(time() - start_time)
    if elapsed_time > 60:
        elapsed_time_sec = round(elapsed_time % 60)
        elapsed_time = round(elapsed_time // 60)
        print('Analysis completed. \nIt took %sm %ss to analyse all files.' % (elapsed_time, elapsed_time_sec))
        logs.write('Analysis completed. \nIt took %sm %ss to analyse all files.' % (elapsed_time, elapsed_time_sec))
    else:
        print('Analysis completed. \nIt took %ss to analyse all files.' % elapsed_time)
        logs.write('Analysis completed. \nIt took %ss to analyse all files.' % elapsed_time)
