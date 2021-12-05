import json
import os

from src.interface.highConfidenceOfTool import List_Hight_Confidence_Vulnerabilities

Default_Count_Leve_Vulnerabilities ={ "warning" : 0,"error":0,"note":0,"none":0}
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

def final_results(file_name,results_folder):
    combine_results_path = results_folder + file_name + '/combine_results.json'
    final_results_path = results_folder + file_name + '/final_results.json'
    with open(combine_results_path, 'r') as combine_results_file:
        data_combine_result = json.load(combine_results_file)
    data_final_results = {}
    data_final_results["contract"] = data_combine_result["contract"]
    data_final_results["sourceLanguage"] = data_combine_result["sourceLanguage"]
    list_vulnerabilities = []
    count_vulnerabilities = {}
    count_leve_vulnerabilities = Default_Count_Leve_Vulnerabilities
    num_risk = 0
    list_line = data_combine_result["listLine"]
    for line in list_line:
        line = str(line)
        list_vulnerabilities_in_line = data_combine_result["analysis"][line]
        count_vulnerabilities_in_line = len(list_vulnerabilities_in_line)
        for vulnerabilitie_in_line in list_vulnerabilities_in_line:
            if "honeybadger" in vulnerabilitie_in_line["tool"]:
                if count_vulnerabilities_in_line == 1:
                    list_line.remove(line)
                list_vulnerabilities_in_line.remove(vulnerabilitie_in_line)
            elif len(vulnerabilitie_in_line["tool"]) > 1:
                count_leve_vulnerabilities[vulnerabilitie_in_line["level"]] = count_leve_vulnerabilities[
                                                                                  vulnerabilitie_in_line[
                                                                                      "level"]] + 1
                if vulnerabilitie_in_line["name"] not in list_vulnerabilities:
                    list_vulnerabilities.append(vulnerabilitie_in_line["name"])
                    count_vulnerabilities[vulnerabilitie_in_line["name"]] = int(1)
                else:
                    count_vulnerabilities[vulnerabilitie_in_line["name"]] = count_vulnerabilities[vulnerabilitie_in_line["name"]] + 1
            else:
                # print(vulnerabilitie_in_line["tool"][0])
                # print(List_Hight_Confidence_Vulnerabilities[''])
                list_hight_confidence_vulnerabilities = List_Hight_Confidence_Vulnerabilities[vulnerabilitie_in_line["tool"][0]]
                if vulnerabilitie_in_line["name"] not in list_hight_confidence_vulnerabilities:
                    vulnerabilitie_in_line["flag"] = "risk of false positives"
                    num_risk = num_risk +1
                count_leve_vulnerabilities[vulnerabilitie_in_line["level"]] = count_leve_vulnerabilities[
                                                                                  vulnerabilitie_in_line[
                                                                                      "level"]] + 1
                if vulnerabilitie_in_line["name"] not in list_vulnerabilities:
                    list_vulnerabilities.append(vulnerabilitie_in_line["name"])
                    count_vulnerabilities[vulnerabilitie_in_line["name"]] = int(1)

                else:
                    count_vulnerabilities[vulnerabilitie_in_line["name"]] = count_vulnerabilities[
                                                                                vulnerabilitie_in_line["name"]] + 1
        data_combine_result["analysis"][line] = list_vulnerabilities_in_line
    data_combine_result["listLine"] = list_line
    data_final_results["count_risk_of_false_positives"] = num_risk
    data_final_results["list_vulnerabilities"] = list_vulnerabilities
    data_final_results["rules"] = data_combine_result["rules"]
    data_final_results["listLine"] = data_combine_result["listLine"]
    data_final_results["analysis"] = data_combine_result["analysis"]
    data_final_results["count_vulnerabilities"] = count_vulnerabilities
    data_final_results["count_leve_vulnerabilities"] = count_leve_vulnerabilities
    with open(final_results_path, 'w') as f:
        json.dump(data_final_results, f)

    print(Default_Count_Leve_Vulnerabilities)
    return data_final_results

def add_two_leve_list(list1, list2):
    Count_Leve_Vulnerabilities= {}

    Count_Leve_Vulnerabilities["warning"] = list1["warning"] + list2["warning"]
    Count_Leve_Vulnerabilities["error"] = list1["error"] + list2["error"]
    Count_Leve_Vulnerabilities["note"] = list1["note"] + list2["note"]
    Count_Leve_Vulnerabilities["none"] = list1["none"] + list2["none"]
    print(list1)
    print(list2)
    print(Count_Leve_Vulnerabilities)
    return Count_Leve_Vulnerabilities