import smtplib
from email.mime.text import MIMEText


def send(smtp_host: str, smtp_port: int, smtp_user: str, smtp_pwd: str, sender: str, to: str, subject: str, body: str):
    """
    发送邮件, 本工具不支持代理
    :param smtp_host: SMTP 服务器地址
    :param smtp_port: SMTP 服务器端口
    :param smtp_user: SMTP 用户名
    :param smtp_pwd: SMTP 密码
    :param sender: 发件人邮箱地址
    :param to: 收件人邮箱地址
    :param subject: 邮件主题
    :param body: 邮件内容
    """
    # 连接 SMTP 服务器并发送邮件
    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()  # 使用 TLS 加密 (如果使用 465 端口则不需要此行)
        smtp.login(smtp_user, smtp_pwd)

        # 创建 MIMEText 对象
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to
        smtp.send_message(msg)

