import json

import pytest
import yaml
import requests

# 使用读取配置文件的方式，灵活的修改url
urlUc = "http://172.15.33.65:27012//user/login"


# env =yaml.safe_load(open("env.yaml"))
# urlUc = str(urlUc).replace("testing-url",env["url"]["urlUc"])
# 登录接口
@pytest.fixture(scope='module')
def logingaj():
    url = "http://172.15.33.65:27012//user/login"
    # headers必须为字典类型
    headers = {"Content-Type": "application/json"}
    data = yaml.safe_load(open("data.yaml", encoding='utf-8'))
    dataGaj = data["dataGaj"]
    print(type(data))
    # 将字典类型的数据转化为字符串类型(json类型)
    dataGaj = json.dumps(dataGaj)
    # 方式1:现将data转换为字符串类型，然后使用data参数
    re = requests.post(url=url, data=dataGaj, headers=headers)
    # 方式2:data为字典类型，使用json参数，该参数自动将字典类型的对象转换为json格式
    # response = requests.post(url=url, json=data, headers=headers)
    re.encoding = "utf-8"
    re.status_code = 200
    response = json.loads(re.text, encoding='utf-8')
    if response["code"] == 0:
        print(response["data"]["token"])
        return response["data"]["token"], response["data"]["userId"]
    else:
        return "请求失败!"

@pytest.fixture(scope='module')
def loginzxy():
    url = "http://172.15.33.65:27012//user/login"
    headers = {"Content-Type": "application/json"}
    data = yaml.safe_load(open("data.yaml", encoding='utf-8'))
    dataZxy = data["dataZxy"]
    dataZxy = json.dumps(dataZxy)
    re = requests.post(url=url, data=dataZxy, headers=headers)
    response = json.loads(re.text, encoding='utf-8')
    if response["code"] == 0:
        print(response["data"]["token"])
        return response["data"]["token"], response["data"]["userId"]
    else:
        return "请求失败!"

# 打开坐席员待办事件列表接口
@pytest.fixture(scope='module')
def openListZxyDaiban(loginzxy):
    urlLC = "http://testing-url/cooperative_governance_server/event/openList"
    # 读取配置文件
    env = yaml.safe_load(open("env.yaml"))
    # 替换testing-url
    urlLC = str(urlLC).replace("testing-url", env["url"]["urlLC"])
    headers = {"Content-Type": "application/json", "token": f"{loginzxy[0]}"}
    data = yaml.safe_load(open("data.yaml", encoding='utf-8'))
    dataOpenListZxyDaiban = data["dataOpenListZxyDaiban"]
    dataOpenListZxyDaiban["userId"] = f"{loginzxy[1]}"
    dataOpenListZxyDaiban = json.dumps(dataOpenListZxyDaiban)
    print(dataOpenListZxyDaiban)
    re = requests.post(url=urlLC, data=dataOpenListZxyDaiban, headers=headers)
    response = json.loads(re.text, encoding='utf-8')
    print(response)
    return response

# 打开处置单位待办事件列表接口
@pytest.fixture(scope='module')
def OpenListGajDaiban(logingaj):
    urlLC = "http://testing-url/cooperative_governance_server/event/openList"
    # 读取配置文件
    env = yaml.safe_load(open("env.yaml"))
    # 替换testing-url
    urlLC = str(urlLC).replace("testing-url", env["url"]["urlLC"])
    headers = {"Content-Type": "application/json", "token": f"{logingaj[0]}"}
    data = yaml.safe_load(open("data.yaml", encoding='utf-8'))
    dataOpenListGajDaiban = data["dataOpenListGajDaiban"]
    dataOpenListGajDaiban["userId"] = f"{logingaj[1]}"
    dataOpenListGajDaiban = json.dumps(dataOpenListGajDaiban)
    print(dataOpenListGajDaiban)
    re = requests.post(url=urlLC, data=dataOpenListGajDaiban, headers=headers)
    response = json.loads(re.text, encoding='utf-8')
    print(response)
    return response
