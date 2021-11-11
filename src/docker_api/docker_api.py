#!/usr/bin/env python3

import docker
import json
import os
import re
import sys
import tarfile
import yaml

from solidity_parser import parser

from src.output_parser.Conkas import Conkas
from src.output_parser.HoneyBadger import HoneyBadger
from src.output_parser.Maian import Maian
from src.output_parser.Manticore import Manticore
from src.output_parser.Mythril import Mythril
from src.output_parser.Osiris import Osiris
from src.output_parser.Oyente import Oyente
from src.output_parser.Securify import Securify
from src.output_parser.Slither import Slither
from src.output_parser.Smartcheck import Smartcheck
from src.output_parser.Solhint import Solhint

from time import time


client = docker.from_env()

"""
get solidity compiler version
"""
def get_solc_version(file, logs):
    try:
        with open(file, 'r', encoding='utf-8') as fd:
            sourceUnit = parser.parse(fd.read())
            solc_version = sourceUnit['children'][0]['value']
            solc_version = solc_version.strip('^')
            solc_version = solc_version.split('.')
            return (int(solc_version[1]), int(solc_version[2]))
    except:
        print('\x1b[1;33m' + 'WARNING: could not parse solidity file to get solc version' + '\x1b[0m')
        logs.write('WARNING: could not parse solidity file to get solc version \n')
    return (None, None)


"""
pull images
"""
def pull_image(image, logs):
    try:
        print('pulling ' + image + ' image, this may take a while...')
        logs.write('pulling ' + image + ' image, this may take a while...\n')
        image = client.images.pull(image)
        print('image pulled')
        logs.write('image pulled\n')

    except docker.errors.APIError as err:
        print(err)
        logs.write(err + '\n')


"""
mount volumes
"""
def mount_volumes(dir_path, logs):
    try:
        volume_bindings = {os.path.abspath(dir_path): {'bind': '/' + dir_path, 'mode': 'rw'}}
        return volume_bindings
    except os.error as err:
        print(err)
        logs.write(err + '\n')


"""
stop container
"""
def stop_container(container, logs):
    try:
        if container is not None:
            container.stop(timeout=0)
    except (docker.errors.APIError) as err:
        print(err)
        logs.write(str(err) + '\n')


"""
remove container
"""
def remove_container(container, logs):
    try:
        if container is not None:
            container.remove()
    except (docker.errors.APIError) as err:
        print(err)
        logs.write(err + '\n')


"""
write output
"""
def parse_results(output, tool, file_name, container, cfg, logs, results_folder, start, end, sarif_outputs,
                  file_path_in_repo, output_version):
    output_folder = os.path.join(results_folder, file_name)

    results = {
        'contract': file_name,
        'tool': tool,
        'start': start,
        'end': end,
        'duration': end - start,
        'analysis': None
    }
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_name_json_output = tool + '_result.log'
    with open(os.path.join(output_folder, file_name_json_output), 'w', encoding='utf-8') as f:
        f.write(output)
    print(cfg)
    if 'output_in_files' in cfg:
        try:
            file_name_tar_output = tool + '_result.tar'
            with open(os.path.join(output_folder, file_name_tar_output), 'wb') as f:
                output_in_file = cfg['output_in_files']['folder']
                bits, stat = container.get_archive(output_in_file)
                for chunk in bits:
                    f.write(chunk)
        except Exception as e:
            print(output)
            print(e)
            print('\x1b[1;31m' + 'ERROR: could not get file from container. file not analysed.' + '\x1b[0m')
            logs.write('ERROR: could not get file from container. file not analysed.\n')

    try:
        sarif_holder = sarif_outputs[file_name]
        if tool == 'oyente':
            results['analysis'] = Oyente().parse(output)
            # Sarif Conversion
            sarif_holder.addRun(Oyente().parseSarif(results, file_path_in_repo))
        elif tool == 'honeybadger':
            results['analysis'] = HoneyBadger().parse(output)
            sarif_holder.addRun(HoneyBadger().parseSarif(results, file_path_in_repo))
        elif tool == 'mythril':
            results['analysis'] = json.loads(output)
            sarif_holder.addRun(Mythril().parseSarif(results, file_path_in_repo))
        elif tool == 'slither':
            file_name_tar_output = tool + '_result.tar'
            if os.path.exists(os.path.join(output_folder, file_name_tar_output)):
                tar = tarfile.open(os.path.join(output_folder, file_name_tar_output))
                output_file = tar.extractfile('output.json')
                results['analysis'] = json.loads(output_file.read())
                sarif_holder.addRun(Slither().parseSarif(results, file_path_in_repo))

        sarif_outputs[file_name] = sarif_holder

    except Exception as e:
        print(output)
        print(e)
        # ignore
        pass

    file_name_json_output = tool + '_result.json'
    if output_version == 'v1' or output_version == 'all':
        with open(os.path.join(output_folder, file_name_json_output), 'w') as f:
            json.dump(results, f, indent=2)
    file_name_sarif_output = tool + '_result.sarif'
    if output_version == 'v2' or output_version == 'all':
        with open(os.path.join(output_folder, file_name_sarif_output), 'w') as sarifFile:
            json.dump(sarif_outputs[file_name].printToolRun(tool=tool), sarifFile, indent=2)

    combine_results(tool, file_name, results_folder)

