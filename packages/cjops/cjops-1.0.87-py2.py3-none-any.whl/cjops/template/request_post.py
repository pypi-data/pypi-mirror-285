def _request_post():
    """
    返回request POST请求模板
    """
    msg = """
import requests
import simplejson

url = 'http://127.0.0.1:8080/updateTopic'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8'
}
data = {
    "clusterNameList": None,
    "brokerNameList": ["broker-a"],
    "writeQueueNums": "20",
    "readQueueNums": "20",
    "perm": 6,
    "order": False
}
result = requests.post(url=url, headers=headers, data=simplejson.dumps(data))
if result.status_code == 200:
    print(f'{topic} 的数值更新成功')
else:
    print(f'{topic} 的数值更新失败')
    """
    return msg

request_post = _request_post()