import glob
import json
import shutil

import git
import requests
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from requests import Session
from werkzeug.utils import secure_filename
import os

from smartBugs import worthwhite
from worthwhite import result_statistics_tool

UPLOAD_FOLDER = 'data/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','sol'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
sess = Session()

@app.route("/")
def hello():
    return render_template('index.html', title='Docker Python', name='Thaovt1111')

@app.route("/wortwhile",methods=['Get'])
def wortwhile_smart_contract():
    data_req = request.get_data()
    data = json.loads(data_req.decode("utf-8"))
    list_tool =data["list_tool"]
    list_file_info = data["file_info"]
    list_file = list_file_info["list_path"]
    project_name = list_file_info["project_name"]
    # print(list_tool)
    # print(list_file)
    worthwhite(list_tool, list_file,project_name)
    return "logs"



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
def upload_file():
    file_info = {}
    file_info["list_path"] = []
    file_info["list_name"] = []
    count = 0
    data_req = request.get_data()
    print(data_req)
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
            project_name =url_split[ len(url_split) -1]
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
    return file_info

@app.route('/statistics', methods=['GET', 'POST'])
def result_statistics():
    data_req = request.get_data()
    data = json.loads(data_req.decode("utf-8"))
    list_tool = data["list_tool"]
    list_file_info = data["file_info"]
    list_file = list_file_info["list_path"]
    project_name = list_file_info["project_name"]
    result_statistics_tool(list_tool,list_file,project_name)
    return True

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ['8888'], debug=True)