"""
analyse solidity files
"""
def analyse_files(tool, file, logs, project_name, sarif_outputs, output_version, import_path):
    try:
        cfg_path = os.path.abspath('config/tools/' + tool + '.yaml')
        with open(cfg_path, 'r', encoding='utf-8') as ymlfile:
            try:
                cfg = yaml.safe_load(ymlfile)
            except yaml.YAMLError as exc:
                print(exc)
                logs.write(exc)


        # create result folder with time
        results_folder = 'data/'+ project_name + '/results/'
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        # os.makedirs(os.path.dirname(results_folder), exist_ok=True)

        # check if config file as all required fields
        if 'default' not in cfg['docker_image'] or cfg['docker_image'] == None:
            logs.write(tool + ': default docker image not provided. please check you config file.\n')
            sys.exit(tool + ': default docker image not provided. please check you config file.')
        elif 'cmd' not in cfg or cfg['cmd'] == None:
            logs.write(tool + ': commands not provided. please check you config file.\n')
            sys.exit(tool + ': commands not provided. please check you config file.')

        if import_path == "FILE":
            import_path = file
            file_path_in_repo = file
        else:
            file_path_in_repo = file.replace(import_path, '')  # file path relative to project's root directory

        # bind directory path instead of file path to allow imports in the same directory
        volume_bindings = mount_volumes(os.path.dirname(import_path), logs)

        file_name = os.path.basename(file)
        file_name = os.path.splitext(file_name)[0]
        start = time()

        (solc_version, solc_version_minor) = get_solc_version(file, logs)

        if isinstance(solc_version, int) and solc_version < 5 and 'solc<5' in cfg['docker_image']:
            image = cfg['docker_image']['solc<5']
        # if there's no version or version >5, choose default
        else:
            image = cfg['docker_image']['default']

        if not client.images.list(image):
            pull_image(image, logs)

        cmd = cfg['cmd']
        if '{contract}' in cmd:
            cmd = cmd.replace('{contract}', '/' + file)
        else:
            cmd += ' /' + file
        container = None
        print("cmd")
        print(cmd)
        try:
            container = client.containers.run(image,
                                              cmd,
                                              detach=True,
                                              # cpu_quota=150000,
                                              volumes=volume_bindings)
            # print("container")
            # print(container)
            container = client.containers.run(image,
                                              cmd,
                                              detach=True,
                                              # cpu_quota=150000,
                                              volumes=volume_bindings)
            try:
                container.wait(timeout=(30 * 60))
            except Exception as e:
                pass
            output = container.logs().decode('utf8').strip()
            if (output.count('Solc experienced a fatal error') >= 1 or output.count('compilation failed') >= 1):
                print(
                    '\x1b[1;31m' + 'ERROR: Solc experienced a fatal error. Check the results file for more info' + '\x1b[0m')
                logs.write('ERROR: Solc experienced a fatal error. Check the results file for more info\n')

            end = time()

            parse_results(output, tool, file_name, container, cfg, logs, results_folder, start, end, sarif_outputs,
                          file_path_in_repo, output_version)

        finally:
            # print("thaovt in logs")
            # print(logs)
            stop_container(container, logs)
            remove_container(container, logs)

    except (docker.errors.APIError) as err:
        print(err)
        logs.write(err + '\n')

