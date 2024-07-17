import yagmail  # pip install yagmail
import pendulum

class Mail:
    def __init__(self, host, user, password, port, smtp_ssl=False):
        self.yag = yagmail.SMTP(
            host=host,
            user=user,
            password=password,
            port=port,
            smtp_ssl=smtp_ssl
        )

    def _log(self, content):
        now_time = pendulum.now().to_time_string()
        print(f'INFO [{now_time}]: {content}')

    def send_msg_mail(self, title: str, msg: str, receivers: list):
        """
        发送纯文本邮件

        :param title: 邮件标题
        :param msg: 邮件正文
        :param receivers: 收件人列表
        """
        for receiver in receivers:
            self._log(f'开始给 {receiver} 发送邮件...')
            try:
                self.yag.send(
                    receiver,
                    title,
                    msg
                )
                self._log('发送成功!')
            except Exception as e:
                print(f"{str(e)}\nError: 发送邮件失败!")

    def send_file_mail(self, title: str, msg: str, file_path: str, receivers: list):
        """
        带有附件文件的邮件

        :param title: 邮件标题
        :param msg: 邮件正文
        :param file_path: 附件文件路径
        :param receivers: 收件人列表
        """
        for receiver in receivers:
            self._log(f'开始给 {receiver} 发送邮件...')
            try:
                self.yag.send(
                    receiver,
                    title,
                    [msg, file_path]  # 添加邮件正文和文件路径
                )
                self._log('发送成功!')
            except Exception as e:
                print(f"{str(e)}\nError: 发送邮件失败!")

