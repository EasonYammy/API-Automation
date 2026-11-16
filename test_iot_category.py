import requests
import pytest
import time
import allure


@allure.title("测试分类层级:{check_path}")
@pytest.mark.parametrize("check_path,expected_zh",[       #为什么参数是这两个
    ("/lifeapps","生活电器"),      #在HTTP请求头里，是Key：Value;python字典里是{"Key":"Value"};在函数参数和元组里("A","B")
    ("/lifeapps/hold","清洁"),
    ("/lifeapps/pet","宠物"),
    ("/lifeapps/bath","智能卫浴"),
    ("/lifeapps/winbot","擦窗机"),

])
def test_get_category_hierarchy(base_url,headers,check_path,expected_zh):
    url=f"{base_url}/api/dreame-product/categories/hierarchy"

    with allure.step("1.发送分类层级请求"):
        start_time=time.time()
        response=requests.get(url,headers=headers)
        elapsed_time=time.time()-start_time

    with allure.step("2.校验HTTP状态码与响应耗时"):
        assert response.status_code==200,"HTTP状态码不是200"
        assert elapsed_time<2.0,f"接口响应太慢,耗时：{elapsed_time}"

    with allure.step("3.解析响应体并进行业务断言"):
        result=response.json()
        assert result['code']==0,f"业务报错：{result.get('msg')}"
        assert result['success'] is True

    with allure.step(f"4.在数据中查找并核对路径：{check_path}"):
        data_list=result['data']
        assert len(data_list)>0,"返回的数据为空"

        found=False
        for category in data_list:
            if category['categoryPath']==check_path:
                assert category['localizationDisplayNames']['zh']==expected_zh
                found=True
                break
            for child in category.get('childCategories',[]):   #字典的get方法，“尝试去取childCategories的值,如果取不到或者值为null，就默认给一个空列表[]
                if child['categoryPath']==check_path:
                    assert child['localizationDisplayNames']['zh']==expected_zh
                    found=True
                    break
        assert found is True,f"没有在返回结果中找到路径：{check_path}"



