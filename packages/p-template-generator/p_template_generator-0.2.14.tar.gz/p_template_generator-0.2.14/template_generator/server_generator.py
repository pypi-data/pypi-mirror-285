import sys
import os
import time
import json
import threading
from urllib.parse import urlparse
from pathlib import Path
import requests
import zipfile
from urllib.parse import *
import imagesize
from template_generator import binary
from template_generator import ffmpeg
from mecord.pb import aigc_ext_pb2 
from mecord.pb import rpcinput_pb2 

def mediaInfo(path):
    file_name = Path(path).name
    ext = file_name[file_name.index("."):].lower()
    width = 0
    height = 0
    type = "image"
    if ext in [".jpg", ".png", ".jpeg", ".bmp", ".webp", ".gif"]:
        width,height = imagesize.get(path)
        type = "image"
    else:
        width,height,bitrate,fps = ffmpeg.videoInfo(path,"")
        type = "video"
    return type, int(width), int(height)

class MecordAIGC:
    IS_TEST = True
    def _domain(self):
        if self.IS_TEST:
            return "https://mecord-beta.2tianxin.com/proxymsg"
        else:
            return "https://api.mecordai.com/proxymsg"
    def _token(self):
        if self.IS_TEST:
            return"NzN8OGZmZmQ0N2UyNWY1NTY5ZWFhYWNjMzA5OGRiNDcxOTZ8YThmOWM3Nzg2NTM3YzVmMzMzNzY0MTI1NWM4MmZlNzU="
        else:
            return "NDl8NWU5OGI1ODk4N2ExNTZmZWE1MmI4YzM3MTNjNjI0MDd8ZjI2MzYwZTA2ZWVkODg0Y2ZlNjZlZTBlNzVhZDM1OWY="
        
    def __init__(self):
        self.checking = False
        self.result = False, "Unknow"
        self.checkUUID = ""
        self.checkCount = 0

    def _post(self, request, function):
        req = request.SerializeToString()
        opt = {
            "lang": "zh-Hans",
            "region": "CN",
            "appid": "80",
            "application": "template_generator",
            "version": "1.0",
            "uid": "1",
        }
        input_req = rpcinput_pb2.RPCInput(obj="mecord.aigc.AigcExtObj", func=function, req=req, opt=opt)
        try:
            requests.adapters.DEFAULT_RETRIES = 2
            s = requests.session()
            s.keep_alive = False
            s.headers.update({'Connection':'close'})
            res = s.post(url=self._domain(), data=input_req.SerializeToString())
            res_content = res.content
            res.close()
            pb_rsp = rpcinput_pb2.RPCOutput()
            pb_rsp.ParseFromString(res_content)
            s.close()
        except UnicodeDecodeError as e:
            return -1, f"url decode error : {e}", "" 
        except Exception as e:
            return -1, f"error : {e}", ""
        if pb_rsp.ret == 0:
            return 0, "", pb_rsp.rsp
        else:
            return pb_rsp.ret, pb_rsp.desc, "" 
    
    def _findWidget(self, name):
        req = aigc_ext_pb2.WidgetOptionReq()
        rsp = aigc_ext_pb2.WidgetOptionRes()
        r1, r2, r3 = self._post(req, "WidgetOption")
        if r1 != 0:
            return 0
        rsp.ParseFromString(r3)
        for it in rsp.items:
            widget_id = it.id
            widget_name = it.name
            if widget_name.strip().lower() == name.strip().lower():
                return widget_id

    def _getOssUrl(self,ext):
        req = aigc_ext_pb2.UploadFileUrlReq()
        req.token = self._token()
        req.version = "1.0"
        req.fileExt = ext

        rsp = aigc_ext_pb2.UploadFileUrlRes()
        r1, r2, r3 = self._post(req, "UploadFileUrl")
        if r1 != 0:
            return "", r2
        rsp.ParseFromString(r3)
        return rsp.url, rsp.contentType

    def _checkTask(self):
        self.checkCount += 1
        req = aigc_ext_pb2.TaskInfoReq()
        req.taskUUID = self.checkUUID

        rsp = aigc_ext_pb2.TaskInfoRes()
        r1, r2, r3 = self._post(req, "TaskInfo")
        if r1 != 0:
            print("server fail, waiting...")
            return
        rsp.ParseFromString(r3)
        if rsp.taskStatus < 3:
            print("waiting...")#threading.Timer(1, self._checkTask, ()).start()
        elif rsp.taskStatus == 3:
            self.result = True, rsp.url
            self.checking = False
        elif rsp.taskStatus == 4:
            self.result = False, rsp.failReason
            self.checking = False
        
    def _beginCheck(self, uuid):
        self.checkUUID = uuid
        self.checking = True
        self.checkCount = 0

    def _timeout(self):
        return self.checkCount > 600
    
    def _upload(self, f):
        if os.path.exists(f) == False:
            raise Exception(f"upload file not found")

        file_name = Path(f).name
        ossurl, content_type = self._getOssUrl(os.path.splitext(file_name)[-1][1:])
        if len(ossurl) == 0:
            raise Exception(f"oss server is not avalid, msg = {content_type}")

        headers = dict()
        headers['Content-Type'] = content_type
        requests.adapters.DEFAULT_RETRIES = 3
        s = requests.session()
        s.keep_alive = False
        res = s.put(ossurl, data=open(f, 'rb').read(), headers=headers)
        s.close()
        if res.status_code == 200:
            realOssUrl = urljoin(ossurl, "?s")
            return realOssUrl
        else:
            raise Exception(f"upload file fail! res = {res}")
    
    def _processParams(self, inputs, fn_name, params, output_width=0, output_height=0):
        dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp.zip")
        if os.path.exists(dist):
            os.remove(dist)
        zip = zipfile.ZipFile(dist, "w", zipfile.ZIP_DEFLATED)
        first_name = ""
        w = output_width
        h = output_height
        type = ""
        for it in inputs:
            name = Path(it).name
            if len(first_name) == 0:
                first_name = name
                type, w1, h1 = mediaInfo(it)
                if w == 0 or h == 0:
                    w = w1
                    h = h1
            zip.write(it, name)
        zip.close()
        package_url = self._upload(dist)
        os.remove(dist)
        params["fn_name"] = fn_name
        params["package_url"] = package_url
        params["user_file_name"] = first_name
        params["type"] = type
        params["width"] = w
        params["height"] = h

    def testTask(self, widget_id, inputs, fn_name, params, output_width=0, output_height=0):
        req = aigc_ext_pb2.CreateTaskReq()
        req.taskType = 0
        req.labelType = 7
        req.labelValue = 1
        req.user_id = 1  
        req.widget_id = widget_id
        req.widget_data = json.dumps({"fn_name":fn_name,"param":params})
        req.parentTaskId = 0

        rsp = aigc_ext_pb2.CreateTaskRes()
        r1, r2, r3 = self._post(req, "CreateTask")
        if r1 != 0:
            raise Exception(f"create task fail!, reason={r2}")
        
    def createTask(self, inputs, fn_name, params, output_width=0, output_height=0):
        widget_id = self._findWidget(fn_name)
        if widget_id == None or widget_id == 0:
            raise Exception(f"aigc fail, widget_id not found")
        self._processParams(inputs, fn_name, params, output_width, output_height)
        req = aigc_ext_pb2.CreateTaskReq()
        req.taskType = 0
        req.labelType = 7
        req.labelValue = 1
        req.user_id = 1
        req.widget_id = widget_id
        req.widget_data = json.dumps({"fn_name":fn_name,"param":params})
        req.parentTaskId = 0

        rsp = aigc_ext_pb2.CreateTaskRes()
        r1, r2, r3 = self._post(req, "CreateTask")
        if r1 != 0:
            raise Exception(f"create task fail!, reason={r2}")
        rsp.ParseFromString(r3)
        self._beginCheck(rsp.taskUUID)
        while self.checking or self._timeout():
            self._checkTask()
            time.sleep(1)
        success, data = self.result
        if success:
            return data
        else:
            raise Exception(f"aigc fail, reason={data}")

def process(inputs, fn_name, params, output_width=0, output_height=0):
    result_url = MecordAIGC().createTask(inputs, fn_name, params, output_width, output_height)
    result_url_path = urlparse(result_url).path
    savePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{Path(result_url_path).stem}{Path(result_url_path).suffix}")
    if os.path.exists(savePath):
        os.remove(savePath)
    s = requests.session()
    s.keep_alive = False
    file = s.get(result_url, verify=False)
    with open(savePath, "wb") as c:
        c.write(file.content)
    s.close()
    if os.path.exists(savePath):
        return savePath
    else:
        raise Exception(f"aigc success, but download fail!")
