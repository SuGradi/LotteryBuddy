import os
import random
import smtplib
import json
import base64
import requests
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
    """保存推荐号码到GitHub仓库"""
    today = datetime.now()
    month = today.strftime('%Y-%m')
    data = {
        'date': today.strftime('%Y-%m-%d'),
        'lottery_type': lottery_type,
        'numbers': numbers,
        'analysis': analysis
    }
    
    # GitHub API配置
    github_token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'your-username')
    repo_name = os.getenv('GITHUB_REPOSITORY_NAME', 'LotteryBuddy')
    
    # 文件路径
    file_path = f'data/recommended_numbers_{month}.json'
    
    # 获取现有文件内容
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'LotteryBuddy'
    }
    
    # 首先检查token权限
    try:
        response = requests.get(
            f'https://api.github.com/user',
            headers=headers
        )
        if response.status_code != 200:
            print(f"Token权限检查失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"Token权限检查时发生错误: {str(e)}")
        return
    
    # 获取文件SHA（如果存在）
    try:
        response = requests.get(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}',
            headers=headers
        )
        if response.status_code == 200:
            existing_data = json.loads(base64.b64decode(response.json()['content']).decode('utf-8'))
            sha = response.json()['sha']
        else:
            existing_data = {}
            sha = None
    except Exception as e:
        print(f"获取现有文件失败: {str(e)}")
        existing_data = {}
        sha = None
    
    # 更新数据
    existing_data[today.strftime('%Y-%m-%d')] = data
    
    # 准备提交数据
    content = json.dumps(existing_data, ensure_ascii=False, indent=2)
    content_bytes = content.encode('utf-8')
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
    
    # 提交到GitHub
    commit_data = {
        'message': f'Update lottery numbers for {today.strftime("%Y-%m-%d")}',
        'content': content_base64,
        'branch': 'master'  # 指定分支
    }
    
    if sha:
        commit_data['sha'] = sha
    
    try:
        response = requests.put(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}',
            headers=headers,
            json=commit_data
        )
        if response.status_code in [200, 201]:
            print(f"推荐号码已保存到GitHub仓库: {file_path}")
        else:
            print(f"保存到GitHub失败: {response.status_code} - {response.text}")
            print("请确保Token具有以下权限：")
            print("1. repo 权限")
            print("2. workflow 权限")
            print("3. 仓库的写入权限")
    except Exception as e:
        print(f"保存到GitHub时发生错误: {str(e)}")

def get_recommended_numbers(lottery_type):
    """从GitHub仓库获取今日推荐号码"""
    today = datetime.now()
    month = today.strftime('%Y-%m')
    
    # GitHub API配置
    github_token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'your-username')
    repo_name = os.getenv('GITHUB_REPOSITORY_NAME', 'LotteryBuddy')
    
    # 文件路径
    file_path = f'data/recommended_numbers_{month}.json'
    
    try:
        response = requests.get(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}',
            headers={
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        
        if response.status_code == 200:
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            data = json.loads(content)
            today_str = today.strftime('%Y-%m-%d')
            
            if today_str in data and data[today_str]['lottery_type'] == lottery_type:
                return data[today_str]['numbers'], data[today_str]['analysis']
    except Exception as e:
        print(f"从GitHub获取数据失败: {str(e)}")
    
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