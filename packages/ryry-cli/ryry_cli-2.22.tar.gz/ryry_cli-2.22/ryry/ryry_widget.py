import os
import json
import sys
import shutil
import zipfile
import pkg_resources
import threading
import time
import requests
import random
import subprocess
import platform
import re
from pkg_resources import get_distribution
import socket

from pathlib import Path
from ryry import store
from ryry import ryry_webapi
from ryry import upload
from ryry import taskUtils
from ryry import utils

def compare_versions(version1, version2):
    if len(version1) <= 0:
        version1 = "0"
    if len(version2) <= 0:
        version2 = "0"
    v1 = list(map(int, version1.split('.')))
    v2 = list(map(int, version2.split('.')))
    while len(v1) < len(v2):
        v1.append(0)
    while len(v2) < len(v1):
        v2.append(0)
    for i in range(len(v1)):
        if v1[i] < v2[i]:
            return -1
        elif v1[i] > v2[i]:
            return 1
    return 0

def _remote_package_version(py_package):
    remote_version = ""
    for pip in ["pip3","pip"]:
        result = subprocess.run(f"pip index versions {py_package} -i https://pypi.python.org/simple/", 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        ss = result.stdout.decode(encoding="utf8", errors="ignore").split("\n")
        for s in ss:
            if "LATEST:" in s.strip():
                remote_version = s.replace("LATEST:", "").strip()
                break
        else:
            continue
        break
    return remote_version

#real time version get
def _local_package_version(py_package):
    find_str = "grep"
    if platform.system() == 'Windows':
        find_str = "findstr"
    local_version = ""
    for pip in ["pip3","pip"]:
        result = subprocess.run(f"{pip} list | {find_str} {py_package}", 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        ss = result.stdout.decode(encoding="utf8", errors="ignore").split("\n")
        for s in ss:
            s = re.sub(r'\s+', ' ', s)
            sl = s.strip().split(" ")
            if len(sl) == 2:
                if py_package.strip() == sl[0].strip():
                    local_version = sl[1].strip()
                    break
        else:
            continue
        break
    return local_version

def _pypi_folder_name(name):
    import re
    return re.sub(r"[/,\-\s]", "", name)

def GetWidgetConfig(path):
    #search h5 folder first, netxt search this folder
    if os.path.exists(path):
        for filename in os.listdir(path):
            pathname = os.path.join(path, filename) 
            if (os.path.isfile(pathname)) and filename in ["config.json", "config.json.py"]:
                with open(pathname, 'r', encoding='UTF-8') as f:
                    return json.load(f)
    for filename in os.listdir(path):
        pathname = os.path.join(path, filename) 
        if (os.path.isfile(pathname)) and filename in ["config.json", "config.json.py"]:
            with open(pathname, 'r', encoding='UTF-8') as f:
                return json.load(f)
    return {}

def PathIsEmpty(path):
    return len(os.listdir(path)) == 0

def replaceIfNeed(dstDir, name, subfix):
    newsubfix = subfix + ".py"
    if name.find(newsubfix) != -1:
        os.rename(os.path.join(dstDir, name), os.path.join(dstDir, name.replace(newsubfix, subfix)))

def copyWidgetTemplate(root, name):
    templateDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)#sys.prefix
    dstDir = root
    for item in os.listdir(templateDir):
        source = os.path.join(templateDir, item)
        destination = os.path.join(dstDir, item)
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    shutil.rmtree(os.path.join(dstDir, "__pycache__"))
    os.remove(os.path.join(dstDir, "__init__.py"))
    for filename in os.listdir(dstDir):
        replaceIfNeed(dstDir, filename, ".json")
        replaceIfNeed(dstDir, filename, ".js")
        replaceIfNeed(dstDir, filename, ".png")
        replaceIfNeed(dstDir, filename, ".html")

def setWidgetData(root, widgetid):
    data = GetWidgetConfig(root)
    data["widget_id"] = widgetid
    data["name"] = "Demo"
    data["version"] = "1.0"
    data["device_keys"] = [
        utils.generate_unique_id()
    ]
    data["cmd"] = os.path.join(root, "main.py")
    with open(os.path.join(root, "config.json"), 'w') as f:
        json.dump(data, f)

def createWidget(root):
    if PathIsEmpty(root) == False:
        print("current folder is not empty, create widget fail!")
        return
        
    widgetid = ryry_webapi.CreateWidgetUUID()
    if len(widgetid) == 0:
        print("create widget fail! ryry server is not avalid")
        return
    
    copyWidgetTemplate(root, "script_template")
    setWidgetData(root, widgetid)
    addWidgetToEnv(root, True)
    print("create widget success")

def CheckWidgetDataInPath(path):
    data = GetWidgetConfig(path)
    if "widget_id" not in data:
        print("folder is not widget")
        return False

    if "widget_id" in data:
        widget_id = data["widget_id"]
        if len(widget_id) == 0:
            print("widget_id is empty!")
            return False
        
    return True

def addWidgetToEnv(root, mute=False):
    #maybe pip package
    try:
        package = pkg_resources.get_distribution(root)
        local_version = package.version
        name = package.project_name
        version = package.version
        root = os.path.join(package.location, name.replace("-", "_"))
    except:
        pass

    if CheckWidgetDataInPath(root) == False:
        return
    data = GetWidgetConfig(root)
    widget_id = data["widget_id"]
    mainPythonPath = os.path.join(root, "main.py")
    store.insertWidget(widget_id, mainPythonPath)
    if mute == False:
        print(f"add {widget_id.ljust(len(widget_id)+4)} {mainPythonPath}")

def remove(args):
    widget_id = args
    if os.path.exists(args):
        #find widgetid in args path
        data = GetWidgetConfig(args)
        if "widget_id" not in data:
            print(f"path {args} is not widget folder!")
            return
        widget_id = data["widget_id"]
    # if ryry_webapi.DeleteWidget(widget_id):
    store.removeWidget(widget_id)
    print(f"widget:{widget_id} is removed with local")
        
def enable(args):
    widget_id = args
    if os.path.exists(args):
        #find widgetid in args path
        data = GetWidgetConfig(args)
        if "widget_id" not in data:
            print(f"path {args} is not widget folder!")
            return
        widget_id = data["widget_id"]
    store.enableWidget(widget_id)
    print(f"widget:{widget_id} updated")
        
def disable(args):
    widget_id = args
    if os.path.exists(args):
        #find widgetid in args path
        data = GetWidgetConfig(args)
        if "widget_id" not in data:
            print(f"path {args} is not widget folder!")
            return
        widget_id = data["widget_id"]
    store.disableWidget(widget_id)
    print(f"widget:{widget_id} updated")

def publishWidget(package_folder):
    if CheckWidgetDataInPath(package_folder) == False:
        return
        
    data = GetWidgetConfig(package_folder)
    widget_id = data["widget_id"]
    name = None
    if "name" in data:
        name = data["name"]
    if "py_package" in data:
        name = data["py_package"]
    local_version = "1.0"
    if "version" in data:
        local_version = data["version"]
    user_id = utils.generate_unique_id()
        
    #if in h5&script parent folder, add env path
    if len(package_folder) > 0:
        addWidgetToEnv(package_folder, True)
        
    #package python to private pip server
    requirements_txts = [
        os.path.join(package_folder, "requirements.txt")
    ]
    requirements = ""
    for requirements_txt in requirements_txts:
        if os.path.exists(requirements_txt):
            with open(requirements_txt, "r", encoding="UTF-8") as f:
                ss = f.readlines()
                for s in ss:
                    reals = s.replace("\n","").replace(" ","")
                    if ";" in reals:
                        requirements += f"'{reals[:reals.index(';')]}',"  
                    elif "#" not in reals:
                        requirements += f"'{reals}',"
    pip_dir = os.path.join(os.path.dirname(package_folder), "tmp")
    if os.path.exists(pip_dir):
        shutil.rmtree(pip_dir)
    os.makedirs(pip_dir)
    source_folder_name = _pypi_folder_name(name)
    pip_source_dir = os.path.join(pip_dir, source_folder_name)
    shutil.copytree(package_folder, pip_source_dir)
    config_json_file = os.path.join(pip_source_dir, "config.json") 
    if os.path.exists(config_json_file):
        with open(config_json_file, 'r') as f:
            cc = json.load(f)
        cc["py_package"] = name
        cc["name"] = name
        cc["version"] = local_version
        with open(config_json_file, 'w') as f:
            json.dump(cc, f)
    if os.path.exists(os.path.join(pip_source_dir, "__init__.py")) == False:
        with open(os.path.join(pip_source_dir, "__init__.py"), 'w') as f:
            f.write("")
    #get datafile
    data_file_config = {}
    for root,dirs,files in os.walk(package_folder):
        for file in files:
            if file.find(".") > 0 and file[file.rindex("."):] == ".py":
                continue
            dir_path = os.path.relpath(root, package_folder)
            file_path = os.path.join(dir_path, file)
            file_path = os.path.normpath(file_path).replace("\\", "/")
            k = dir_path.replace("\\", "/")
            if k in data_file_config:
                data_file_config[k].append(file_path)
            else:
                data_file_config[k] = [file_path]
    package_data_str = ""
    for k in data_file_config:
        for p in data_file_config[k]:
            package_data_str += f"'{p}',"
    setup_py = os.path.join(pip_dir, "setup.py")
    with open(setup_py, 'w') as f:
        f.write(f'''import setuptools, os, sys, subprocess, datetime
    
setuptools.setup(
    name="{name}",
    version="{local_version}",
    author="{user_id}",
    author_email="{user_id}@dalipen.com",
    description="ryry widget",
    long_description="privide by ryry-cli",
    long_description_content_type="text/markdown",
    url="https://ryryai.com/#/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=[],
    install_requires=[
        {requirements}
    ],
    package_data={{
        '{name}':[{package_data_str}]
    }},
    entry_points={{
        'console_scripts':[
            '{name} = {source_folder_name}.main:main'
        ]
    }},
    python_requires='>=3.4',
)
''')
    try:
        #build
        subprocess.run(f"python {setup_py} sdist bdist_wheel", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=pip_dir, encoding="utf-8")
        #uninstall
        subprocess.run(f"pip uninstall {name} -y", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
        subprocess.run(f"pip3 uninstall {name} -y", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
        #install
        whl = utils.firstExitWithDir(os.path.join(pip_dir, "dist"), "whl")
        subprocess.run(f"pip install {whl} --extra-index-url https://pypi.python.org/simple/", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
        subprocess.run(f"pip3 install {whl} --extra-index-url https://pypi.python.org/simple/", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
        #upload
        ryry_webapi.uploadWidget(widget_id, name, whl, ".whl", local_version)
        print(f"发布 {name}_{local_version} -> 成功")
    except Exception as ex:
        print(ex)
    finally:
        shutil.rmtree(pip_dir)

def widgetUpdateNotify(widgetName, oldver, newver):
    device_id = utils.generate_unique_id()
    machine_name = socket.gethostname()
    ver = get_distribution("ryry-cli").version
    taskUtils.notifyWechatRobot({
        "msgtype": "text",
        "text": {
            "content": f"机器<{machine_name}[{device_id}]>[{ver}] widget:[{widgetName}]升级版本[{oldver}]->[{newver}]"
        }
    })
    
def widgetInstallNotify(widgetName, newver):
    device_id = utils.generate_unique_id()
    machine_name = socket.gethostname()
    ver = get_distribution("ryry-cli").version
    taskUtils.notifyWechatRobot({
        "msgtype": "text",
        "text": {
            "content": f"机器<{machine_name}[{device_id}]>[{ver}] 安装widget:[{widgetName}][{newver}]"
        }
    })

def pipReInstall(name, url):
    if name:       
        subprocess.run(f"pip uninstall {name} -y", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        subprocess.run(f"pip3 uninstall {name} -y", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    subprocess.run(f"pip install {url} -i https://pypi.python.org/simple/ --extra-index-url https://pypi.python.org/simple/", 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    subprocess.run(f"pip3 install {url} -i https://pypi.python.org/simple/ --extra-index-url https://pypi.python.org/simple/", 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
def UpdateWidgetFromPypi():
    map = store.widgetMap()
    for it in map:
        is_block = False
        if isinstance(map[it], (dict)):
            is_block = map[it]["isBlock"]
            path = map[it]["path"]
        else:
            path = map[it]
        path = os.path.dirname(path)
        if is_block == False and os.path.exists(path):
            data = GetWidgetConfig(path)
            if "name" in data and len(data["name"]) > 0:
                try:
                    py_package = data["name"]
                    local_version = data.get("version", "")
                    widgetid, remote_version, package_url = ryry_webapi.findWidget(py_package)
                    if len(local_version) <= 0:
                        local_version = _local_package_version(py_package)
                    if len(local_version) <= 0:
                        continue
                    if compare_versions(remote_version, local_version) > 0:
                        #update
                        pipReInstall(py_package, package_url)
                        widgetUpdateNotify(py_package, local_version, remote_version)
                except Exception as ex:
                    print(ex)
                    continue
    for widget_id, widget_name, remote_version, package_url in ryry_webapi.getAutoDeployWidget():
        if widget_id not in map:
            try:
                pipReInstall(widget_name, package_url)
                widgetInstallNotify(widget_name, remote_version)
                addWidgetToEnv(widget_name)
            except Exception as ex:
                print(ex)
                continue

def installWidget(name):
    widgetid, remote_version, package_url = ryry_webapi.findWidget(name)
    if len(widgetid) <= 0:
        print(f"{name} 不存在")
        return
    local_version = _local_package_version(name)
    if compare_versions(remote_version, local_version) > 0:
        #update
        pipReInstall(name, package_url)
        widgetInstallNotify(name, remote_version)
        addWidgetToEnv(name)
    else:
        print(f"本地 {local_version} 版本较高，请卸载后再安装")
        