import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def get_lottery_type():
    """判断今日开奖类型"""
    today = datetime.now().weekday()
    if today in [0, 2, 5]:  # 周一、三、六
        return "大乐透"
    else:
        return "双色球"

def get_lottery_result(lottery_type):
    """获取开奖结果"""
    try:
        if lottery_type == "大乐透":
            url = "https://www.lottery.gov.cn/kj/kjlb.html?dlt"
        else:
            url = "https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/"
            
        response = requests.get(url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取最新一期开奖号码
        if lottery_type == "大乐透":
            latest_draw = soup.find('div', class_='kjjg')
        else:
            # 双色球开奖结果在表格中
            latest_draw = soup.find('table', class_='table-bordered')
            if latest_draw:
                # 获取第一行数据（最新一期）
                first_row = latest_draw.find('tr', class_='t_tr1')
                if first_row:
                    numbers = ' '.join([td.text.strip() for td in first_row.find_all('td')])
                    return numbers
                return None
            return None
            
        if latest_draw:
            numbers = latest_draw.text.strip()
            return numbers
        return None
    except Exception as e:
        print(f"获取开奖结果失败: {str(e)}")
        return None

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
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")

def main():
    lottery_type = get_lottery_type()
    result = get_lottery_result(lottery_type)
    
    if result:
        subject = f"今日{lottery_type}开奖结果"
        content = f"""
        您好！

        今日{lottery_type}开奖结果：
        {result}

        祝您中奖！
        """
    else:
        subject = f"今日{lottery_type}开奖结果获取失败"
        content = f"""
        您好！

        很抱歉，今日{lottery_type}开奖结果获取失败。
        请手动查看开奖结果。

        祝您中奖！
        """
    
    send_email(subject, content)

if __name__ == "__main__":
    main() 