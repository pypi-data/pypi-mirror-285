import copy
import requests
from dzwl.fun_util import fun_util,DateEncoder
import os
import yaml
from string import Template
import json
from Config.config import CommonConfig
import pytest

class requsts_util:
    session = requests.session()
    @classmethod
    def send_request(self,method,url,data,headers,**kwargs):
        method = str(method).lower()
        try:
            if method == 'get':
                rep = requsts_util.session.request(method=method, url=url, params=data,headers = headers,**kwargs)
            elif method == 'delete':
                rep = requsts_util.session.delete(url=url, params=data,headers = headers,**kwargs)
            else:
                if 'form' in str(headers):
                    rep = requsts_util.session.request(method=method, url=url, data=data,headers= headers, **kwargs)
                else:
                    rep = requsts_util.session.request(method=method, url=url, json=data,headers= headers, **kwargs)
        except Exception as e:
            print('无法连接:'+str(e))
        else:
            if rep.status_code==200:
                resp = json.loads(rep.text)
                return resp
            else:
                print('请求状态异常：'+str(rep.status_code))

    @classmethod
    def excute_interface(self,caseinfo,domain):
        #循环读取yml中配置的接口参数
            #caseinfo是个dic，通过caseinfo.keys()获取key，使用list()转为list类型，取下标0即可，yml测试数据的动态管理
            #caseinfo_key = list(caseinfo.keys())[0]
            #从config文件中读取domain与接口地址拼接,login接口可能用别的域名，判断一下
            url = domain + caseinfo['path']
            #读取请求类型
            method = caseinfo['method']
            #读取请求数据
            data = caseinfo['data']
            #读取请求头
            headers = caseinfo['headers']
            #读取描述
            description = caseinfo['description']
            #发送请求
            resp = self.send_request(method=method,url=url,data=data,headers=headers)
            print('\n')
            fun_util.logView('描述：'+description)
            fun_util.logView('请求url：'+url)
            fun_util.logView('请求header：'+json.dumps(headers,indent = 4,ensure_ascii=False))
            fun_util.logView('请求body：'+json.dumps(data,indent = 4,ensure_ascii=False,cls=DateEncoder))
            fun_util.logView('返回：'+json.dumps(resp,indent = 4,ensure_ascii=False))
            if 'assert_type' in caseinfo and 'is_assert' in caseinfo:
                # 读取断言类型
                assert_type = caseinfo['assert_type']
                # 读取断言信息
                is_assert = caseinfo['is_assert']
                requsts_util.check_assert(is_assert,resp,assert_type)
            return resp

    @staticmethod
    def check_assert(expected, result, type):
        fun_util.logView('-------------------------------------------------------------------------------------')
        fun_util.logView('断言期望内容：' + json.dumps(expected, indent=4, ensure_ascii=False) + '；断言模式：' + type)
        if result != None:
            if expected == None:
                fun_util.logView('断言结果：无须断言')
                pytest.assume(True)
                return True
            else:
                if type == 'and':
                    for expected_key, expected_value in expected.items():
                        # 取出的键值拼装新的单个字典
                        dic = dict.fromkeys([expected_key], expected_value)
                        # 字典转为字符串，并截取dic的花括号
                        dic = str(dic)
                        # 截取去除花括号
                        dic = dic[1:len(dic) - 1]
                        result = str(result)
                        if dic in result:
                            continue
                        if dic not in result:
                            fun_util.logView('断言结果：断言失败')
                            pytest.assume(False)
                            return False
                    fun_util.logView('断言结果：断言成功')
                    pytest.assume(True)
                    return True
                if type == 'or':
                    for expected_key, expected_value in expected.items():
                        # 取出的键值拼装新的单个字典
                        dic = dict.fromkeys([expected_key], expected_value)
                        # 字典转为字符串，并截取dic的花括号
                        dic = str(dic)
                        # 截取去除花括号
                        dic = dic[1:len(dic) - 1]
                        result = str(result)
                        if dic in result:
                            fun_util.logView('断言结果：断言成功')
                            pytest.assume(True)
                            return True
                        if dic not in result:
                            continue
                    fun_util.logView('断言结果：断言失败')
                    pytest.assume(False)
                    return False
                if type == 'not_and':
                    for expected_key, expected_value in expected.items():
                        # 取出的键值拼装新的单个字典
                        dic = dict.fromkeys([expected_key], expected_value)
                        # 字典转为字符串，并截取dic的花括号
                        dic = str(dic)
                        # 截取去除花括号
                        dic = dic[1:len(dic) - 1]
                        result = str(result)
                        # print(str(dic),str(result))
                        if dic not in result:
                            continue
                        if dic in result:
                            fun_util.logView('断言结果：断言失败')
                            pytest.assume(False)
                            return False
                    fun_util.logView('断言结果：断言成功')
                    pytest.assume(True)
                    return True
                if type == 'not_or':
                    for expected_key, expected_value in expected.items():
                        # 取出的键值拼装新的单个字典
                        dic = dict.fromkeys([expected_key], expected_value)
                        # 字典转为字符串，并截取dic的花括号
                        dic = str(dic)
                        # 截取去除花括号
                        dic = dic[1:len(dic) - 1]
                        result = str(result)
                        if dic not in result:
                            fun_util.logView('断言结果：断言成功')
                            pytest.assume(True)
                            return True
                        if dic in result:
                            continue
                    fun_util.logView('断言结果：断言失败')
                    pytest.assume(False)
                    return False
        else:
            pytest.assume(False)
            return False
            print('接口返回为空')

