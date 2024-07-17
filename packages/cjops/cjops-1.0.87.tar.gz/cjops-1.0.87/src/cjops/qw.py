import requests

def send_markdown_message(token, content) -> bool:
    """
    发送markdown格式的企业微信通知
    @param token: 企业微信的token
    @param content: 通知内容
    @return: bool
    # TODO 功能完善，支持不同的数据类型 不同颜色 超过4096提示支持分成多条消息 @指定的人
    """
    resultBool = True
    if not token:
        raise Exception("你必须传入token的值")
    if not content:
        raise Exception("你必须传入content的值")

    url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={token}'
    headers = {"Content-Type": "application/json; charset=utf-8"}
    # logger.info(f'获取的发信内容: {content}')
    send_data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    req = requests.post(url, json=send_data, headers=headers)
    result = req.json()
    if result['errcode'] != 0:
        resultBool = False
    return resultBool
