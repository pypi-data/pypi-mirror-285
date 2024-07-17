import os
from typing import List, Dict
from aliyun.log import LogClient, GetLogsRequest
from cryptography.fernet import Fernet

class SlsLogStore:
    def __init__(self, key=None):
        self._access_key_id, self._access_key_secret = SlsLogStore._get_access_key(key)

    @staticmethod
    def _get_access_key(key):
        encryption_account = {
            "access_key_id": 'gAAAAABmFlzfOJRPM9r8y37flIiJkM3TO6NrVdYK62cZGsqoEzymIzCZ8LbUdnkoPk5K8ibOo4GD-DPOos00B0ocaWcvkvsVfu-DtcSbxCJFkAOJVS0x9-8=',
            "access_key_secret": 'gAAAAABmFl0AY5ych1DeBtlpv2efMzqzrRaerEjOgB5H5cJKjlyWVMQ5e0KutYM7tBvHIxL3BUR1MqIqdkXY6ZF9Mpg30miCa2zKbkz2FPuQ9Z2EoiMx5vc='
        }
        if not key:
            key = os.environ.get('fernet_key')
            if not key:
                raise Exception("请先设置fernet_key")
        try:
            cipher_suite = Fernet(key.encode('utf-8'))
        except Exception as e:
            raise Exception(f"密钥格式不正确: {e}")

        access_key_id = cipher_suite.decrypt(encryption_account.get('access_key_id').encode('utf-8')).decode('utf-8')
        access_key_secret = cipher_suite.decrypt(encryption_account.get('access_key_secret').encode('utf-8')).decode('utf-8')

        return access_key_id, access_key_secret

    def _get_logs(self, tp, from_timestamp, to_timestamp, query) -> List[Dict]:
        result = []
        config = {
            "hz_log": {
                "endpoint": "cn-hangzhou.log.aliyuncs.com",
                "project_name": "hz-k8s",
                "logstore_name": "hz-k8s"
            },
            "hz_ingress": {
                "endpoint": "cn-hangzhou.log.aliyuncs.com",
                "project_name": "hz-k8s",
                "logstore_name": "nginx-ingress"
            },
            "usa_log": {
                "endpoint": "us-west-1.log.aliyuncs.com",
                "project_name": "usa-k8s",
                "logstore_name": "usa-log"
            },
            "usa_ingress": {
                "endpoint": "us-west-1.log.aliyuncs.com",
                "project_name": "usa-k8s",
                "logstore_name": "usa-ingress"
            }
        }
        endpoint, project_name, logstore_name = config.get(tp).values()
        client = LogClient(endpoint, self._access_key_id, self._access_key_secret)
        request = GetLogsRequest(project_name, logstore_name, from_timestamp, to_timestamp, query=query) # 指定获取所有日志数量
        response = client.get_logs(request)
        for log in response.get_logs():
            result.append(dict(log.contents))
        return result

    def _sls_config_res(self, tp, from_timestamp, to_timestamp, query) -> List[Dict]:
        try:
            result = self._get_logs(tp, from_timestamp, to_timestamp, query)
        except Exception as e:
            raise Exception(f"查询 {tp} 日志失败: {e}")
        return result

    def hz_ingress_log(self, from_timestamp, to_timestamp, query) -> List[Dict]:
        """
        查询杭州的ingress日志; 注意!!!!!!!!!!! 返回最大日志记录数为100条
        @param from_timestamp: 开始时间戳
        @param to_timestamp: 结束时间戳
        @param query: 查询条件
        @return: 查询结果(List类型)
        """
        return self._sls_config_res('hz_ingress', from_timestamp, to_timestamp, query)

    def hz_service_log(self, from_timestamp, to_timestamp, query) -> List[Dict]:
        """
        查询杭州的服务日志; 注意!!!!!!!!!!! 返回最大日志记录数为100条
        @param from_timestamp: 开始时间戳
        @param to_timestamp: 结束时间戳
        @param query: 查询条件
        @return: 查询结果(List类型)
        """
        return self._sls_config_res('hz_log', from_timestamp, to_timestamp, query)

    def usa_ingress_log(self, from_timestamp, to_timestamp, query) -> List[Dict]:
        """
        查询美国的ingress日志; 注意!!!!!!!!!!! 返回最大日志记录数为100条
        @param from_timestamp: 开始时间戳
        @param to_timestamp: 结束时间戳
        @param query: 查询条件
        @return: 查询结果(List类型)
        """
        return self._sls_config_res('usa_ingress', from_timestamp, to_timestamp, query)

    def usa_service_log(self, from_timestamp, to_timestamp, query) -> List[Dict]:
        """
        查询美国的服务日志;注意!!!!!!!!!!! 返回最大日志记录数为100条
        @param from_timestamp: 开始时间戳
        @param to_timestamp: 结束时间戳
        @param query: 查询条件
        @return: 查询结果(List类型)
        """
        return self._sls_config_res('usa_log', from_timestamp, to_timestamp, query)
