#
# import json
# import os
# import sys
#
#
#
# from multiprocessing import Manager, Pool
#
#
# from smartBugs import analyse
# from src.docker_api.docker_api import analyse_files
# from src.interface.cli import create_parser, getRemoteDataset, isRemoteDataset, DATASET_CHOICES, TOOLS_CHOICES
# from src.output_parser.SarifHolder import SarifHolder
# from time import time, localtime, strftime
#
#
# cfg_dataset_path = os.path.abspath('config/dataset/dataset.yaml')
# def worthwhite(list_tool, list_file, import_path= 'FILE',  output_version='all', skip_existing=False, processes=1,aggregate_sarif=False,unique_sarif_output=False ):
#     global logs, output_folder
#     logs.write('Arguments passed: ' + str(sys.argv) + '\n')
#     print("thaovt")
#
#     files_to_analyze = []
#
#     # if args.dataset:
#     #     if args.dataset == ['all']:
#     #         DATASET_CHOICES.remove('all')
#     #         args.dataset = DATASET_CHOICES
#     #     for dataset in args.dataset:
#     #         # Directory search is recursive (see below), so
#     #         # if a remote D is used, we don't need to specify
#     #         # the subsets of D
#     #         base_name = dataset.split('/')[0]
#     #         if isRemoteDataset(cfg_dataset, base_name):
#     #             remote_info = getRemoteDataset(cfg_dataset, base_name)
#     #             base_path = remote_info['local_dir']
#     #
#     #             if not os.path.isdir(base_path):
#     #                 # local copy does not exist; we need to clone it
#     #                 print(
#     #                     '\x1b[1;37m' + "%s is a remote dataset. Do you want to create a local copy? [Y/n] " % base_name + '\x1b[0m')
#     #                 answer = input()
#     #                 if answer.lower() in ['yes', 'y', '']:
#     #                     sys.stdout.write('\x1b[1;37m' + 'Cloning remote dataset [%s <- %s]... ' % (
#     #                         base_path, remote_info['url']) + '\x1b[0m')
#     #                     sys.stdout.flush()
#     #                     git.Repo.clone_from(remote_info['url'], base_path)
#     #                     sys.stdout.write('\x1b[1;37m\n' + 'Done.' + '\x1b[0m\n')
#     #                 else:
#     #                     print(
#     #                         '\x1b[1;33m' + 'ABORTING: cannot proceed without local copy of remote dataset %s' % base_name + '\x1b[0m')
#     #                     quit()
#     #             else:
#     #                 sys.stdout.write('\x1b[1;37m' + 'Using remote dataset [%s <- %s] ' % (
#     #                     base_path, remote_info['url']) + '\x1b[0m\n')
#     #
#     #             if dataset == base_name:  # basename included
#     #                 dataset_path = base_path
#     #                 args.file.append(dataset_path)
#     #             if dataset != base_name and base_name not in args.dataset:
#     #                 sbset_name = dataset.split('/')[1]
#     #                 dataset_path = os.path.join(base_path, remote_info['subsets'][sbset_name])
#     #                 args.file.append(dataset_path)
#     #         else:
#     #             dataset_path = cfg_dataset[dataset]
#     #             args.file.append(dataset_path)
#
#     for file in list_file:
#         # analyse files
#         if os.path.basename(file).endswith('.sol'):
#             files_to_analyze.append(file)
#         # analyse dirs recursively
#         elif os.path.isdir(file):
#             if import_path == "FILE":
#                 import_path = file
#             for root, dirs, files in os.walk(file):
#                 for name in files:
#                     if name.endswith('.sol'):
#                         # if its running on a windows machine
#                         if os.name == 'nt':
#                             files_to_analyze.append(os.path.join(root, name).replace('\\', '/'))
#                         else:
#                             files_to_analyze.append(os.path.join(root, name))
#         else:
#             print('%s is not a directory or a solidity file' % file)
#
#     if list_tool== ['all']:
#         TOOLS_CHOICES.remove('all')
#         list_tool = TOOLS_CHOICES
#
#     # Setting up analysis variables
#     start_time = time()
#     manager = Manager()
#
#     nb_task_done = manager.Value('i', 0)
#     total_execution = manager.Value('f', 0)
#     nb_task = len(files_to_analyze) * len(list_tool)
#
#     sarif_outputs = manager.dict()
#     tasks = []
#     file_names = []
#     for file in files_to_analyze:
#         for tool in list_tool:
#             results_folder ='data'+ project_name + 'results/' + tool + '/' + output_folder
#             if not os.path.exists(results_folder):
#                 os.makedirs(results_folder)
#
#             if skip_existing:
#                 file_name = os.path.splitext(os.path.basename(file))[0]
#                 file_name_json_output = tool + '_result.json'
#                 folder = os.path.join(results_folder, file_name, file_name_json_output)
#                 if os.path.exists(folder):
#                     continue
#
#             tasks.append((tool, file, sarif_outputs, import_path, output_version, nb_task, nb_task_done,
#                           total_execution, start_time))
#         file_names.append(os.path.splitext(os.path.basename(file))[0])
#
#     # initialize all sarif outputs
#     for file_name in file_names:
#         sarif_outputs[file_name] = SarifHolder()
#
#     print(tasks)
#     with Pool(processes=processes) as pool:
#         pool.map(analyse, tasks)
#
#     if aggregate_sarif:
#         for file_name in file_names:
#             sarif_file_path = 'data'+ project_name + 'results/' + output_folder + '/' + file_name + '.sarif'
#             with open(sarif_file_path, 'w') as sarif_file:
#                 # json.dump(sarif_outputs[file_name].print(), sarif_file, indent=2)
#                 json.dump(sarif_file, indent=2)
#     if unique_sarif_output:
#         sarif_holder = SarifHolder()
#         for sarif_output in sarif_outputs.values():
#             for run in sarif_output.sarif.runs:
#                 sarif_holder.addRun(run)
#         sarif_file_path = 'data'+ project_name + 'results/' + output_folder + '.sarif'
#         with open(sarif_file_path, 'w') as sarif_file:
#             # json.dump(sarif_holder.print(), sarif_file, indent=2)
#             json.dump( sarif_file, indent=2)
#
#
#     return logs
import glob
import json
import os

# from app import app


def result_statistics_tool(project_name,folder_data):
    info_wortwhile_path = os.path.join(folder_data,"info_wortwhile.json")
    with open(info_wortwhile_path, 'r') as file:
        info_wortwhile_data = json.load(file)
    info_wortwhile = info_wortwhile_data.get("list_file_wortwhile")
    print(info_wortwhile)
    list_tool =[]
    list_file = []
    if info_wortwhile is not None:
        list_file = info_wortwhile.get("list_file")
        list_tool = []
        for file in list_file:
            list_tool = info_wortwhile["data"].get(file)
            file_name = str(file).split(".")[0]
            combine_results_path = os.path.join(folder_data,"results/",file_name,"/combine_results.json")
            with open(combine_results_path, 'r') as combine_results_file:
                combine_results_data = json.load(combine_results_file)

    # for file in list_file:
    #     if True:
    #         return False
    # return True