def combine_results(tool,file_name,results_folder):
    # create file combine_results
    combine_results_path = results_folder + file_name + '/combine_results.json'

    output_folder = os.path.join(results_folder, file_name)
    file_name_sarif_output = tool + '_result.sarif'
    with open(os.path.join(output_folder, file_name_sarif_output), 'r') as sarifFile:
        sarif_data = json.load(sarifFile)
    print(sarif_data['runs'])
    if (sarif_data['runs']):
        if os.path.exists(combine_results_path):
            print("đã có file")
            with open(combine_results_path, 'r') as combine_results_file:
                data_combine_result = json.load(combine_results_file)
            rules = sarif_data["runs"][0]["tool"]["driver"]["rules"]
            for rule in rules:
                if rule not in data_combine_result["rules"]:
                    data_combine_result["rules"].append(rule)
            results = sarif_data["runs"][0]["results"]
            list_line_erro = data_combine_result["listLine"]
            print(list_line_erro)
            print("đây là lần đầu")
            for result in results:
                message = result["message"]["text"]
                ruleId = result["ruleId"]
                level = result["level"]
                # print("thaovt for result")

                for location in result["locations"]:
                    # print("thaovt for location")
                    line_erro = str(location["physicalLocation"]["region"]["startLine"])
                    snippet = location["physicalLocation"]["region"].get("snippet")
                    list_erro_in_line = data_combine_result["analysis"].get(line_erro)
                    if list_erro_in_line is None:
                        data_combine_result["analysis"][line_erro] = []
                        erro_in_line = {}
                        erro_in_line["level"]=level
                        erro_in_line["tool"] = [tool]
                        if snippet is not None:
                            erro_in_line["snippet"] = snippet
                        for rule in rules:
                            if rule["id"] == ruleId:
                                erro_in_line["fullDescription"] = rule["fullDescription"]["text"]
                                erro_in_line["name"] = rule["name"]
                        data_combine_result["analysis"][line_erro].append(erro_in_line)
                        data_combine_result["listLine"].append(int(line_erro))

                    else :
                        name_erro = ''
                        for rule in rules:
                            if rule["id"] == ruleId:
                                name_erro = rule["name"]
                        count = 0
                        for erro_line in list_erro_in_line:
                            if name_erro == erro_line["name"]:
                                print("dong nay da co loi nay")
                                count = count +1
                                if tool not in erro_line["tool"]:
                                    erro_line["tool"].append(tool)
                        if count == 0:
                            erro_in_line = {}
                            erro_in_line["level"] = level
                            erro_in_line["tool"] = [tool]
                            for rule in rules:
                                if rule["shortDescription"]["text"] == message:
                                    erro_in_line["fullDescription"] = rule["fullDescription"]["text"]
                                    erro_in_line["name"] = rule["name"]
                            data_combine_result["analysis"][line_erro].append(erro_in_line)
        else:
            data_combine_result = {}
            rules = sarif_data["runs"][0]["tool"]["driver"]["rules"]
            data_combine_result["contract"] = file_name
            data_combine_result["sourceLanguage"] = sarif_data["runs"][0]["artifacts"][0]["sourceLanguage"]
            results = sarif_data["runs"][0]["results"]
            data_combine_result["analysis"] = {}
            data_combine_result["listLine"] = []
            data_combine_result["rules"]=rules
            list_line_erro = []
            for result in results:
                message = result["message"]["text"]
                level = result["level"]
                for location in result["locations"]:
                    snippet = location["physicalLocation"]["region"].get("snippet")
                    line_erro = location["physicalLocation"]["region"]["startLine"]
                    list_erro_in_line = data_combine_result["analysis"].get(line_erro)
                    print(type(data_combine_result["analysis"]))
                    print(type(line_erro))
                    if list_erro_in_line is None:
                        list_line_erro.append(line_erro)
                        data_combine_result["analysis"][line_erro] = []
                        erro_in_line = {}
                        erro_in_line["level"]=level
                        erro_in_line["tool"] = [tool]
                        if snippet is not None:
                            erro_in_line["snippet"] = snippet
                        for rule in rules:
                            if rule["shortDescription"]["text"] == message:
                                erro_in_line["fullDescription"] = rule["fullDescription"]["text"]
                                erro_in_line["name"] = rule["name"]
                        data_combine_result["analysis"][line_erro].append(erro_in_line)
                        data_combine_result["listLine"].append(line_erro)
                    else :
                        name_erro = ''
                        for rule in rules:
                            if rule["shortDescription"]["text"] == message:
                                name_erro = rule["name"]
                        count = 0
                        for erro_line in list_erro_in_line:
                            if name_erro == erro_line["name"]:
                                count = count +1
                                if tool not in erro_line["tool"]:
                                    erro_line["tool"].append(tool)
                        if count == 0:
                            print("chưa có lỗi nãy")
                            erro_in_line = {}
                            erro_in_line["level"] = level
                            erro_in_line["tool"] = [tool]
                            for rule in rules:
                                if rule["shortDescription"]["text"] == message:
                                    erro_in_line["fullDescription"] = rule["fullDescription"]["text"]
                                    erro_in_line["name"] = rule["name"]
                            data_combine_result["analysis"][line_erro].append(erro_in_line)
                            print('tạo lần sauu')
                            print(data_combine_result["analysis"])
        print(data_combine_result)
        with open(combine_results_path, 'w') as f:
            json.dump(data_combine_result, f)
