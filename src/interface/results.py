import json
import os


def combine_results(tool,file_name,results_folder):
    # create file combine_results
    combine_results_path = results_folder + file_name + '/combine_results.json'
    output_folder = os.path.join(results_folder, file_name)
    file_name_sarif_output = tool + '_result.sarif'
    with open(os.path.join(output_folder, file_name_sarif_output), 'r') as sarifFile:
        sarif_data = json.load(sarifFile)
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
            # list_line_erro = data_combine_result["listLine"]
            for result in results:
                message = result["message"]["text"]
                ruleId = result["ruleId"]
                level = result["level"]
                for location in result["locations"]:
                    line_erro = str(location["physicalLocation"]["region"]["startLine"])
                    snippet = location["physicalLocation"]["region"].get("snippet")
                    list_erro_in_line = data_combine_result["analysis"].get(line_erro)
                    if list_erro_in_line is None:
                        data_combine_result["analysis"][line_erro] = []
                        erro_in_line = {}
                        erro_in_line["level"] = level
                        erro_in_line["tool"] = [tool]
                        if snippet is not None:
                            erro_in_line["snippet"] = snippet
                        for rule in rules:
                            if rule["id"] == ruleId:
                                erro_in_line["fullDescription"] = rule["fullDescription"]["text"]
                                print(rule)
                                erro_in_line["name"] = rule["name"]
                        data_combine_result["analysis"][line_erro].append(erro_in_line)
                        data_combine_result["listLine"].append(int(line_erro))

                    else:
                        name_erro = ''
                        for rule in rules:
                            if rule["id"] == ruleId:
                                name_erro = rule["name"]
                        count = 0
                        for erro_line in list_erro_in_line:
                            if name_erro == erro_line["name"]:
                                print("dong nay da co loi nay")
                                count = count + 1
                                if tool not in erro_line["tool"]:
                                    erro_line["tool"].append(tool)
                        if count == 0:
                            erro_in_line = {}
                            erro_in_line["level"] = level
                            erro_in_line["tool"] = [tool]
                            for rule in rules:
                                if rule["id"] == ruleId:
                                    print(rule)
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
            data_combine_result["rules"] = rules
            list_line_erro = []
            for result in results:
                ruleId = result["ruleId"]
                message = result["message"]["text"]
                level = result["level"]
                for location in result["locations"]:
                    snippet = location["physicalLocation"]["region"].get("snippet")
                    line_erro = location["physicalLocation"]["region"]["startLine"]
                    list_erro_in_line = data_combine_result["analysis"].get(line_erro)
                    if list_erro_in_line is None:
                        list_line_erro.append(line_erro)
                        data_combine_result["analysis"][line_erro] = []
                        erro_in_line = {}
                        erro_in_line["level"] = level
                        erro_in_line["tool"] = [tool]
                        if snippet is not None:
                            erro_in_line["snippet"] = snippet
                        for rule in rules:
                            if rule["id"] == ruleId:
                                erro_in_line["fullDescription"] = rule["fullDescription"]["text"]
                                erro_in_line["name"] = rule["name"]
                        data_combine_result["analysis"][line_erro].append(erro_in_line)
                        data_combine_result["listLine"].append(line_erro)
                    else:
                        name_erro = ''
                        for rule in rules:
                            if rule["shortDescription"]["text"] == message:
                                name_erro = rule["name"]
                        count = 0
                        for erro_line in list_erro_in_line:
                            if name_erro == erro_line["name"]:
                                count = count + 1
                                if tool not in erro_line["tool"]:
                                    erro_line["tool"].append(tool)
                        if count == 0:
                            print("chưa có lỗi nãy")
                            erro_in_line = {}
                            erro_in_line["level"] = level
                            erro_in_line["tool"] = [tool]
                            for rule in rules:
                                if rule["id"] == ruleId:
                                    erro_in_line["fullDescription"] = rule["fullDescription"]["text"]
                                    erro_in_line["name"] = rule["name"]
                            data_combine_result["analysis"][line_erro].append(erro_in_line)
        with open(combine_results_path, 'w') as f:
            json.dump(data_combine_result, f)

