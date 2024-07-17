from common.common.api_driver import APIDriver
from common.plugin.data_bus import DataBus
from loguru import logger
from common.autotest.handle_allure import allure_step
from common.common.constant import Constant
from common.data.data_process import DataProcess
from common.data.handle_common import convert_json_bank,req_expr
from common.data.handle_common import extractor, get_system_key, set_system_key
from common.file.ReadFile import ReadFile, get_yaml_ApiSchemal,get_yaml_config
from common.plat.mysql_platform import MysqlPlatForm
from common.autotest.handle_assert import *


class BaseRequest(APIDriver):

    @classmethod
    def send_request(cls, case: dict, host: str = 'host', datatype: str='json') -> object:
        """处理case数据，转换成可用数据发送请求，针对单接口
        :param case: 读取出来的每一行用例内容，可进行解包
        :param env: 环境名称 默认使用config.yaml server下的 dev 后面的基准地址
        return: 响应结果， 预期结果
        """
        DataBus.save_init_data()
        case_number = DataProcess.get_key_dic(case, Constant.CASE_NO)
        path = DataProcess.get_key_dic(case, "接口地址")
        if DataProcess.get_key_dic(case, Constant.CASE_DATA_PARAM) != None:
            parametric_key = DataProcess.get_key_dic(case, Constant.CASE_DATA_PARAM)
        else:
            parametric_key = DataProcess.get_key_dic(case, "入参关键字")
        if DataProcess.get_key_dic(case, Constant.CASE_DATA_HEADER) != None:
            token = DataProcess.get_key_dic(case, Constant.CASE_DATA_HEADER)
        else:
            token = DataProcess.get_key_dic(case, "token操作")
        if DataProcess.get_key_dic(case, Constant.CASE_DATA_TYPE) != None:
            datatype = DataProcess.get_key_dic(case, Constant.CASE_DATA_TYPE)
        method = DataProcess.get_key_dic(case, Constant.CASE_DATA_METHOD)
        file_obj = DataProcess.get_key_dic(case, "上传文件")
        data = DataProcess.get_key_dic(case, Constant.CASE_DATA)
        sql = DataProcess.get_key_dic(case, "后置sql")
        expect = DataProcess.get_key_dic(case, Constant.CASE_EXPECTED)
        is_save = DataProcess.get_key_dic(case, "保存响应")
        url = DataProcess.handle_path(path)
        if url.find("http") == -1:
            url = str(get_system_key(host)) + str(DataProcess.handle_path(path))
        cls._convert_url(url)
        header = DataProcess.handle_header(token)
        try:
            if datatype == 'json':
                data = DataProcess.handle_data(data)
            else:
                data = DataProcess.handle_data(data, False)
        except Exception as e:
            logger.info(f'测试数据：{data} 转换异常:' + repr(e))
        file = DataProcess.handler_files(file_obj)
        desc = f'测试接口详情:{url}'
        # 发送请求
        res = cls.http_request(url=url, method=method, parametric_key=parametric_key,
                               header=header, data=data, file=file, desc=desc)
        try:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                MysqlPlatForm.insert_api_data(url, method, header, data, res.elapsed.total_seconds(), res.status_code)
        except:
            logger.warning("保存请求数据异常")
        # 响应后操作
        if token == '写':
            DataProcess.have_token['Authorization'] = extractor(res.json(), ReadFile.get_config_value('$.expr.token'))
            allure_step('请求头中添加Token', DataProcess.have_token)
        # 保存用例的实际响应
        if is_save == "yes":
            DataProcess.save_response(case_number, res.json())
        try:
            return res.json(), expect, res
        except:
            return res.text, expect, res

    @classmethod
    def api_exec(self, schemal_key, data=None, header=None, file=None, cookie=None, host: str = 'host', datatype: str='json', step:str='测试接口详情', _replace:int=0, assert_data=None) -> object:
        """处理case数据，转换成可用数据发送请求
        :param case: 读取出来的每一行用例内容，可进行解包
        :param env: 环境名称 默认使用config.yaml server下的 dev 后面的基准地址
        return: 响应结果， 预期结果
        """
        DataBus.save_init_data()
        temp = data
        schemal_data = get_yaml_ApiSchemal(schemal_key)
        url = DataProcess.handle_path(schemal_data['url'])
        if url.find("http") == -1:
            url = get_system_key(host) + DataProcess.handle_path(url)
        self._convert_url(url)
        if 'header' in schemal_data:
            header = DataProcess.handle_header(schemal_data['header'])
        else:
            if isinstance(header, str):
                header = DataProcess.handle_header(header, data)
            elif header is None:
                header = DataProcess.handle_header(schemal_data['datatype'], data)
            else:
                header = DataProcess.handle_header(header, data)
        try:
            if schemal_data['datatype'] == 'json' or schemal_data['datatype'] == 'params':
                if 'body' in schemal_data:
                    schemal_body = ReadFile.get_yaml_ApiSchemal(schemal_key)
                    content = schemal_body['body']
                    if isinstance(content,dict):
                        if 'file' in content:
                            from common.plugin.file_plugin import FilePlugin
                            content = FilePlugin.load_data(content['file'])
                    data = convert_json_bank(content, data)
                data = DataProcess.handle_data(variable=data, _replace=_replace)
            else:
                if 'body' in schemal_data:
                    schemal_body = ReadFile.get_yaml_ApiSchemal(schemal_key)
                    content = schemal_body['body']
                    if isinstance(content,dict):
                        if 'file' in content:
                            from common.plugin.file_plugin import FilePlugin
                            content = FilePlugin.load_data(content['file'])
                    data = req_expr(content=content, data=data, _no_content=0)
            if 'datatype' in schemal_data:
                datatype = schemal_data['datatype']
            if 'format' in schemal_data:
                datatype = schemal_data['format']
            data = BaseRequest.handle_body(data, datatype,_replace)
        except Exception as e:
            data = data
        if 'file' in schemal_data and file is None:
            file = schemal_body['file']
        file_obj = DataProcess.handler_files(file)
        if step == '测试接口详情' and DataProcess.isNotNull(schemal_data['desc']):
            step = '测试接口详情:'+schemal_data['desc']
        res = self.http_request(url=url, method=schemal_data['method'], parametric_key=schemal_data['datatype'],
                               header=header, data=data, file=file_obj, cookie=cookie, desc=step)
        if 'assert' in schemal_data:
            if isinstance(temp,dict) and temp is not None:
                schemal_body = ReadFile.get_yaml_ApiSchemal(schemal_key)
                assertData = schemal_body['assert']
                _assert = convert_json_bank(assertData, temp)
            elif isinstance(assert_data,dict) and assert_data is not  None:
                schemal_body = ReadFile.get_yaml_ApiSchemal(schemal_key)
                assertData = schemal_body['assert']
                _assert = convert_json_bank(assertData, assert_data)
            elif isinstance(assert_data,str) and DataProcess.isNotNull(assert_data):
                _assert = assert_data
            else:
                _assert = schemal_data['assert']

            if str(_assert).find('*ResCode') >= 0:
                assert_response(res, _assert)
            else:
                if DataProcess.isNotNull(get_system_key(Constant.RESPONSE_CODE)):
                    ex_status_code = get_system_key(Constant.RESPONSE_CODE)
                    allure_step(f'返回结果检查【状态码】', f'实际状态码: {res.status_code}小于 预期状态码:{ex_status_code}')
                    assert res.status_code <= int(ex_status_code)
                assert_response(res, _assert)
        else:
            if DataProcess.isNotNull(get_system_key(Constant.RESPONSE_CODE)):
                ex_status_code = get_system_key(Constant.RESPONSE_CODE)
                allure_step(f'状态码检查', f'实际状态码: {res.status_code}小于{ex_status_code}')
                assert res.status_code <= int(ex_status_code)
        if 'data' in schemal_data:
            databus = schemal_data['data']
            DataProcess.get_response_jpath(res, databus, schemal_key)
        try:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                MysqlPlatForm.insert_api_data(url, schemal_data['method'], header, data, res.elapsed.total_seconds(), res.status_code)
        except:
            logger.warning("保存请求数据异常")
        return res


    @classmethod
    def handle_body(self, data, format, _replace):
        test_data = data
        try:
            if format == 'json':
                test_data = DataProcess.handle_data(variable=data, _replace=_replace)
            elif format == 'None':
                test_data = data
            else:
                test_data = DataProcess.handle_data(variable=data, jsonformat=False, _replace=_replace)
            return test_data
        except Exception as e:
            test_data = data
            return test_data


    @classmethod
    def api_request(self, schemal_key, data=None, header=None, file=None, cookie=None, step: str = '测试接口详情') -> object:
        """处理case数据，转换成可用数据发送请求
        :param case: 读取出来的每一行用例内容，可进行解包
        :param env: 环境名称 默认使用config.yaml server下的 dev 后面的基准地址
        return: 响应结果， 预期结果
        """
        DataBus.save_init_data()
        schemal_data = get_yaml_ApiSchemal(schemal_key)
        url = DataProcess.handle_path(schemal_data['url'])
        file_obj = DataProcess.handler_files(file)
        if step == '测试接口详情' and DataProcess.isNotNull(schemal_data['desc']):
            step = '测试接口详情:' + schemal_data['desc']
        res = self.http_request(url=url, method=schemal_data['method'], parametric_key=schemal_data['datatype'],
                               header=header, data=data, file=file_obj, cookie=cookie,
                               desc=step)
        try:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                MysqlPlatForm.insert_api_data(url, schemal_data['method'], header, data, res.elapsed.total_seconds(),
                                              res.status_code)
        except:
            logger.warning("保存请求数据异常")
        return res

    @classmethod
    def request(self, url, method, parametric_key=None, header=None, data=None, file=None, cookie=None,  datatype: str='json',desc: str = '测试接口详情'):
        DataBus.save_init_data()
        try:
            if datatype == 'json':
                data = DataProcess.handle_data(data)
            else:
                data = DataProcess.handle_data(data, False)
        except Exception as e:
            logger.info(f'测试数据：{data} 转换异常:' + repr(e))
        file_obj = DataProcess.handler_files(file)
        res = self.http_request(url=DataProcess.handle_path(url), method=method, parametric_key=parametric_key,
                               header=DataProcess.setDictEncode(DataProcess.handle_header(header)), data=data,
                               file=file_obj, cookie=cookie,desc=desc)
        try:
            if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)):
                MysqlPlatForm.insert_api_data(url, method, header, data, res.elapsed.total_seconds(),
                                              res.status_code)
        except:
            logger.warning("保存请求数据异常")
        return res


    @classmethod
    def _convert_url(self,url):
        _url = url.replace("//", '####').split('/')
        _newurl = '';
        for i in range(len(_url)):
            if _url[i].find(Constant.DATA_NO_CONTENT) == -1:
                _newurl = _newurl + _url[i] + '/'
        _newurl = _newurl.replace("//", "/").replace("####", "//")
        return _newurl












