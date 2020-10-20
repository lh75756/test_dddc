# 此代码为协同调度接口测试用例V1.0版本代码，代码未进行封装和优化
# 以后使用git进行统一管理
import pytest
import requests
import json
import yaml
import allure


# fixture conftest setup 参数化

class TestDDDC:
    # 使用读取配置文件的方式，灵活的修改url
    urlUc = "http://testing-url/user/login"
    env =yaml.safe_load(open("env.yaml"))
    urlUc = str(urlUc).replace("testing-url",env["url"]["urlUc"])

    def setup_class(self):
        print("开始获取token")
        url = self.urlUc
        # headers必须为字典类型
        headers = {"Content-Type": "application/json"}
        data = {
            "loginAccount": "gajlh",
            "loginPwd": "000000"
        }
        data = json.dumps(data)
        re = requests.post(url=url, data=data, headers=headers)
        response = json.loads(re.text, encoding='utf-8')
        if response["code"] == 0:
            print(response["data"]["token"])
            return response["data"]["token"]
        else:
            return "请求失败!"


    def teardown_class(self):
        print("已成功获取token")

    @pytest.fixture()
    def test_logingaj(self):
        url = self.urlUc
        # headers必须为字典类型
        headers = {"Content-Type": "application/json"}
        data = {
            "loginAccount": "gajlh",
            "loginPwd": "000000"
        }
        print(type(data))
        # 将字典类型的数据转化为字符串类型(json类型)
        data = json.dumps(data)
        # 方式1:现将data转换为字符串类型，然后使用data参数
        re = requests.post(url=url, data=data, headers=headers)
        # 方式2:data为字典类型，使用json参数，该参数自动将字典类型的对象转换为json格式
        # response = requests.post(url=url, json=data, headers=headers)
        re.status_code = 200
        response = json.loads(re.text, encoding='utf-8')
        if response["code"] == 0:
            print(response["data"]["token"])
            return response["data"]["token"]
        else:
            return "请求失败!"

    @pytest.fixture()
    def test_loginzxy(self):
        url = self.urlUc
        headers = {"Content-Type": "application/json"}
        data = {
            "loginAccount": "zxylh",
            "loginPwd": "000000"
        }
        data = json.dumps(data)
        re = requests.post(url=url, data=data, headers=headers)
        response = json.loads(re.text, encoding='utf-8')
        if response["code"] == 0:
            print(response["data"]["token"])
            return response["data"]["token"], response["data"]["userId"]
        else:
            return "请求失败!"

    # 上报接口
    def test_report(self, test_logingaj):
        urlLC = "http://testing-url/event/saveReport"
        env = yaml.safe_load(open("env.yaml"))
        urlLC = str(urlLC).replace("testing-url",env["url"]["urlLC"])
        headers = {"Content-Type": "application/json", "token": f"{test_logingaj}"}
        # 直接读取配置文件,data的格式为{"data": {"actionLabel": "上报"}}，不是借口需要的参数格式，返回信息为参数异常
        # 使用data = data["data"],data的文件格式为{"actionLabel": "上报"}，是正确的接口请求格式
        data = yaml.safe_load(open("data.yaml",encoding='UTF-8'))
        data = data["dataReport"]
        print(data)
        data = json.dumps(data)
        print(data)
        re = requests.post(url=urlLC, data=data, headers=headers)
        print(re.text)
        assert re.status_code == 200

    # 1.返回的列表数据只是分页后的列表数据，不是全部的列表数据
    # 2.bizId和taskId的处理问题，是使用return方式获取bizId和taskId还是直接对bizId和taskId进行赋值
    # 3.对无事件可办结情况的判断（一是待办事件列表中无数据，二是待办待办事件列表中有数据但是不能进行办结）
    # 办结接口
    def test_procEnd(self, test_loginzxy):
        url = "http://172.15.33.62:27018/dispatching/procEnd"
        headers = {"ConTent-Type": "application/json", "token": f"{test_loginzxy[0]}", "userId": f"{test_loginzxy[1]}"}
        print("login返回登录userId")
        print(f"{test_loginzxy[0]}")
        print(f"{test_loginzxy[1]}")
        # 调用openList接口，打开事件列表
        url1 = "http://172.15.33.62:27018/event/openList"
        headers1 = {"Content-Type": "application/json", "token": f"{test_loginzxy[0]}"}
        data1 = {
            "pageNum": 1,
            "pageSize": 100,
            "queryListCode": "daibanlistNoUnit",
            "roleId": 22,
            "userId": f"{test_loginzxy[1]}"
        }
        data1 = json.dumps(data1)
        re1 = requests.post(url=url1, data=data1, headers=headers1)
        response1 = json.loads(re1.text, encoding='utf-8')
        eventNum = response1["data"]["total"]
        print("坐席员待办事件列表中的数量为:", eventNum)
        mylist = response1["data"]["list"]
        mylistLen = len(mylist)
        print(type(mylist))
        print("返回列表的长度为", len(mylist))
        if mylistLen == 0:
            print("待办事件列表中无事件")
        # 判断待办事件列表中是否有可以办结的事件
        for i in range(mylistLen):
            if mylist[i]["eventStateName"] == "已核实" or mylist[i]["eventStateName"] == "已处置":
                bizId = mylist[i]["actObject"]["bizId"]
                taskId = mylist[i]["actObject"]["taskId"]
                break
            else:
                bizId = None
                taskId = None
        data = {
            "actionLabel": "办结",
            "actionName": "archive",
            "bizId": bizId,
            "opinion": "1111111",
            "roleIds": 22,
            "taskId": taskId
        }
        data = json.dumps(data)
        if bizId is not None and taskId is not None:
            re = requests.post(url=url, data=data, headers=headers)
            response = json.loads(re.text, encoding='utf-8')
            print(response)
        else:
            print("待办事件列表中暂无可办结事件")
