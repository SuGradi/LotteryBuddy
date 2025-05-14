import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from lottery_recommendation import generate_numbers

def get_lottery_type():
    """判断今日开奖类型"""
    today = datetime.now().weekday()
    print(f"今天是星期{today + 1}")
    if today in [0, 2, 5]:  # 周一、三、六
        print("今天开大乐透")
        return "大乐透"
    else:
        print("今天开双色球")
        return "双色球"

def get_lottery_result(lottery_type):
    """获取开奖结果"""
    try:
        if lottery_type == "大乐透":
            url = "https://datachart.500.com/dlt/history/newinc/history.php"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        else:
            url = "https://datachart.500.com/ssq/history/newinc/history.php"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
        print(f"正在获取{lottery_type}开奖结果，URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312'  # 500彩票网使用gb2312编码
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        print("成功解析HTML")

        # 查找开奖表格
        tbody = soup.find('tbody', id='tdata')
        if tbody:
            print("找到开奖表格")
            first_tr = tbody.find('tr')
            if first_tr:
                tds = first_tr.find_all('td')
                if len(tds) >= 8:
                    # 第2到8个td（索引1到7）
                    numbers = [td.text.strip() for td in tds[1:8]]
                    print(f"找到开奖号码: {' '.join(numbers)}")
                    return numbers
                else:
                    print("td数量不足，无法提取开奖号码")
                    return None
            else:
                print("未找到第一个tr")
                return None
        else:
            print("未找到id为tdata的tbody")
            return None
                
    except requests.exceptions.Timeout:
        print("请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {str(e)}")
        return None
    except Exception as e:
        print(f"获取开奖结果失败: {str(e)}")
        return None

def check_winning(lottery_type, recommended_numbers, winning_numbers):
    """检查是否中奖"""
    if lottery_type == "大乐透":
        # 解析推荐号码
        recommended = recommended_numbers.replace("前区：", "").replace("后区：", "").split("，")
        front_recommended = [int(n.strip()) for n in recommended[0].split(",")]
        back_recommended = [int(n.strip()) for n in recommended[1].split(",")]
        
        # 解析开奖号码
        front_winning = [int(n) for n in winning_numbers[:5]]
        back_winning = [int(n) for n in winning_numbers[5:]]
        
        # 计算前区匹配数
        front_matches = len(set(front_recommended) & set(front_winning))
        # 计算后区匹配数
        back_matches = len(set(back_recommended) & set(back_winning))
        
        # 判断中奖等级
        if front_matches == 5 and back_matches == 2:
            return "恭喜您中了一等奖！"
        elif front_matches == 5 and back_matches == 1:
            return "恭喜您中了二等奖！"
        elif front_matches == 5 and back_matches == 0:
            return "恭喜您中了三等奖！"
        elif front_matches == 4 and back_matches == 2:
            return "恭喜您中了四等奖！"
        elif (front_matches == 4 and back_matches == 1) or (front_matches == 3 and back_matches == 2):
            return "恭喜您中了五等奖！"
        elif (front_matches == 4 and back_matches == 0) or (front_matches == 3 and back_matches == 1) or (front_matches == 2 and back_matches == 2):
            return "恭喜您中了六等奖！"
        else:
            return "很遗憾，您没有中奖。"
    else:
        # 解析推荐号码
        recommended = recommended_numbers.replace("红球：", "").replace("蓝球：", "").split("，")
        red_recommended = [int(n.strip()) for n in recommended[0].split(",")]
        blue_recommended = int(recommended[1].strip())
        
        # 解析开奖号码
        red_winning = [int(n) for n in winning_numbers[:6]]
        blue_winning = int(winning_numbers[6])
        
        # 计算红球匹配数
        red_matches = len(set(red_recommended) & set(red_winning))
        # 计算蓝球是否匹配
        blue_match = blue_recommended == blue_winning
        
        # 判断中奖等级
        if red_matches == 6 and blue_match:
            return "恭喜您中了一等奖！"
        elif red_matches == 6 and not blue_match:
            return "恭喜您中了二等奖！"
        elif red_matches == 5 and blue_match:
            return "恭喜您中了三等奖！"
        elif (red_matches == 5 and not blue_match) or (red_matches == 4 and blue_match):
            return "恭喜您中了四等奖！"
        elif (red_matches == 4 and not blue_match) or (red_matches == 3 and blue_match):
            return "恭喜您中了五等奖！"
        elif red_matches == 2 and blue_match or red_matches == 1 and blue_match or red_matches == 0 and blue_match:
            return "恭喜您中了六等奖！"
        else:
            return "很遗憾，您没有中奖。"

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

def main():
    print("开始执行开奖查询...")
    lottery_type = get_lottery_type()
    
    # 获取推荐号码
    recommended_numbers, analysis = generate_numbers(lottery_type)
    print(f"\n今日推荐号码：\n{recommended_numbers}")
    
    # 获取开奖结果
    winning_numbers = get_lottery_result(lottery_type)
    
    if winning_numbers:
        # 检查是否中奖
        result = check_winning(lottery_type, recommended_numbers, winning_numbers)
        
        subject = f"今日{lottery_type}开奖结果"
        content = f"""
        您好！

        今日{lottery_type}开奖结果：
        {' '.join(winning_numbers)}

        您的推荐号码：
        {recommended_numbers}

        号码对比：
        {format_number_comparison(lottery_type, recommended_numbers, winning_numbers)}

        {result}

        祝您中奖！
        """
        print(f"\n今日{lottery_type}开奖结果：")
        print(' '.join(winning_numbers))
        print(f"\n{result}")
        
        # 发送邮件
        send_email(subject, content)
    else:
        print("无法获取开奖结果")

def format_number_comparison(lottery_type, recommended_numbers, winning_numbers):
    """格式化号码对比信息"""
    if lottery_type == "大乐透":
        # 解析推荐号码
        recommended = recommended_numbers.replace("前区：", "").replace("后区：", "").split("，")
        front_recommended = [int(n.strip()) for n in recommended[0].split(",")]
        back_recommended = [int(n.strip()) for n in recommended[1].split(",")]
        
        # 解析开奖号码
        front_winning = [int(n) for n in winning_numbers[:5]]
        back_winning = [int(n) for n in winning_numbers[5:]]
        
        # 找出匹配的号码
        front_matches = set(front_recommended) & set(front_winning)
        back_matches = set(back_recommended) & set(back_winning)
        
        # 格式化输出
        front_recommended_str = " ".join([f"{n:02d}" for n in front_recommended])
        back_recommended_str = " ".join([f"{n:02d}" for n in back_recommended])
        front_winning_str = " ".join([f"{n:02d}" for n in front_winning])
        back_winning_str = " ".join([f"{n:02d}" for n in back_winning])
        
        return f"""
        前区推荐：{front_recommended_str}
        前区开奖：{front_winning_str}
        前区匹配：{' '.join([f"{n:02d}" for n in front_matches])}（{len(front_matches)}个）

        后区推荐：{back_recommended_str}
        后区开奖：{back_winning_str}
        后区匹配：{' '.join([f"{n:02d}" for n in back_matches])}（{len(back_matches)}个）
        """
    else:
        # 解析推荐号码
        recommended = recommended_numbers.replace("红球：", "").replace("蓝球：", "").split("，")
        red_recommended = [int(n.strip()) for n in recommended[0].split(",")]
        blue_recommended = int(recommended[1].strip())
        
        # 解析开奖号码
        red_winning = [int(n) for n in winning_numbers[:6]]
        blue_winning = int(winning_numbers[6])
        
        # 找出匹配的号码
        red_matches = set(red_recommended) & set(red_winning)
        blue_match = blue_recommended == blue_winning
        
        # 格式化输出
        red_recommended_str = " ".join([f"{n:02d}" for n in red_recommended])
        red_winning_str = " ".join([f"{n:02d}" for n in red_winning])
        
        return f"""
        红球推荐：{red_recommended_str}
        红球开奖：{red_winning_str}
        红球匹配：{' '.join([f"{n:02d}" for n in red_matches])}（{len(red_matches)}个）

        蓝球推荐：{blue_recommended:02d}
        蓝球开奖：{blue_winning:02d}
        蓝球匹配：{'是' if blue_match else '否'}
        """

if __name__ == "__main__":
    main() 