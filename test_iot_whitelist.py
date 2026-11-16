import requests
import pytest
import allure
import yaml
import os

@pytest.fixture
def setup_and_cleanup_user(base_url,headers,test_user):
     target_uid=test_user["uid"]
     target_name=test_user["name"]
     created_user_id=None

     with allure.step(f"[前置]新增白名单账号：{target_uid}"):
          add_url=f"{base_url}/api/dreame-user/userproduct/save"
          body={
               "uid":target_uid,
               "realName":target_name,
               "remark":"",
               "products":[{"productId":"","model":"ALLMODELS","productName":""}],
               "roleType":"1"
          }
          response=requests.post(add_url,headers=headers,json=body)
          result=response.json()

          if result.get('code') !=0 and "已存在"  not in str(result.get('msg')) and "10000" not in str(result.get('code')):
                pytest.fail(f"前置新增失败，服务器报错：{result}")

     with allure.step("[前置]查询获取真实的userID(供清理使用)"):
          list_url=f"{base_url}/api/dreame-user/userproduct/list"
          params={                    #为什么参数是这几个
               "current": "1", 
               "size": "10", 
               "uid": target_uid         
          }
          res=requests.get(list_url,headers=headers,params=params).json()
          if res.get("code")==0 and len(res["data"]["records"])>0:
                created_user_id=res["data"]["records"][0].get("userId")
                print(f"\n 成功提取到userId:{created_user_id}")
     yield {"uid":target_uid,"name":target_name,"user_id":created_user_id}

     if created_user_id:
            with allure.step(f"[后置]清理测试数据(userId:{created_user_id})"):
                 del_url=f"{base_url}/api/dreame-user/userproduct/delWhite"
                 del_response=requests.post(del_url,headers=headers,json=[created_user_id])
                 del_result=del_response.json()
                 if  del_result.get('code')==0:
                        print(f"\n🧹 完美清理测试脏数据！已删除 userId: {created_user_id}")
                 else:
                        print(f"\n⚠️ 清理失败，服务器返回: {del_result}")
     else:
            print("\n 未获取到 userId，跳过后置清理。")

def get_yaml_data():
      file_path=os.path.join(os.path.dirname(__file__),"test_data.yaml")
      with open(file_path,"r",encoding="utf-8") as f:
            return yaml.safe_load(f)["whitelist_users"]

@allure.title("查询白名单并验证新增用户-{test_user[uid]}")
@pytest.mark.parametrize("test_user",get_yaml_data())

def test_query_whitelist(base_url,headers,setup_and_cleanup_user,test_user):
    my_uid=setup_and_cleanup_user["uid"]
    my_name=setup_and_cleanup_user["name"]

    url=f"{base_url}/api/dreame-user/userproduct/list"
    WHITE_PARAMS={
         "current": "1",
         "size": "10",
         "uid": my_uid
    }


    with allure.step("1.发送新增白名单用户的POST请求"):
        response=requests.get(url,headers=headers,params=WHITE_PARAMS)

    with allure.step ("2.验证HTTP状态码和业务状态码"):
        assert response.status_code==200,f"HTTP状态码错误,实际为:{response.status_code}"
        result=response.json()

        assert result['code'] == 0, f"业务报错：{result.get('msg')}"
        assert result['success'] is True, "success字段不为True"


    with allure.step("3.验证数据一致性"):
          records_list=result["data"]["records"]
          assert len(records_list)>0,"查询结果为空,没找到新增数据"
          first_record=records_list[0]
          assert str(first_record['uid'])==str(my_uid),f"uid不匹配,实际为{first_record['uid']}"
          assert first_record['realName']==my_name,f"姓名不匹配，实际为：{first_record.get('realName')}"
          print(f"\n 数据一致性校验通过！查到的用户：{first_record['uid']}-{first_record['realName']}")
