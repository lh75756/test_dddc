import pytest
import requests
import json
import yaml
import allure
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
@allure.feature("协同调度系统测试用例")
class TestDDDC:

    # 上报接口
    @allure.story("上报接口测试用例")
    def test_report(self, logingaj):
        urlLC = "http://testing-url/cooperative_governance_server/event/saveReport"
        env = yaml.safe_load(open("env.yaml"))
        urlLC = str(urlLC).replace("testing-url",env["url"]["urlLC"])
        headers = {"Content-Type": "application/json", "token": f"{logingaj[0]}"}
        # 直接读取配置文件,data的格式为{"data": {"actionLabel": "上报"}}，不是接口需要的参数格式，返回信息为参数异常
        requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接

        # 使用data = data["data"],data的文件格式为{"actionLabel": "上报"}，是正确的接口请求格式
        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataReport = data["dataReport"]
        print(dataReport)
        dataReport = json.dumps(dataReport)
        re = requests.post(url=urlLC, data=dataReport, headers=headers)
        re.encoding='utf-8'
        with allure.step("输出请求结果"):
            print(re.text)
        assert re.status_code == 200
        with allure.step("输出token值"):
            print("token is "f"{logingaj}")



    # 1.返回的列表数据只是分页后的列表数据，不是全部的列表数据
    # 2.bizId和taskId的处理问题，是使用return方式获取bizId和taskId还是直接对bizId和taskId进行赋值
    # 3.对无事件可办结情况的判断（一是待办事件列表中无数据，二是待办待办事件列表中有数据但是不能进行办结）
    # 办结接口
    @allure.story("办结接口测试用例")
    def test_procEnd(self, loginzxy,openListZxyDaiban):
        # 替换事件办结接口url
        urlLC = "http://testing-url/cooperative_governance_server/dispatching/procEnd"
        env = yaml.safe_load(open("env.yaml"))
        urlLC = str(urlLC).replace("testing-url",env["url"]["urlLC"])
        headers = {"ConTent-Type": "application/json", "token": f"{loginzxy[0]}", "userId": f"{loginzxy[1]}"}
        requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接

        print("login返回登录userId")
        print(f"{loginzxy[0]}")
        print(f"{loginzxy[1]}")
        eventNum = openListZxyDaiban["data"]["total"]
        print("坐席员待办事件列表中的数量为:", eventNum)
        mylist = openListZxyDaiban["data"]["list"]
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
            re = requests.post(url=urlLC, data=dataProcEnd, headers=headers)
            response = json.loads(re.text, encoding='utf-8')
            print(response)
            print(re.text)
        else:
            print("待办事件列表中暂无可办结事件")



    # 认领事件接口
    @allure.story("认领接口测试用例")
    def test_assignTask(self,logingaj,OpenListGajDaiban):
        mylist = OpenListGajDaiban["data"]["list"]
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
        urlLC = "http://testing-url/cooperative_governance_server/dispatching/assignTask"
        env = yaml.safe_load(open("env.yaml"))
        urlLC = str(urlLC).replace("testing-url",env["url"]["urlLC"])
        headers = {"Content-Type": "application/json","token": f"{logingaj[0]}","userId": f"{logingaj[1]}"}

        requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接

        print(f"{logingaj[0]}")
        print(f"{logingaj[1]}")
        data = yaml.safe_load(open("data.yaml",encoding='utf-8'))
        dataAssignTask = data["dataAssignTask"]
        dataAssignTask["bizId"] = bizId
        dataAssignTask["taskId"] = taskId
        dataAssignTask = json.dumps(dataAssignTask)
        print(dataAssignTask)
        if bizId is not None and taskId is not None:
            re = requests.post(url=urlLC, data=dataAssignTask, headers=headers)
            print(re)
            print(re.text)
            assert re.status_code == 200
        else:
            print("待办事件列表中无可认领的事件")












