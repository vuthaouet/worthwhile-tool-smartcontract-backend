import glob
import json
import shutil
import time

import git
import requests
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify, Response, send_file
from requests import Session
from werkzeug.utils import secure_filename
import os

from analyse import worthwhite
from src.interface.results import combine_results, final_results, add_two_leve_list
from worthwhite import result_statistics_tool
from flask_cors import CORS, cross_origin
Default_Count_Leve_Vulnerabilities ={ "warning" : 0,"error":0,"note":0,"none":0}
UPLOAD_FOLDER = 'data/'
ALLOWED_EXTENSIONS = {'sol'}

app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
sess = Session()

@app.route("/")
def hello():
    return render_template('index.html', title='Docker Python', name='Thaovt1111')

@app.route('/time')
@cross_origin(supports_credentials=True)
def get_current_time():
    return {'time': time.time()}
@app.route("/wortwhile",methods=['POST'])
@cross_origin(supports_credentials=True)
def wortwhile_smart_contract():
    print("thaovt")
    print(request)
    print(request.data)
    data_req = request.get_data()
    print(data_req)
    data = json.loads(data_req.decode("utf-8"))["data"]
    print(data_req)
    list_tool = data["list_tool"]
    list_file_info = data["file_info"]
    list_file = list_file_info["list_path"]
    project_name = list_file_info["project_name"]
    worthwhite(list_tool, list_file,project_name)
    return data
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def exists_or_create_dir(project_name):
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    # check if the post request has the file part
    folder = os.path.join(app.config['UPLOAD_FOLDER'], project_name, 'source_code')
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        filelist = glob.glob(os.path.join(folder, "*.sol"))
        for f in filelist:
            os.remove(f)
    return folder
def parse_result_file_info(file_info,filename,filepath):
    file_info["list_name"].append(filename)
    file_info["list_path"].append(filepath)
