import pytest
import os
import requests
import yaml

def pytest_addoption(parser):
    parser.addini("env","运行环境",default="UAT")
    parser.addini("base_url","接口基础地址",default="https://iot.dreamewash.com")
    parser.addini("username", "登录账号", default="")
    parser.addini("password", "登录密码", default="")
    parser.addini("test_uid","自动化测试账号",default="")
    parser.addini("test_name","自动化测试账号密码",default="")

@pytest.fixture(scope="session")
def base_url(pytestconfig):    #pytestconfig是pytest内置的，专门用来读取pytest.ini里的配置
    """获取全局配置的base_url"""
    return os.getenv("BASE_URL") or pytestconfig.getini("base_url")

@pytest.fixture(scope="session")
def test_account(pytestconfig):
    """获取全局配置的账号密码"""

    username = os.getenv("TEST_USERNAME") or pytestconfig.getini("username")
    password = os.getenv("TEST_PASSWORD") or pytestconfig.getini("password")

    return {
        "username": username,
        "password": password
    }

@pytest.fixture(scope="session")
def auth_token(base_url,test_account):
    print("\n正在自动登录获取最新的token...")
    login_url=f"{ base_url}/api/dreame-auth/oauth/token"

    LOGIN_PARAMS={      #参数一般是后端提供，或者抓包时contents中的Query String
        "username":test_account["username"],
        "password":test_account["password"],
        "grant_type": "password",
        "scope": "all",     
        "type":"account",
        "login_system":"management_system",
        "signtype":"pk"
    }

    login_headers={
        "authorization":"Basic ZHJlYW1lX3N5czo0TDZyZjVTb0Jlc3hsTWdj",
        "tenant-id":"000000"
    }
    response=requests.post(login_url,headers=login_headers,params=LOGIN_PARAMS)
    result=response.json()

    token=result.get("access_token")
    assert token is not None,f"登录未拿到token,响应:{result}"

    print(f"登录成功！获取到最新Token：{token[:20]}....")     #既确认了拿到 Token，又保持了终端界面的整洁。这是高级开发日志的常见写法。
    return token

@pytest.fixture
def headers(auth_token):
    return {
        'authorization':"Basic ZHJlYW1lX3N5czo0TDZyZjVTb0Jlc3hsTWdj",
        'dreame-auth':f'bearer {auth_token}',
        'cookie':'ajs_user_id=b152926bf742628104008e60b37353faefcd3d3c;ajs_anonymous_id=9e8e428a-4dfd-4ef5-8d47-9b4d212e5be5',
        'tenant-id':'000000'
    }



#自动生成Allure报告的environment信息
def pytest_sessionstart(session):   #钩子函数(HOOK),每次运行测试前，会在result文件夹里生成environment.properties文件，Allure报告会自动读取这个文件，并在报告的environment页面展示
    """在测试开始时,自动生成environment.properties供Allure读取"""
    env=session.config.getini("env") if session.config.getini("env") else "UAT"
    base_url=session.config.getini("base_url")
    #确保result目录存在

    if not os.path.exists("result"):
        os.makedirs("result")

    env_file="result/environment.properties"
    with open(env_file,"w",encoding="utf-8") as f:
        f.write(f"测试环境={env}\n")
        f.write(f"接口域名={base_url}\n")
        f.write("测试人员=Admin\n")
        f.write("Python版本=3.10\n")

@pytest.fixture(scope="session")
def yaml_data():
    file_path=os.path.join(os.path.dirname(__file__),"test_data.yaml")
    with open(file_path,"r",encoding="utf-8") as f:
        data=yaml.safe_load(f)
    return data
    