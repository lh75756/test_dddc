import pytest
import requests
import json
import yaml
# 后续需要完成的工作:
# 1.断言的优化，需要更加准确
# 2.登录接口和打开事件列表接口作为公共的方法
# 3.编写剩余其他接口
# 4.将代码提交至git
# 5.在两个登录方法中添加@pytest.fixture()后，无法收集到测试用例
# 2020.12.30解决问题包括:
# (1)请求地址更换(如何实现地址的灵活更换)
# (2)test_case前不能添加@pytest.fixture()
# (3)json.decoder.JSONDecodeError是json的格式不对，可能是返回值为空，但是仍然去返回值里边以json的格式去拿值
# (4)接口跑不通，请求url 请求头  请求参数这三个方面去找
# (5)出现9100 ，oauth未登录，原因是token值传错了，应该是"token": f"{logingaj[0]}"，写成了"token": f"{logingaj}"
class TestDDDC:
    # 使用读取配置文件的方式，灵活的修改url
    urlUc = "http://172.15.33.65:27012//user/login"
    # env =yaml.safe_load(open("env.yaml"))
    # urlUc = str(urlUc).replace("testing-url",env["url"]["urlUc"])

    # 登录接口
    @pytest.fixture()
    def logingaj(self):
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
        re.encoding="utf-8"
        re.status_code = 200
        response = json.loads(re.text, encoding='utf-8')
        if response["code"] == 0:
            print(response["data"]["token"])
            return response["data"]["token"], response["data"]["userId"]
        else:
            return "请求失败!"

    @pytest.fixture()
    def loginzxy(self):
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
    def test_report(self, logingaj):
        urlLC = "http://testing-url/cooperative_governance_server/event/saveReport"
        env = yaml.safe_load(open("env.yaml"))
        urlLC = str(urlLC).replace("testing-url",env["url"]["urlLC"])
        headers = {"Content-Type": "application/json", "token": f"{logingaj[0]}"}
        # 直接读取配置文件,data的格式为{"data": {"actionLabel": "上报"}}，不是接口需要的参数格式，返回信息为参数异常
        # 使用data = data["data"],data的文件格式为{"actionLabel": "上报"}，是正确的接口请求格式
        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataReport = data["dataReport"]
        print(dataReport)
        dataReport = json.dumps(dataReport)
        re = requests.post(url=urlLC, data=dataReport, headers=headers)
        re.encoding='utf-8'
        print(re.content)
        print(re.headers)
        print(re.text)
        assert re.status_code == 200
        print("token is "f"{logingaj}")

    # 1.返回的列表数据只是分页后的列表数据，不是全部的列表数据
    # 2.bizId和taskId的处理问题，是使用return方式获取bizId和taskId还是直接对bizId和taskId进行赋值
    # 3.对无事件可办结情况的判断（一是待办事件列表中无数据，二是待办待办事件列表中有数据但是不能进行办结）
    # 办结接口
    def test_procEnd(self, loginzxy):
        # 替换事件办结接口url
        urlLC = "http://testing-url/cooperative_governance_server/event/openList"
        env = yaml.safe_load(open("env.yaml"))
        urlLC = str(urlLC).replace("testing-url", env["url"]["urlLC"])
        # 替换打开事件类表接口url
        urlLC1 = "http://testing-url/cooperative_governance_server/dispatching/procEnd"
        env = yaml.safe_load(open("env.yaml"))
        urlLC1 = str(urlLC1).replace("testing-url",env["url"]["urlLC"])

        headers = {"ConTent-Type": "application/json", "token": f"{loginzxy[0]}", "userId": f"{loginzxy[1]}"}
        print("login返回登录userId")
        print(f"{loginzxy[0]}")
        print(f"{loginzxy[1]}")
        headers1 = {"Content-Type": "application/json", "token": f"{loginzxy[0]}"}

        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataOpenListZxyDaiban = data["dataOpenListZxyDaiban"]
        dataOpenListZxyDaiban["userId"] = f"{loginzxy[1]}"
        dataOpenListZxyDaiban = json.dumps(dataOpenListZxyDaiban)
        print(dataOpenListZxyDaiban)
        re1 = requests.post(url=urlLC, data=dataOpenListZxyDaiban, headers=headers1)
        response1 = json.loads(re1.text,encoding='utf-8')
        eventNum = response1["data"]["total"]
        print("坐席员待办事件列表中的数量为:", eventNum)
        mylist = response1["data"]["list"]
        mylistLen = len(mylist)
        print(type(mylist))
        print("返回列表的长度为", len(mylist))

        if mylistLen == 0:
            print("待办事件列表中无事件")
        # 判断待办事件列表中是否有可以办结的事件,如果有，取出bizId和taskId
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
            print(re.text)
        else:
            print("待办事件列表中暂无可办结事件")

    # 打开事件列表接口
    def test_openList(self,loginzxy):
        urlLC = "http://testing-url/cooperative_governance_server/event/openList"
        # 读取配置文件
        env = yaml.safe_load(open("env.yaml"))
        # 替换testing-url
        urlLC = str(urlLC).replace("testing-url",env["url"]["urlLC"])
        headers = {"Content-Type": "application/json","token": f"{loginzxy[0]}"}
        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataOpenListZxyDaiban = data["dataOpenListZxyDaiban"]
        dataOpenListZxyDaiban["userId"] = f"{loginzxy[1]}"
        dataOpenListZxyDaiban = json.dumps(dataOpenListZxyDaiban)
        print(dataOpenListZxyDaiban)
        re = requests.post(url=urlLC, data=dataOpenListZxyDaiban, headers=headers)
        print(re.text)
        assert re.status_code == 200

    # 认领事件接口
    def test_assignTask(self,logingaj):
        urlLC = "http://testing-url/cooperative_governance_server/event/openList"
        env = yaml.safe_load(open("env.yaml"))
        urlLC =str(urlLC).replace("testing-url",env["url"]["urlLC"])
        headers = {"Content-Type": "application/json","token": f"{logingaj[0]}"}
        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataOpenListGajDaiban = data["dataOpenListGajDaiban"]
        dataOpenListGajDaiban["userId"] = f"{logingaj[1]}"
        dataOpenListGajDaiban = json.dumps(dataOpenListGajDaiban)
        re = requests.post(url=urlLC, data=dataOpenListGajDaiban, headers=headers)
        response = json.loads(re.text,encoding='utf-8')
        mylist = response["data"]["list"]
        mylistLen = len(mylist)
        if mylistLen == 0:
            print("待办事件列表中无事件")
        # 判断处置单位的待办事件列表中是否有可认领的事件
        for i in range(mylistLen):
            if mylist[i]["eventStateName"] == "已立案":
                bizId = mylist[i]["actObject"]["bizId"]
                taskId = mylist[i]["actObject"]["taskId"]
                break
            else:
                bizId = None
                taskId = None
        print("bizId is:",bizId)
        print("taskId is:",taskId)

        urlLC1 = "http://testing-url/cooperative_governance_server/dispatching/assignTask"
        env = yaml.safe_load(open("env.yaml"))
        urlLC1 = str(urlLC1).replace("testing-url",env["url"]["urlLC"])
        headers1 = {"Content-Type": "application/json","token": f"{logingaj[0]}","userId": f"{logingaj[1]}"}
        print(f"{logingaj[0]}")
        print(f"{logingaj[1]}")
        data1 = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataAssignTask = data1["dataAssignTask"]
        dataAssignTask["bizId"] = bizId
        dataAssignTask["taskId"] = taskId
        dataAssignTask = json.dumps(dataAssignTask)
        print(dataAssignTask)
        if bizId is not None and taskId is not None:
            re1 = requests.post(url=urlLC1, data=dataAssignTask, headers=headers1)
            print(re1)
            print(re1.text)
            assert re1.status_code == 200
        else:
            print("待办事件列表中无可认领的事件")