@app.route('/wortwhile/uploadfile', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def upload_file():
    output = {}
    file_info = {}
    file_info["list_path"] = []
    file_info["list_name"] = []
    output["list_tool"] = []
    list_tool = request.form['list_tool'].split(",")
    print(list_tool)
    print("thaovt list_tool test")
    for tool in list_tool:
        output["list_tool"].append(tool)
    # output["list_tool"] = request.form['list_tool']
    count = 0
    # data_req = request.get_data()
    print("thaovt data")
    # print(data_req)
    print("thaovt form")
    print(request.form)
    # print(request.json)
    # data = request.json
    if request.method == 'POST':
        if(request.form['type'].lower() == 'file'):
            print("thaovt file")
            project_name = request.form.get('project_name')
            file_info["project_name"] = project_name
            folder = exists_or_create_dir(project_name)
            print(request.files)
            if 'file' not in request.files:
                print("No file part")
                flash('No file part')
                return redirect(request.url)
            files = request.files.getlist("file")
            for file in files:
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if file.filename == '':
                    flash('No selected file')
                    # return redirect(request.url)
                if file and allowed_file(file.filename):
                    count = count + 1
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(folder, filename)
                    file.save(os.path.join(file_path))
                    parse_result_file_info(file_info,filename,file_path)
                # return file_path
        elif (request.form['type'].lower() == 'repo'):
            print("thaovt repo")
            url_repo = request.form.get('url')
            url_split = url_repo.split('/')
            project_name =request.form.get('project_name')
            file_info["project_name"] = project_name
            folder = os.path.join(app.config['UPLOAD_FOLDER'], project_name, 'source_code')
            if os.path.exists(folder):
                shutil.rmtree(folder)
            folder_git = os.path.join(app.config['UPLOAD_FOLDER'], project_name,'folder_git')
            if os.path.exists(folder_git) and os.listdir(folder_git) :
                shutil.rmtree(folder_git)
                os.makedirs(folder_git)
            git.Repo.clone_from(url_repo, folder_git)
            filelist = os.path.join(folder_git,'contracts')
            shutil.copytree(filelist, folder)
            filelist = glob.glob(os.path.join(filelist,'*.sol'))
            for file in filelist:
                count = count + 1
                file_split = file.split('/')
                filename = file_split[len(file_split) - 1]
                print(file_split)
                print(filename)
                file_path= folder + '/' +filename
                print(file_path)
                parse_result_file_info(file_info, filename, file_path)
                # shutil.copy(file,folder)
            print(folder)
        file_info["count"] = count
    output["file_info"]= file_info
    return output

@app.route('/statistics', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def result_statistics():
    data_req = request.get_data()
    data = json.loads(data_req.decode("utf-8"))
    project_name = data["project_name"]
    folder_data = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
    result_statistics_tool(project_name,folder_data)
    return True
@app.route('/combine_results', methods=['POST'])
@cross_origin(supports_credentials=True)
def combine_results_api():
    data_req = request.get_data()
    project_name = json.loads(data_req.decode("utf-8"))["data"]
    # print(info_wortwhile)
    data_static = {}
    data_static["count_risk_of_false_positives"] = 0
    data_static["count_leve_vulnerabilities"]= { "warning" : 0,"error":0,"note":0,"none":0}
    data_static["list_vulnerabilities"] = []
    data_static["count_vulnerabilities"] = {}
    data_static["list_contract"] =[]
    data_static["project_name"] = project_name
    folder_results = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
    info_wortwhile_path = os.path.join(folder_results, "info_wortwhile.json")
    with open(info_wortwhile_path, 'r') as file:
        info_wortwhile_data = json.load(file)
    info_wortwhile = info_wortwhile_data.get("list_file_wortwhile")
    if info_wortwhile is not None:
        list_file = info_wortwhile["list_file"]
        data_file_tool = info_wortwhile["data"]
        for file in list_file:
            results_folder = os.path.join(app.config['UPLOAD_FOLDER'], project_name,"results/")
            tool_of_file = data_file_tool[file]
            file_name = os.path.splitext(file)[0]
            for tool in tool_of_file:
                combine_results(tool, file_name, results_folder)
            data_final_results = final_results(file_name, results_folder,project_name)
            print(data_final_results)
            print("thaovt")
            print(data_static)
            data_static["count_risk_of_false_positives"] = data_static["count_risk_of_false_positives"] + data_final_results["count_risk_of_false_positives"]
            print(data_static["count_leve_vulnerabilities"])
            print(data_final_results["count_leve_vulnerabilities"])
            data_static["count_leve_vulnerabilities"] = add_two_leve_list(data_static["count_leve_vulnerabilities"], data_final_results["count_leve_vulnerabilities"] )
            for vulnerabilities in data_final_results["list_vulnerabilities"]:
                if vulnerabilities in data_static["list_vulnerabilities"]:
                    data_static["count_vulnerabilities"][vulnerabilities] = data_static["count_vulnerabilities"][vulnerabilities] + data_final_results["count_vulnerabilities"][vulnerabilities]
                else :
                    data_static["list_vulnerabilities"].append(vulnerabilities)
                    data_static["count_vulnerabilities"][vulnerabilities] = data_final_results["count_vulnerabilities"][vulnerabilities]
            data_static["sourceLanguage"] = data_final_results["sourceLanguage"]
            data_static["list_contract"].append(file)

    return data_static
@app.route('/dowloadFile', methods=['POST','GET'])
@cross_origin(supports_credentials=True)
def sendFile():
    # data_req = request.get_data()
    # project_name = json.loads(data_req.decode("utf-8"))["data"]
    project_name = request.args.get("project_name")
    folder_results = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
    final_results_path = folder_results + '/synthesis_results.json'
    # with open(final_results_path, 'r') as final_results_file:
    #     final_results_result = json.load(final_results_file)
    # print(final_results_result)
    # return Response(final_results_result,
    #         mimetype='application/json',
    #         headers={'Content-disposition': 'attachment; filename=synthesis_results.json'})
    return send_file(final_results_path,
                     mimetype='text/json',
                     attachment_filename='synthesis_results.json',
                     as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ['8888'], debug=True)

