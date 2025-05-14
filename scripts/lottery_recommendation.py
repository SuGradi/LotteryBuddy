import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_lottery_type():
    """判断今日开奖类型"""
    today = datetime.now().weekday()
    # 大乐透：周一、三、六开奖
    # 双色球：周二、四、日开奖
    if today in [0, 2, 5]:  # 周一、三、六
        return "大乐透"
    else:
        return "双色球"

def generate_numbers(lottery_type):
    """生成推荐号码"""
    if lottery_type == "大乐透":
        # 前区5个号码(1-35)，后区2个号码(1-12)
        front_numbers = sorted(random.sample(range(1, 36), 5))
        back_numbers = sorted(random.sample(range(1, 13), 2))
        return f"前区：{', '.join(map(str, front_numbers))}，后区：{', '.join(map(str, back_numbers))}"
    else:
        # 双色球：6个红球(1-33)，1个蓝球(1-16)
        red_numbers = sorted(random.sample(range(1, 34), 6))
        blue_number = random.randint(1, 16)
        return f"红球：{', '.join(map(str, red_numbers))}，蓝球：{blue_number}"

def send_email(subject, content):
    """发送邮件"""
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(content, 'plain'))

    try:
        # 使用QQ邮箱的SMTP服务器
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")

def main():
    lottery_type = get_lottery_type()
    numbers = generate_numbers(lottery_type)
    
    subject = f"今日{lottery_type}推荐号码"
    content = f"""
    您好！

    今日{lottery_type}推荐号码：
    {numbers}

    祝您好运！
    """
    
    send_email(subject, content)

if __name__ == "__main__":
    main() 