# import re
import ssl
import socket
import dns.resolver
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import pendulum
from typing import Dict, Any
from loguru import logger

def _is_valid_domain(domain) -> bool:
    """
    暂时不验证,没想好怎么写
    验证域名的合法性,未对含有中文的域名做验证;
    """
    resultBool = True
    # # 如果域名中含有中文,返回True
    # if re.search(r'[\u4e00-\u9fa5]', domain):
    #     return resultBool
    #
    # # 域名的正则表达式
    # domain_pattern = r'^([a-zA-Z0-9_]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    # # 编译正则表达式
    # regex = re.compile(domain_pattern)
    # # 使用 match 方法匹配域名
    # if not regex.match(domain):
    #     resultBool = False

    return resultBool

def _convert_utc_to_eastern_8(utc_time):
    """
    将日期时间字符串转换为东八区时间
    """
    # 将字符串转换为 Pendulum 对象
    utc_time = pendulum.parse(str(utc_time))

    # 将时区从 UTC 转换为东八区（北京时间）
    eastern_time = utc_time.in_timezone("Asia/Shanghai").strftime("%Y-%m-%d %H:%M:%S")

    return eastern_time

def _counting_days(after_time):
    """
    计算两个日期时间之间的天数差异
    """
    # 获取当前时间,时区为东八区
    before_time = pendulum.now('Asia/Shanghai')
    after_time = pendulum.parse(str(after_time))

    # 计算天数差异
    days_diff = after_time.diff(before_time).days
    return days_diff

def _get_domain_ip_list(domain, dns_server='114.114.114.114') -> Dict:
    """获取域名解析出的IP列表
    @param domain: 域名
    @param dns_server: DNS服务器
    """
    result = {
        'stats': False,
        'msg': '获取IP成功🍺🍺🍺🍺🍺',
        'data': []
    }
    # 默认重试次数3次
    max_retries = 3
    ip_set = set()
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [dns_server]

    for _ in range(max_retries):
        try:
            answers = resolver.resolve(domain, 'A')  # 查询A记录
            ips = {item.address for item in answers}
            ip_set.update(ips)
        except Exception as e:
            result['msg'] = f'解析域名{domain}失败了😢😢😢😢😢,{e}'
        else:
            if ip_set:
                result['stats'] = True
                result['msg'] = '获取IP成功🍺🍺🍺🍺🍺'
                result['data'] = list(ip_set)
                break

    return result


def get_cert_details(domain: str, dns_server='114.114.114.114') -> Dict[str, Any]:
    """
    获取指定域名的证书信息，并返回证书的过期时间和剩余有效天数。

    参数:
    - domain (str): 要查询证书信息的域名。
    - dns_server (str): 用于解析域名的 DNS 服务器地址，默认为 114.114.114.114。

    返回:
    - Dict[str, Any]: 包含证书信息的字典，包括证书版本、主题、颁发者、解析 IP、证书有效期等信息。
    """
    result = {
        'stats': True,
        'msg': '获取域名证书成功🍺🍺🍺🍺🍺',
        'data': ''
    }
    # 使用正则验证域名的合法性
    if not _is_valid_domain(str(domain)):
        result['stats'] = False
        result['msg'] = f'{domain}格式不合法😢😢😢😢😢'
        return result

    # 获取域名解析出的IP列表及证书
    try:
        ip_res = _get_domain_ip_list(domain, dns_server=dns_server)
        if ip_res.get('stats'):
            if len(ip_res.get('data')) > 1:
                result['data'] = ip_res.get('data')
                many_ips = ",".join(ip_res.get('data'))
                msg = f'解析{domain}存在多个ip [{many_ips}] ⚠️⚠️⚠️⚠️⚠️'
                raise Exception(msg)
        else:
            msg = ip_res.get('msg')
            raise Exception(msg)

        ip = ip_res.get('data')[0]
        try:
            # 建立连接并获取服务器证书
            with socket.create_connection((ip, 443), timeout=10) as sock: # 设置超时时间10s
                with ssl.create_default_context().wrap_socket(sock, server_hostname=domain) as ssock:
                    der_cert = ssock.getpeercert(True)
        except socket.timeout:
            msg = f'解析{domain}的ip为[{ip}],获取证书超时😢😢😢😢😢'
            raise Exception(msg)
        except Exception:
            msg = f'解析{domain}的ip为[{ip}],获取证书失败😢😢😢😢😢'
            raise Exception(msg)

        # 解析证书
        cert = x509.load_der_x509_certificate(der_cert, default_backend())

        # 计算过期剩余天数
        not_valid_before = _convert_utc_to_eastern_8(cert.not_valid_before)
        not_valid_after = _convert_utc_to_eastern_8(cert.not_valid_after)
        remaining_days = _counting_days(not_valid_after)

        result['data'] = {
            'domain': domain,
            'version': cert.version,
            'subject': cert.subject.rfc4514_string(),
            'issuer': cert.issuer.rfc4514_string(),
            'resolve_ip': ip,
            'not_valid_before': not_valid_before,
            'not_valid_after': not_valid_after,
            'expiration_days': remaining_days
        }
    except Exception as e:
        result['stats'] = False
        result['msg'] = str(e)

    return result

def get_ip_list(domain, dns_server='114.114.114.114') -> list:
    """获取域名解析出的IP列表
    @param domain: 域名
    @param dns_server: DNS服务器
    """
    max_retries = 3
    ip_set = set()
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]

    for _ in range(max_retries):
        try:
            answers = resolver.resolve(domain, 'A')  # 查询A记录
            ips = {item.address for item in answers}
            ip_set.update(ips)
        except Exception as e:
            logger.error(f'解析域名{domain}出错了，请查看: {e}')
        else:
            if ip_set:
                break

    return list(ip_set)


# if __name__ == "__main__":
#     details = get_cert_details('www.cjdropshipping.com')
#     for k,v in details['data'].items():
#         print(k,v)
# print(get_ip_list('xxx.cjdropshipping.cn'))