# 工具集

## aliyun
阿里云相关功能方法 SlsLogStore(key) 实例化
> 1.杭州ingress日志查询方法  hz_ingress_log
> 1.杭州service日志查询方法  hz_service_log
> 2.硅谷ingress日志查询方法  usa_ingress_log
> 2.硅谷service日志查询方法  usa_service_log

## excel
excel相关功能方法
> 1.将字典列表写入到excel文件中 write_list_dict_excel
> 2.将列表元组写入到excel文件中 write_list_tuple_excel

## qw
企业微信
> 1.markdown格式的企业微信通知 send_markdown_message

## command
subprocess执行shell命令
> 1.通过subprocess执行shell命令 exec_command
> 2.通过subprocess执行shell命令支持实时输出 exec_command_realtime_output

## domain
域名相关功能方法
> 1.获取域名解析的IP地址 get_ip_list
> 2.获取域名解析的证书及过期天数 get_cert_details

## sql
执行mysql相关的sql
> 1.执行sql exec_mysql

## email
发送邮件 Mail(host, user, password, port, ssl)初始化
> 1.发送文本邮件 send_msg_mail(title: str, msg: str, receivers: list)
> 2.发送带有附件邮件 send_file_mail(title: str, msg: str, file_path: str, receivers: list)

## csv
csv相关功能方法
> 1.将数据写入到csv中 write_csv

## thread
线程相关功能方法
> 1.多线程运行任务 run_multithreaded

## utils
工具箱
> 1.md5加密 md5_encrypt
> 2.base64编码 base64_encode
> 3.base64解码 base64_decode
> 4.生成随机Fernet密钥 fernet_generate_key
> 4.使用fernet加密数据 fernet_jiami
> 4.使用fernet解密数据 fernet_jiemi
> 5.进度条 process_with_progress
> 6.复制数据到粘贴板  copy_to_clipboard