class yaml_util:
    rootPath = CommonConfig.rootPath
    # 读取common_var.yml文件
    @classmethod
    def read_extract_yaml(self, key, file_path=rootPath + "/Common/common_var.yml"):
        with open(file_path, mode='r', encoding='utf-8') as f:
            value = yaml.load(stream=f, Loader=yaml.FullLoader)
            if value == None:
                return None
            else:
                for kk in value:
                    if key == kk:
                        if value == None:
                            return None
                        else:
                            return value[key];
                    else:
                        continue
                    return None

    # 写入common_var.yml文件
    @classmethod
    def write_extract_yaml(self,data,file_path = rootPath + "/Common/common_var.yml"):
        # 获取文件所在的目录路径
        dir_path = os.path.dirname(file_path)
        # 检查目录是否存在，如果不存在则创建目录
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 读取文件中的所有数据
        with open(file_path, mode='r', encoding='utf-8') as f:
            all_data = yaml.safe_load(f) or {}
        # 将传入的数据转换为字典格式，并更新到all_data中
        for d in data:
            for key_data in d.keys():
                if key_data in all_data:
                    all_data[key_data]=d[key_data]
                else:
                    all_data.update(d)
        # 将所有数据写入文件中
        with open(file_path, mode='w', encoding='utf-8') as f:
            yaml.dump(data=all_data, stream=f, allow_unicode=True)
    #旧
    # @classmethod
    # def write_extract_yaml(self,data):
    #     file_path = os.path.join(self.rootPath, "Common", "common_var.yml")
    #
    #     # 读取文件中的所有数据
    #     with open(file_path, mode='r', encoding='utf-8') as f:
    #         all_data = yaml.safe_load(f) or {}
    #     # 将传入的数据转换为字典格式，并更新到all_data中
    #     for d in data:
    #         for key_data in d.keys():
    #             if key_data in all_data:
    #                 all_data[key_data]=d[key_data]
    #             else:
    #                 all_data.update(d)
    #     # 将所有数据写入文件中
    #     with open(file_path, mode='w', encoding='utf-8') as f:
    #         yaml.dump(data=all_data, stream=f, allow_unicode=True)


    # 清除common_var.yml文件
    @classmethod
    def clean_extract_yaml(self) :
        with open(self.rootPath+"/Common/common_var.yml",mode='w',encoding='utf-8') as f:
            f.truncate()

    #读取测试用例的yml文件
    @classmethod
    def read_testcase_yaml(self,yaml_name):
        with open(self.rootPath+yaml_name,mode='r',encoding='utf-8') as f:
            value = yaml.load(stream=f,Loader=yaml.FullLoader)
            return value;

    #写入测试用例的yml文件
    @classmethod
    def write_testcase_yaml(self,caseinfo,content) :
        def toDict(caseinfo_tmp,new_key,new_value):
            #值为list时
            if isinstance(caseinfo_tmp, list):
                for caseinfo_tmp_value in caseinfo_tmp:
                    toDict(caseinfo_tmp_value, new_key, new_value)
            #值为dict时
            if isinstance(caseinfo_tmp, dict):
                for caseinfo_tmp_key, caseinfo_tmp_value in caseinfo_tmp.items():
                    #判断是否有请求内容，没有跳过
                    if caseinfo_tmp_value!=None:
                        #判断模板中字段值是否有下一级，没有进行替换值
                        if isinstance(caseinfo_tmp_value, str):
                            #判断匹配
                            if '${' + new_key + '}' in caseinfo_tmp_value:
                                #全部替换
                                if '${' + new_key + '}' == caseinfo_tmp_value:
                                    caseinfo_tmp[caseinfo_tmp_key] = new_value
                                #模糊替换
                                else:
                                    caseinfo_tmp[caseinfo_tmp_key] = caseinfo_tmp[caseinfo_tmp_key].replace('${' + new_key + '}',new_value)
                        #子字段值为嵌套dict
                        if isinstance(caseinfo_tmp_value, dict):
                            toDict(caseinfo_tmp_value,new_key,new_value)
                        #子字段值为list
                        if isinstance(caseinfo_tmp_value, list):
                            toDict(caseinfo_tmp_value, new_key, new_value)

                    else:
                        continue
        #拿到模板dict
        caseinfo_tmp = copy.deepcopy(caseinfo)
        # 从参数list获取每个要替换的字段dict
        for cont in content:
            #获取每个字段与对应值
            for new_key,new_value in cont.items():
                    toDict(caseinfo_tmp,new_key,new_value)
        return  caseinfo_tmp

    #测试用例文件移除特定字段
    @classmethod
    def remove_testcase_yaml(self,caseinfo,content) :
        caseinfo_tmp = copy.deepcopy(caseinfo)

        def remove_name_items(dictionary,cont):
            new_dictionary = {}
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    new_dictionary[key] = remove_name_items(value,cont)
                elif key != cont:
                    new_dictionary[key] = value
            return new_dictionary

        for cont in content:
            caseinfo_tmp = remove_name_items(caseinfo_tmp, cont)
        return caseinfo_tmp

    @classmethod
    #添加测试用例中的键值对
    def test_add_testcase_yaml(self,caseinfo,caseinfo_key,caseinfo_value):
        #使用示例：移除data下name键值对
        #remove_testcase_yaml(caseinfo['data']['name'])
        caseinfo_tmp = copy.deepcopy(caseinfo)
        caseinfo_key = caseinfo_value
        return caseinfo_tmp

    @classmethod
    #移除测试用例中的键值对
    def test_remove_testcase_yaml(self,caseinfo,caseinfo_key):
        #使用示例：移除data下name键值对
        #remove_testcase_yaml(caseinfo['data']['name'])
        caseinfo_tmp = copy.deepcopy(caseinfo)
        del caseinfo_key
        return caseinfo_tmp

