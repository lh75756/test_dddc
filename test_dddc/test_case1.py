import pytest
import requests
import json
import yaml
# 后续需要完成的工作:
# 1.断言的优化，需要更加准确
# 2.将打开事件列表接口独立出来
# 3.编写剩余其他接口
# 4.将代码提交至git
class TestDDDC:
    # 使用读取配置文件的方式，灵活的修改url
    urlUc = "http://testing-url/user/login"
    env =yaml.safe_load(open("env.yaml"))
    urlUc = str(urlUc).replace("testing-url",env["url"]["urlUc"])

    @pytest.fixture()
    def test_logingaj(self):
        url = self.urlUc
        # headers必须为字典类型
        headers = {"Content-Type": "application/json"}
        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataGaj = data["dataGaj"]
        print(type(data))
        # 将字典类型的数据转化为字符串类型(json类型)
        dataGaj = json.dumps(dataGaj)
        # 方式1:现将data转换为字符串类型，然后使用data参数
        re = requests.post(url=url, data=dataGaj, headers=headers)
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
        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataZxy = data["dataZxy"]
        dataZxy = json.dumps(dataZxy)
        re = requests.post(url=url, data=dataZxy, headers=headers)
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
        # 直接读取配置文件,data的格式为{"data": {"actionLabel": "上报"}}，不是接口需要的参数格式，返回信息为参数异常
        # 使用data = data["data"],data的文件格式为{"actionLabel": "上报"}，是正确的接口请求格式
        data = yaml.safe_load(open("data.yaml",encoding='UTF-8'))
        dataReport = data["dataReport"]
        print(dataReport)
        dataReport = json.dumps(dataReport)
        print(data)
        re = requests.post(url=urlLC, data=dataReport, headers=headers)
        print(re.text)
        assert re.status_code == 200

    # 1.返回的列表数据只是分页后的列表数据，不是全部的列表数据
    # 2.bizId和taskId的处理问题，是使用return方式获取bizId和taskId还是直接对bizId和taskId进行赋值
    # 3.对无事件可办结情况的判断（一是待办事件列表中无数据，二是待办待办事件列表中有数据但是不能进行办结）
    # 办结接口
    def test_procEnd(self, test_loginzxy):
        # 替换事件办结接口url
        urlLC = "http://testing-url/event/openList"
        env = yaml.safe_load(open("env.yaml"))
        urlLC = str(urlLC).replace("testing-url", env["url"]["urlLC"])
        # 替换打开事件类表接口url
        urlLC1 = "http://testing-url/dispatching/procEnd"
        env = yaml.safe_load(open("env.yaml"))
        urlLC1 = str(urlLC1).replace("testing-url",env["url"]["urlLC"])

        headers = {"ConTent-Type": "application/json", "token": f"{test_loginzxy[0]}", "userId": f"{test_loginzxy[1]}"}
        print("login返回登录userId")
        print(f"{test_loginzxy[0]}")
        print(f"{test_loginzxy[1]}")
        headers1 = {"Content-Type": "application/json", "token": f"{test_loginzxy[0]}"}

        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataOpenList = data["dataOpenList"]
        dataOpenList["userId"] = f"{test_loginzxy[1]}"
        dataOpenList = json.dumps(dataOpenList)
        print(dataOpenList)
        re1 = requests.post(url=urlLC, data=dataOpenList, headers=headers1)
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

        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataProcEnd = data["dataProcEnd"]
        print(dataProcEnd)
        dataProcEnd["bizId"] = bizId
        dataProcEnd["taskId"] = taskId
        dataProcEnd = json.dumps(dataProcEnd)
        print(dataProcEnd)
        if bizId is not None and taskId is not None:
            re = requests.post(url=urlLC1, data=dataProcEnd, headers=headers)
            response = json.loads(re.text, encoding='utf-8')
            print(response)
        else:
            print("待办事件列表中暂无可办结事件")
