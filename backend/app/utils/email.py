import time
import random
import smtplib
import traceback
from functools import partial
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.app.core.config import settings

def generate_otp_html_template(app_name, otp_code, expiration_minutes=5):
    """
    生成HTML格式的验证码邮件

    :param app_name: 应用名称
    :param otp_code: 验证码
    :param expiration_minutes: 验证码有效期(分钟)
    :return: HTML格式邮件内容
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 30px;
                background-color: #f9f9f9;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .logo {{
                font-size: 24px;
                font-weight: bold;
                color: #0066cc;
            }}
            .otp-container {{
                text-align: center;
                margin: 25px 0;
            }}
            .otp-code {{
                display: inline-block;
                background-color: #0066cc;
                color: white;
                font-size: 28px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                letter-spacing: 5px;
                margin: 10px 0;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #777;
                text-align: center;
            }}
            .warning {{
                background-color: #fff8e6;
                border-left: 4px solid #ffc107;
                padding: 10px;
                margin: 15px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">{app_name}</div>
                <h2>邮箱验证码</h2>
            </div>

            <p>您好！</p>

            <p>您的验证码已生成，请在 {expiration_minutes} 分钟内完成验证：</p>

            <div class="otp-container">
                <div class="otp-code">{otp_code}</div>
            </div>

            <div class="warning">
                温馨提示：请勿将验证码泄露给他人，{app_name} 工作人员不会向您索要验证码。
            </div>

            <p>如非本人操作，请忽略此邮件。</p>

            <div class="footer">
                <p>© {app_name} 团队 | {time.strftime("%Y年%m月%d日")}</p>
                <p>此邮件为系统自动发送，请勿直接回复</p>
            </div>
        </div>
    </body>
    </html>
    """

def send_otp_email(sender, password, receiver, app_name=settings.APP_NAME):
    """
    发送验证码邮件

    :param sender: 发件人邮箱
    :param password: 邮箱授权码
    :param receiver: 收件人邮箱
    :param app_name: 应用名称
    :return: (验证码, 是否成功)
    """
    # 生成6位随机验证码
    otp_code = str(random.randint(100000, 999999))
    expiration_minutes = 5

    # 创建邮件
    message = MIMEMultipart()
    message['From'] = f"{app_name} <{sender}>"
    message['To'] = receiver
    message['Subject'] = f"{app_name} 验证码"

    # 添加HTML内容
    html_content = generate_otp_html_template(app_name, otp_code, expiration_minutes)
    message.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        # 连接SMTP服务器 (这里以QQ邮箱为例)
        server = smtplib.SMTP("smtp.qq.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
        print(f"验证码邮件已发送至 {receiver}")
        return otp_code, True
    except Exception as e:
        print(f"发送验证码邮件失败: {traceback.format_exc()}")
        return None, False
    finally:
        server.quit()


send_email = partial(send_otp_email, settings.SENDER_EMAIL, settings.SENDER_PASSWORD)


# 使用示例
if __name__ == "__main__":
    receiver_email = "13102180531@163.com"

    otp, success = send_otp_email(settings.SENDER_EMAIL, settings.SENDER_PASSWORD, receiver_email)

    if success:
        print(f"生成的验证码: {otp}")
        # 这里可以将验证码保存到数据库或缓存中，用于后续验证
        # 例如: cache.set(f"otp:{receiver_email}", otp, expire=300)

