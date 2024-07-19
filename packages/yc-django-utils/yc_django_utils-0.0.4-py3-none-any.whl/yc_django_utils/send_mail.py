"""
Created on 2024/7/18 上午9:58
@author:刘飞
@description: 邮件发送功能
邮件发送功能一般比较耗时，建议使用异步或者配合其他功能使用。
c = CustomSendMail('邮件主题', '邮件内容', None, ['liufei-love@foxmail.com'])
file_list = ["文件1", "文件2"]  # 添加文件【可选】
c.send_mail(file_paths=file_list)
"""
import logging
from django.core.mail import EmailMessage
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger()


class CustomSendMail:
    def __init__(self, subject, message, from_email, recipient_list, *args, **kwargs):
        if not recipient_list:
            raise ImproperlyConfigured("收件人列表不能为空")

        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        logger.info(f'发送邮件初始化: {self.subject} from {self.from_email} to {",".join(self.recipient_list)}')

    def _send_email(self, email_obj):
        try:
            res = email_obj.send()
            logger.info(f'邮件发送结果:{res} 发送的邮件主题: {self.subject}')
            # 邮件发送结果:1 发送的邮件主题: xxx
            return res
        except Exception as e:
            logger.error(f'邮件发送失败: {e} 发送的邮件主题: {self.subject}', exc_info=True)
            return False

    def send_mail(self, file_paths: list = None):
        if not file_paths:
            file_paths = []
        # 构造邮件对象
        email = EmailMessage(
            self.subject,
            self.message,
            self.from_email,
            self.recipient_list,  # 接收方
        )
        for f in file_paths:
            email.attach_file(f)
        res = self._send_email(email)
        return res


if __name__ == '__main__':
    pass
