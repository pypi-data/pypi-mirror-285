import json
import os
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
import shutil
import zipfile


NODE_TYPE_FOLDER = os.path.join(os.path.dirname(__file__), "nodeextension")
NODE_TYPE_REGISTER = {}


def insertToObj(obj, path, value):
    for k in path[:-1]:
        obj = obj[k] if k in obj.keys() else obj['subpackages'][k]
    if ('isPackage' in obj.keys()):
        obj['subpackages'][path[-1]] = value
    else:
        obj[path[-1]] = value


def loadNodeExtensions():
    nodes_folder = NODE_TYPE_FOLDER
    register = NODE_TYPE_REGISTER
    for folder, dirs, files in os.walk(nodes_folder):
        relativeFolder = folder[len(nodes_folder) + 1:]
        for file in files:
            path = os.path.join(folder, file)
            content = None
            try:
                with open(path, "r") as f:
                    content = json.load(f)
            except:
                print("Error reading file: " + path)
                continue
            if content is not None:
                insertToObj(register, os.path.join(
                    relativeFolder, os.path.splitext(file)[0]).split(os.sep), content)
        for dir in dirs:
            insertToObj(register, os.path.join(
                relativeFolder, dir).split(os.sep), {'isPackage': True, 'subpackages': {}})


def loadNodeExtension(name):
    nodes_folder = NODE_TYPE_FOLDER
    register = NODE_TYPE_REGISTER
    target_path = os.path.join(nodes_folder, name)
    if (os.path.isfile(target_path + ".json")):
        with open(target_path + ".json", "r") as f:
            content = json.load(f)
            if content is not None:
                insertToObj(register, [name], content)
    elif (os.path.isdir(target_path)):
        insertToObj(register, [name], {'isPackage': True, 'subpackages': {}})
        for folder, dirs, files in os.walk(target_path):
            relativeFolder = folder[len(nodes_folder) + 1:]
            for file in files:
                path = os.path.join(folder, file)
                content = None
                try:
                    with open(path, "r") as f:
                        content = json.load(f)
                except:
                    print("Error reading file: " + path)
                    continue
                if content is not None:
                    insertToObj(register, os.path.join(
                        relativeFolder, os.path.splitext(file)[0]).split(os.sep), content)
            for dir in dirs:
                insertToObj(register, os.path.join(
                    relativeFolder, dir).split(os.sep), {'isPackage': True, 'subpackages': {}})


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "packages": NODE_TYPE_REGISTER,
        }))

    def addNewExtension(self, files):
        pkgs = {}
        for file in files:
            if (file['content_type'] == 'text/plain' or file['content_type'] == 'application/json'):
                with open(os.path.join(NODE_TYPE_FOLDER, file['filename']), 'w') as f:
                    f.write(file['body'].decode('utf-8'))
            if (file['content_type'] == 'application/octet-stream'):
                with open(os.path.join(NODE_TYPE_FOLDER, file['filename']), 'wb') as f:
                    f.write(file['body'])
                with zipfile.ZipFile(os.path.join(NODE_TYPE_FOLDER, file['filename']), 'r') as zip_ref:
                    zip_ref.extractall(NODE_TYPE_FOLDER)
                os.remove(os.path.join(NODE_TYPE_FOLDER, file['filename']))
            name = file['filename'].split('.')[0]
            loadNodeExtension(name)
            if (NODE_TYPE_REGISTER[name]):
                pkgs[name] = NODE_TYPE_REGISTER[name]
        self.finish(json.dumps({
            "status": "ok",
            "packages": pkgs,
        }))

    def enableExtension(self, path, enable):
        if (path == None):
            self.finish(json.dumps({
                "message": "the input path is empty",
            }))
            return
        fullpath = os.path.join(NODE_TYPE_FOLDER, path)
        if (os.path.isdir(fullpath)):
            fullpath = os.path.join(fullpath, "__init__")
        fullpath = fullpath + ".json"
        if (os.path.exists(fullpath) and os.path.isfile(fullpath)):
            with open(fullpath, "r") as f:
                content = json.load(f)
            content['enable'] = enable
            with open(fullpath, "w") as f:
                json.dump(content, f)
            self.finish(json.dumps({
                "status": "ok"
            }))
        else:
            self.finish(json.dumps({
                "message": "fail, the input path is not valid"
            }))

    def post(self):
        if (self.request.files and 'files' in self.request.files.keys()):
            self.addNewExtension(self.request.files['files'])
            return
        payload = json.loads(self.request.body)
        path = payload['name']
        if (path == None):
            self.finish(json.dumps({
                "message": "the input path is empty",
            }))
            return
        self.enableExtension(path, payload['enable'])

    def delete(self):
        path = json.loads(self.request.body).split('.')
        if (len(path) == 0):
            self.finish(json.dumps({
                "message": "the input path is empty",
            }))
            return
        # delete in the register
        filePath = ''
        isDir = False
        isContent = False
        if (len(path) == 1):
            isDir = True
            filePath = path[0]
            del NODE_TYPE_REGISTER[path[0]]
            isDir = os.path.isdir(os.path.join(NODE_TYPE_FOLDER, filePath))
        else:
            if (path[0] not in NODE_TYPE_REGISTER.keys()):
                self.finish(json.dumps({
                    "message": "fail, the input path is not valid",
                }))
                return
            package = NODE_TYPE_REGISTER[path[0]]
            for i in range(1, len(path) - 1):
                package = package[path[i]]
            filePath = os.sep.join(path[:-1])
            if package['isPackage']:
                if path[-1] in package.keys():
                    filePath = os.path.join(filePath, path[-1])
                    isDir = 'isPackage' in package[path[-1]].keys()
                    del package[path[-1]]
                else:
                    package = package["__init__"]
                    filePath = os.path.join(filePath, "__init__")
                    isContent = True
                    if (path[-1] in package['nodes'].keys()):
                        del package['nodes'][path[-1]]
                    else:
                        self.finish(json.dumps({
                            "message": "fail, the input path is not valid"
                        }))
                        return
            else:
                if (path[-1] in package['nodes'].keys()):
                    isContent = True
                    del package['nodes'][path[-1]]
                else:
                    self.finish(json.dumps({
                        "message": "fail, the input path is not valid"
                    }))
                    return

        # delete in the file system
        if (isDir):
            shutil.rmtree(os.path.join(NODE_TYPE_FOLDER, filePath))
        elif isContent == False:
            os.remove(os.path.join(NODE_TYPE_FOLDER, filePath) + ".json")
        else:
            with open(os.path.join(NODE_TYPE_FOLDER, filePath) + ".json", "r") as f:
                content = json.load(f)
            del content['nodes'][path[-1]]
            with open(os.path.join(NODE_TYPE_FOLDER, filePath) + ".json", "w") as f:
                json.dump(content, f)
        self.finish(json.dumps({
            "status": "ok"
        }))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "vp4jl", "node_extension_manager")
    loadNodeExtensions()
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
