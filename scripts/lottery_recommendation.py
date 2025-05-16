import os
import random
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from email.header import Header
from email.utils import formataddr
from history_analyze import fetch_dlt_history, fetch_ssq_history, analyze_hot_cold

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
        # 获取历史数据并分析
        front_all, back_all = fetch_dlt_history(100)
        hot_f, cold_f, rec_f = analyze_hot_cold(front_all, 3, 2, 5)
        hot_b, cold_b, rec_b = analyze_hot_cold(back_all, 1, 1, 2)
        
        # 使用分析结果生成号码
        front_numbers = rec_f
        back_numbers = rec_b
        return f"前区：{', '.join(map(str, front_numbers))}，后区：{', '.join(map(str, back_numbers))}", {
            'hot_front': hot_f,
            'cold_front': cold_f,
            'hot_back': hot_b,
            'cold_back': cold_b
        }
    else:
        # 获取历史数据并分析
        red_all, blue_all = fetch_ssq_history(100)
        hot_r, cold_r, rec_r = analyze_hot_cold(red_all, 4, 2, 6)
        hot_b, cold_b, rec_b = analyze_hot_cold(blue_all, 1, 0, 1)
        
        # 使用分析结果生成号码
        red_numbers = rec_r
        blue_number = rec_b[0] if rec_b else random.randint(1, 16)
        return f"红球：{', '.join(map(str, red_numbers))}，蓝球：{blue_number}", {
            'hot_red': hot_r,
            'cold_red': cold_r,
            'hot_blue': hot_b,
            'cold_blue': cold_b
        }

def send_email(subject, content):
    """发送邮件"""
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header('【来彩助手】', 'utf-8')), email_user))
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

def save_recommended_numbers(lottery_type, numbers, analysis):
    """保存推荐号码到文件和环境变量"""
    today = datetime.now()
    month = today.strftime('%Y-%m')
    data = {
        'date': today.strftime('%Y-%m-%d'),
        'lottery_type': lottery_type,
        'numbers': numbers,
        'analysis': analysis
    }
    
    # 保存到环境变量
    os.environ['RECOMMENDED_NUMBERS'] = json.dumps(data, ensure_ascii=False)
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 按月保存到文件（作为备份）
    filename = f'data/recommended_numbers_{month}.json'
    
    # 读取现有数据（如果存在）
    existing_data = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = {}
    
    # 更新当天的数据
    existing_data[today.strftime('%Y-%m-%d')] = data
    
    # 保存更新后的数据
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    print(f"推荐号码已保存到 {filename}")

def get_recommended_numbers(lottery_type):
    """获取今日推荐号码"""
    today = datetime.now()
    
    # 首先尝试从环境变量获取
    if 'RECOMMENDED_NUMBERS' in os.environ:
        try:
            data = json.loads(os.environ['RECOMMENDED_NUMBERS'])
            if data['lottery_type'] == lottery_type:
                return data['numbers'], data['analysis']
        except json.JSONDecodeError:
            print("环境变量中的推荐号码格式错误")
    
    # 如果环境变量中没有，尝试从文件读取
    month = today.strftime('%Y-%m')
    filename = f'data/recommended_numbers_{month}.json'
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                monthly_data = json.load(f)
                today_str = today.strftime('%Y-%m-%d')
                if today_str in monthly_data:
                    data = monthly_data[today_str]
                    if data['lottery_type'] == lottery_type:
                        return data['numbers'], data['analysis']
        except json.JSONDecodeError:
            print(f"读取文件 {filename} 失败")
    
    return None, None

def main():
    print("开始生成推荐号码...")
    lottery_type = get_lottery_type()
    print(f"今日开奖类型：{lottery_type}")
    
    # 检查是否已有今日推荐号码
    numbers, analysis = get_recommended_numbers(lottery_type)
    
    if numbers is None:
        # 如果没有今日推荐号码，则生成新的
        numbers, analysis = generate_numbers(lottery_type)
        # 保存推荐号码
        save_recommended_numbers(lottery_type, numbers, analysis)
    
    print(f"\n推荐号码：\n{numbers}")
    
    # 构建邮件内容
    content = f"""
    您好！

    今日{lottery_type}推荐号码：
    {numbers}

    历史数据分析（最近100期）：
    """
    
    if lottery_type == "大乐透":
        content += f"""
    前区热号（出现频率最高的号码）：{', '.join(map(str, analysis['hot_front']))}
    前区冷号（出现频率最低的号码）：{', '.join(map(str, analysis['cold_front']))}
    后区热号：{', '.join(map(str, analysis['hot_back']))}
    后区冷号：{', '.join(map(str, analysis['cold_back']))}
    """
    else:
        content += f"""
    红球热号（出现频率最高的号码）：{', '.join(map(str, analysis['hot_red']))}
    红球冷号（出现频率最低的号码）：{', '.join(map(str, analysis['cold_red']))}
    蓝球热号：{', '.join(map(str, analysis['hot_blue']))}
    蓝球冷号：{', '.join(map(str, analysis['cold_blue']))}
    """
    
    content += """
    注：推荐号码基于历史数据分析，仅供参考。
    祝您好运！
    """
    
    subject = f"今日{lottery_type}智能推荐号码"
    
    print("\n正在发送邮件...")
    send_email(subject, content)
    print("程序执行完成")

if __name__ == "__main__":
    main() 