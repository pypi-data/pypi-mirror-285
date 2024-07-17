def _request_get():
    """
    返回request GET请求模板
    """
    msg = """
import requests
url = 'https://movie.douban.com/j/chart/top_list'
params = {
    'type': '5',
    'interval_id': '100:90',
    'action': '',
    'start': '10',
    'limit': '50',
}
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}
response = requests.get(url=url,params=params,headers=headers)
page_text =  response.json()

for movie in page_text:
    name = movie['title']
    score = movie['score']
    print(name,score)
    """
    return msg

request_get = _request_get()